"""
Bus Monitor — живой мониторинг состояния агентов и задач.

Запуск:
    python scripts/agent_bus/bus_monitor.py --bus-dir \\server\agent-bus

Обновляет терминал каждые N секунд. Показывает:
  - Статусы всех агентов (online/offline/working/paused)
  - Очередь задач (pending/active/blocked/done/failed)
  - Предупреждения (offline агенты, зависшие задачи)
  - Лог последних событий
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.agent_bus.bus import OFFLINE_TIMEOUT, STUCK_MULTIPLIER, TaskBus
from scripts.agent_bus.protocol import AgentStatus

# ── ANSI цвета ────────────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
CYAN   = "\033[96m"
GRAY   = "\033[90m"
WHITE  = "\033[97m"

AGENT_STATUS_COLORS = {
    "idle":    GREEN,
    "working": CYAN,
    "paused":  YELLOW,
    "stopped": GRAY,
    "error":   RED,
    "offline": RED + BOLD,
}

TASK_STATUS_COLORS = {
    "pending":   WHITE,
    "active":    CYAN,
    "done":      GREEN,
    "failed":    RED,
    "blocked":   YELLOW,
    "cancelled": GRAY,
}


def _color(text: str, color: str) -> str:
    return f"{color}{text}{RESET}"


def _age_str(iso_ts: str) -> str:
    """Вернуть удобочитаемое время с момента ts."""
    try:
        dt = datetime.fromisoformat(iso_ts.rstrip("Z"))
        delta = datetime.utcnow() - dt
        secs = int(delta.total_seconds())
        if secs < 60:
            return f"{secs}s"
        if secs < 3600:
            return f"{secs//60}m{secs%60:02d}s"
        return f"{secs//3600}h{secs%3600//60}m"
    except Exception:
        return "?"


def _is_offline(last_heartbeat: str) -> bool:
    try:
        dt  = datetime.fromisoformat(last_heartbeat.rstrip("Z"))
        return datetime.utcnow() - dt > timedelta(seconds=OFFLINE_TIMEOUT)
    except Exception:
        return True


def _is_stuck(updated_at: str, estimated_minutes: int) -> bool:
    try:
        dt    = datetime.fromisoformat(updated_at.rstrip("Z"))
        limit = timedelta(minutes=estimated_minutes * STUCK_MULTIPLIER)
        return datetime.utcnow() - dt > limit
    except Exception:
        return False


def render(bus: TaskBus, log_lines: list[str], refresh_interval: int) -> None:
    """Отрисовать монитор в терминале."""
    os.system("cls" if os.name == "nt" else "clear")

    snap  = bus.get_project_snapshot()
    t     = snap["tasks"]
    now   = datetime.utcnow().strftime("%H:%M:%S")
    width = os.get_terminal_size().columns if sys.stdout.isatty() else 80

    warnings: list[str] = []

    # ── Заголовок ──────────────────────────────────────────────────────────────
    print(_color(f"  AGENT BUS MONITOR  {now}  [refresh: {refresh_interval}s]", BOLD + WHITE))
    print("─" * width)

    # ── Агенты ─────────────────────────────────────────────────────────────────
    print(_color("  AGENTS", BOLD + BLUE))
    agents = bus.get_all_agents()
    if not agents:
        print(_color("    (нет зарегистрированных агентов)", GRAY))
    for a in agents:
        offline = _is_offline(a.last_heartbeat)
        status  = "offline" if offline else a.status.value
        color   = AGENT_STATUS_COLORS.get(status, WHITE)

        task_info = ""
        if a.current_task_id:
            task_info = f"  task={a.current_task_id[:8]}..."

        ctx_bar = ""
        if a.context_window_used > 0:
            pct = int(a.context_window_used * 10)
            ctx_bar = f"  ctx=[{'█'*pct}{'░'*(10-pct)}] {a.context_window_used*100:.0f}%"
            if a.context_window_used > 0.8:
                warnings.append(f"Agent {a.agent_id}: context window >80% full!")

        hb_age = _age_str(a.last_heartbeat)
        done_f = f"done={a.completed_tasks} fail={a.failed_tasks}"

        line = (f"    [{_color(f'{status:8}', color)}]"
                f"  {a.agent_id:20}"
                f"  dir={a.direction:12}"
                f"  hb={hb_age:8}"
                f"  {done_f}"
                f"{task_info}{ctx_bar}")
        print(line)

        if offline and a.current_task_id:
            warnings.append(f"OFFLINE: {a.agent_id} — task {a.current_task_id[:8]} будет возвращена в очередь")

    # ── Задачи ─────────────────────────────────────────────────────────────────
    print()
    print(_color("  TASKS SUMMARY", BOLD + BLUE))
    total    = t["total"]
    progress = (t["done"] / total * 100) if total else 0
    bar_len  = 30
    filled   = int(progress / 100 * bar_len)
    bar      = "█" * filled + "░" * (bar_len - filled)
    print(f"    [{bar}] {progress:.0f}%  "
          f"done={_color(str(t['done']), GREEN)} "
          f"active={_color(str(t['active']), CYAN)} "
          f"pending={t['pending']} "
          f"blocked={_color(str(t['blocked']), YELLOW)} "
          f"failed={_color(str(t['failed']), RED if t['failed'] else WHITE)} "
          f"total={total}")

    # ── Активные и pending задачи ──────────────────────────────────────────────
    active_tasks = [r for r in snap["task_list"] if r["status"] in ("active", "pending")]
    if active_tasks:
        print()
        print(_color("  ACTIVE / PENDING", BOLD + BLUE))
        for task_row in active_tasks[:15]:
            status   = task_row["status"]
            color    = TASK_STATUS_COLORS.get(status, WHITE)
            age      = _age_str(task_row.get("updated_at", ""))
            agent    = task_row.get("assigned_to") or "—"
            estimated= task_row.get("estimated_minutes", 30)
            retry    = task_row.get("retry_count", 0)
            retry_str= f" retry={retry}" if retry else ""

            payload  = {}
            try:
                payload = json.loads(task_row.get("payload", "{}"))
            except Exception:
                pass
            title = (payload.get("command") or {}).get("title") or task_row["task_id"][:16]

            stuck_warn = ""
            if status == "active" and _is_stuck(task_row.get("updated_at", ""), estimated):
                stuck_warn = _color("  ⚠ STUCK", RED + BOLD)
                warnings.append(f"STUCK: task {task_row['task_id'][:8]} ({title[:30]}) — превышено {estimated*STUCK_MULTIPLIER:.0f}m")

            line = (f"    [{_color(status, color):16}]"
                    f"  {task_row['task_id'][:8]}"
                    f"  {task_row['direction']:12}"
                    f"  {age:8}"
                    f"  {agent:20}"
                    f"  {title[:35]}"
                    f"{retry_str}{stuck_warn}")
            print(line)

    # ── Предупреждения ─────────────────────────────────────────────────────────
    if warnings:
        print()
        print(_color("  ⚠ WARNINGS", BOLD + RED))
        for w in warnings:
            print(_color(f"    {w}", YELLOW))

    # ── Последние ошибки ───────────────────────────────────────────────────────
    failed_tasks = [r for r in snap["task_list"] if r["status"] == "failed"]
    if failed_tasks:
        print()
        print(_color("  FAILED TASKS", BOLD + RED))
        for task_row in failed_tasks[-5:]:
            payload = {}
            try:
                payload = json.loads(task_row.get("payload", "{}"))
            except Exception:
                pass
            title = (payload.get("command") or {}).get("title") or task_row["task_id"][:16]
            age   = _age_str(task_row.get("updated_at", ""))
            print(_color(f"    ✗ {task_row['task_id'][:8]}  {task_row['direction']:12}  {age}  {title[:40]}", RED))

    # ── Лог событий ───────────────────────────────────────────────────────────
    print()
    print(_color("  EVENT LOG (last 10)", BOLD + BLUE))
    for line in log_lines[-10:]:
        print(f"    {_color(line, GRAY)}")

    print("─" * width)
    print(f"  {_color('q', BOLD)}=quit  {_color('r', BOLD)}=refresh  Bus: {bus.bus_dir}")


def main():
    parser = argparse.ArgumentParser(description="Agent Bus Live Monitor")
    parser.add_argument("--bus-dir",  required=True,
                        help="Путь к шине (та же папка, что у оркестратора)")
    parser.add_argument("--interval", default=5, type=int,
                        help="Интервал обновления в секундах")
    parser.add_argument("--once",     action="store_true",
                        help="Вывести один раз и выйти")
    args = parser.parse_args()

    bus = TaskBus(bus_dir=args.bus_dir)
    log_lines: list[str] = []

    # Слушаем изменения в results/ — добавляем в лог
    results_dir  = bus.bus_dir / "results"
    seen_results: set = set()

    def _scan_events():
        for f in results_dir.glob("*.json"):
            if f.name not in seen_results:
                seen_results.add(f.name)
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    task_id = data.get("task_id", "?")[:8]
                    agent   = data.get("agent_id", "?")
                    ok      = "✓ done" if data.get("success") else "✗ failed"
                    ts      = data.get("finished_at", "")[:19]
                    log_lines.append(f"{ts}  {ok}  task={task_id}  agent={agent}")
                except Exception:
                    pass

    if args.once:
        _scan_events()
        render(bus, log_lines, args.interval)
        return

    try:
        while True:
            _scan_events()
            render(bus, log_lines, args.interval)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nMonitor stopped.")


if __name__ == "__main__":
    main()
