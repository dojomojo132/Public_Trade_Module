"""
Orchestrator Loop — главный цикл оркестратора.

Запускать на машине оркестратора:
    python -m scripts.agent_bus.orchestrator_loop --bus-dir /shared/agent-bus

Оркестратор:
 1. Назначает задачи idle-агентам с учётом направления и capabilities
 2. Обнаруживает упавших агентов и возвращает их задачи в очередь
 3. Обнаруживает зависшие задачи и отменяет их (или пересоздаёт)
 4. Разблокирует задачи при завершении зависимостей (автоматически в bus.py)
 5. Выводит live-дашборд состояния
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import signal
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from .bus import TaskBus
from .protocol import (
    AgentState, AgentStatus, CommandType, OrchestratorCommand,
    Task, TaskCommand, TaskStatus, TaskType,
)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [ORCHESTRATOR] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("orchestrator")

POLL_INTERVAL    = 5     # сек между итерациями
DASHBOARD_EVERY  = 10    # сек между дашбордом
ALERT_LOG_FILE   = ".agent-bus-alerts.jsonl"  # лог предупреждений (для мониторинга)


class Orchestrator:
    """
    Основной класс оркестратора.

    Пример создания задач и запуска:
        orc = Orchestrator(bus_dir=".agent-bus")
        orc.publish_plan([
            Task(direction="backend",  priority=1, command=TaskCommand(...)),
            Task(direction="frontend", priority=1, command=TaskCommand(..., depends_on=[backend_task_id])),
        ])
        orc.run()
    """

    def __init__(self, bus_dir: str | Path = ".agent-bus"):
        self.bus   = TaskBus(bus_dir)
        self._stop = False
        self._last_dashboard = 0.0
        self._offline_warn_count: Dict[str, int] = {}  # agent_id → кол-во предупреждений

        signal.signal(signal.SIGINT,  self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    # ── Публичный API ─────────────────────────────────────────────────────────
    def publish_plan(self, tasks: List[Task]) -> List[str]:
        """
        Опубликовать список задач (план спринта).
        Порядок depends_on разрешается автоматически.
        """
        ids = []
        for task in tasks:
            tid = self.bus.publish_task(task)
            ids.append(tid)
            log.info("Plan: published task %s [%s] '%s'",
                     tid[:8], task.direction,
                     task.command.title if task.command else "—")
        return ids

    def send_pause(self, agent_id: str, reason: str = "") -> None:
        self.bus.send_command(agent_id, OrchestratorCommand(
            type=CommandType.PAUSE, reason=reason,
        ))

    def send_resume(self, agent_id: str) -> None:
        self.bus.send_command(agent_id, OrchestratorCommand(
            type=CommandType.RESUME,
        ))

    def send_stop(self, agent_id: str, reason: str = "") -> None:
        self.bus.send_command(agent_id, OrchestratorCommand(
            type=CommandType.STOP, reason=reason,
        ))

    def send_context_sync(self, agent_id: str, branch: str = "main") -> None:
        self.bus.send_command(agent_id, OrchestratorCommand(
            type=CommandType.CONTEXT_SYNC,
            payload={"branch": branch},
        ))

    # ── Главный цикл ──────────────────────────────────────────────────────────
    def run(self) -> None:
        log.info("Orchestrator started. Bus: %s", self.bus.bus_dir)
        while not self._stop:
            try:
                self._tick()
            except Exception as exc:
                log.error("Tick error: %s", exc, exc_info=True)
            time.sleep(POLL_INTERVAL)
        log.info("Orchestrator stopped.")

    def _tick(self) -> None:
        agents = self.bus.get_all_agents()
        agent_map: Dict[str, AgentState] = {a.agent_id: a for a in agents}

        # 1. Проверить offline агентов
        offline = self.bus.get_offline_agents()
        for agent in offline:
            self._handle_offline(agent)

        # 2. Проверить зависшие задачи
        stuck = self.bus.get_stuck_tasks()
        for task_row in stuck:
            self._handle_stuck(task_row, agent_map)

        # 3. Агенты сами клеймят задачи через polling (claim_next_task).
        #    Оркестратор отвечает только за публикацию, разблокировку
        #    зависимостей (автоматически в bus.py) и управление сбоями.

        # 4. Дашборд
        now = time.time()
        if now - self._last_dashboard >= DASHBOARD_EVERY:
            self._print_dashboard()
            self._last_dashboard = now

    def _handle_offline(self, agent: AgentState) -> None:
        """Агент не отвечает — вернуть его задачу в очередь + эскалация."""
        agent_id = agent.agent_id
        self._offline_warn_count[agent_id] = self._offline_warn_count.get(agent_id, 0) + 1
        count = self._offline_warn_count[agent_id]

        if agent.current_task_id:
            log.warning("Agent %s OFFLINE (warn #%d) — resetting task %s",
                        agent_id, count, agent.current_task_id)
            self.bus.reset_task_to_pending(agent.current_task_id)

        # Эскалация: записать в лог предупреждений
        self._write_alert(
            level="WARNING" if count < 5 else "ERROR",
            message=f"Agent {agent_id} OFFLINE (consecutive: {count})",
            data={
                "agent_id": agent_id,
                "last_heartbeat": agent.last_heartbeat,
                "current_task_id": agent.current_task_id,
                "offline_count": count,
            },
        )
    
    def _write_alert(self, level: str, message: str, data: dict = None) -> None:
        """Записать предупреждение в JSONL лог-файл."""
        alert = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": level,
            "message": message,
            "data": data or {},
        }
        alert_file = self.bus.bus_dir / ALERT_LOG_FILE
        try:
            with open(alert_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(alert, ensure_ascii=False) + "\n")
        except Exception as e:
            log.warning("Failed to write alert: %s", e)

    def _handle_stuck(self, task_row: dict, agent_map: Dict[str, AgentState]) -> None:
        """Задача висит слишком долго — вернуть в pending (агент подхватит снова)."""
        task_id  = task_row["task_id"]
        agent_id = task_row.get("assigned_to")
        log.warning("Task %s STUCK (agent %s) — resetting to pending",
                    task_id, agent_id)
        if agent_id and agent_id in agent_map:
            self.bus.send_command(agent_id, OrchestratorCommand(
                type=CommandType.CANCEL_TASK,
                reason=f"Task {task_id} exceeded estimated time",
            ))
        self.bus.reset_task_to_pending(task_id)

    def _print_dashboard(self) -> None:
        snap = self.bus.get_project_snapshot()
        t    = snap["tasks"]
        print(f"\n{'─'*60}")
        print(f"  ORCHESTRATOR DASHBOARD  {snap['timestamp'][:19]}")
        print(f"{'─'*60}")
        print(f"  Tasks:  pending={t['pending']}  active={t['active']}  "
              f"done={t['done']}  failed={t['failed']}  blocked={t['blocked']}")
        print(f"  Agents:")
        for aid, info in snap["agents"].items():
            task_str = f"task={info['current_task_id'][:8]}..." if info['current_task_id'] else "—"
            print(f"    [{info['status']:8}] {aid:20} dir={info['direction']:12} "
                  f"{task_str}  done={info['completed']} fail={info['failed']}")
        print(f"{'─'*60}\n")

    def _handle_signal(self, sig, frame) -> None:
        log.info("Signal %s received — stopping after current tick...", sig)
        self._stop = True


# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Agent Bus Orchestrator")
    parser.add_argument("--bus-dir", default=".agent-bus",
                        help="Путь к шине (общая папка или локальная)")
    parser.add_argument("--load-plan", metavar="FILE",
                        help="JSON-файл с планом задач для загрузки при старте")
    args = parser.parse_args()

    orc = Orchestrator(bus_dir=args.bus_dir)

    if args.load_plan:
        plan_path = Path(args.load_plan)
        if not plan_path.exists():
            print(f"Error: plan file not found: {plan_path}", file=sys.stderr)
            sys.exit(1)
        tasks_data = json.loads(plan_path.read_text(encoding="utf-8"))
        tasks = [Task.from_dict(t) for t in tasks_data]
        orc.publish_plan(tasks)

    orc.run()


if __name__ == "__main__":
    main()
