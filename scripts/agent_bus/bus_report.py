"""
Bus Report — агент сообщает результат выполнения задачи.

Запускается агентом-Copilot ПОСЛЕ выполнения задачи:

  # Успех:
  python scripts/agent_bus/bus_report.py --success --summary "Реализован endpoint"

  # Ошибка:
  python scripts/agent_bus/bus_report.py --failed "Не удалось запустить тесты: ..."

Читает .agent-bus-state.json (записал bus_reader.py) и сообщает результат в шину.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.agent_bus.bus import TaskBus
from scripts.agent_bus.protocol import AgentStatus

STATE_FILE = Path(".agent-bus-state.json")


def main():
    parser = argparse.ArgumentParser(description="Report task result to Agent Bus")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--success", action="store_true",
                       help="Задача выполнена успешно")
    group.add_argument("--failed",  metavar="ERROR",
                       help="Задача провалена (описание ошибки)")
    parser.add_argument("--summary",  default="",
                        help="Краткое описание что сделано (при --success)")
    parser.add_argument("--files",    nargs="*", default=[],
                        help="Список изменённых файлов")
    parser.add_argument("--no-git",   action="store_true",
                        help="Не делать git add/commit")
    args = parser.parse_args()

    # Читаем state
    if not STATE_FILE.exists():
        print(f"Error: файл состояния не найден: {STATE_FILE}")
        print("Сначала запустите bus_reader.py для получения задачи.")
        sys.exit(1)

    state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    agent_id  = state["agent_id"]
    task_id   = state["task_id"]
    bus_dir   = state["bus_dir"]
    direction = state["direction"]

    bus = TaskBus(bus_dir=bus_dir)

    if args.success:
        # Git commit изменений (опционально)
        commit_result = {}
        if not args.no_git:
            commit_result = _git_commit(task_id, args.summary or "Task completed", args.files)

        result = {
            "summary":       args.summary,
            "files_changed": args.files or commit_result.get("files_changed", []),
            "git_commit":    commit_result.get("commit_hash", ""),
            "agent_id":      agent_id,
            "finished_at":   datetime.utcnow().isoformat() + "Z",
        }
        bus.complete_task(task_id, agent_id, result)
        bus.heartbeat(agent_id, AgentStatus.IDLE)

        print(f"\n{'='*60}")
        print(f"  ЗАДАЧА ЗАВЕРШЕНА ✓")
        print(f"  Task ID: {task_id}")
        if args.summary:
            print(f"  Итог:    {args.summary}")
        if commit_result.get("commit_hash"):
            print(f"  Commit:  {commit_result['commit_hash']}")
        print(f"{'='*60}")
        print(f"\nЗапустите bus_reader.py для получения следующей задачи.")

    else:
        error_text = args.failed
        bus.fail_task(task_id, agent_id, error_text)
        bus.heartbeat(agent_id, AgentStatus.IDLE)

        print(f"\n{'='*60}")
        print(f"  ЗАДАЧА ПРОВАЛЕНА ✗")
        print(f"  Task ID: {task_id}")
        print(f"  Ошибка:  {error_text}")
        print(f"{'='*60}")
        print(f"\nОркестратор получит сигнал об ошибке и примет решение.")

    # Удаляем state файл
    STATE_FILE.unlink(missing_ok=True)


def _git_commit(task_id: str, summary: str, files: list) -> dict:
    """Сделать git add + commit для изменённых файлов."""
    try:
        if files:
            subprocess.run(["git", "add"] + files, check=True, capture_output=True)
        else:
            subprocess.run(["git", "add", "-A"], check=True, capture_output=True)

        commit_msg = f"[agent-bus] {summary} [{task_id[:8]}]"
        result = subprocess.run(
            ["git", "commit", "-m", commit_msg],
            check=True, capture_output=True, text=True,
        )

        # Получить hash коммита
        hash_result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True,
        )
        commit_hash = hash_result.stdout.strip()

        # Узнать изменённые файлы
        diff_result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
            capture_output=True, text=True,
        )
        changed = diff_result.stdout.strip().splitlines()

        return {"commit_hash": commit_hash, "files_changed": changed}

    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode() if isinstance(e.stderr, bytes) else str(e.stderr)
        if "nothing to commit" in stderr or "nothing added" in stderr:
            return {"commit_hash": "", "files_changed": []}
        print(f"Warning: git commit failed: {stderr}")
        return {"commit_hash": "", "files_changed": []}


if __name__ == "__main__":
    main()
