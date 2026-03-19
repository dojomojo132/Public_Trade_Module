"""
Bus Reader — утилита для VS Code Copilot агентов.

Агент-Copilot запускает эту утилиту, чтобы:
  1. Взять следующую задачу из шины
  2. Записать её в файл current_task.md (для контекста Copilot)
  3. Отправить heartbeat (флаг "я жив")

Запуск из терминала VS Code на каждой агент-машине:
    python scripts/agent_bus/bus_reader.py \
        --agent-id agent-frontend \
        --direction frontend \
        --bus-dir \\server\agent-bus

Вывод: current_task.md — файл с задачей для Copilot агента.
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.agent_bus.bus import TaskBus
from scripts.agent_bus.protocol import AgentState, AgentStatus, CommandType

TASK_OUTPUT_FILE = Path(".github/prompts/current_task.prompt.md")


def main():
    parser = argparse.ArgumentParser(description="Read next task from Agent Bus")
    parser.add_argument("--agent-id",   required=True)
    parser.add_argument("--direction",  required=True)
    parser.add_argument("--bus-dir",    required=True,
                        help="Полный путь к шине (общая папка или локальная)")
    parser.add_argument("--out",        default=str(TASK_OUTPUT_FILE),
                        help="Файл для записи задачи (для Copilot)")
    parser.add_argument("--heartbeat-only", action="store_true",
                        help="Только heartbeat, не брать задачу")
    args = parser.parse_args()

    bus = TaskBus(bus_dir=args.bus_dir)

    # Регистрируем агента (идемпотентно)
    agent = AgentState(
        agent_id=args.agent_id,
        direction=args.direction,
        machine=platform.node(),
    )
    bus.register_agent(agent)

    # Читаем inbox — есть ли команды от оркестратора?
    commands = bus.read_inbox(args.agent_id)
    for cmd in commands:
        print(f"[INBOX] {cmd.type.value}: {cmd.reason}")
        if cmd.type == CommandType.STOP:
            print("Получена команда STOP. Выходим.")
            sys.exit(0)
        if cmd.type == CommandType.PAUSE:
            print("Получена команда PAUSE. Агент приостановлен.")
            bus.heartbeat(args.agent_id, AgentStatus.PAUSED)
            sys.exit(2)  # exit code 2 = paused

    if args.heartbeat_only:
        bus.heartbeat(args.agent_id, AgentStatus.IDLE)
        print(f"Heartbeat sent. Agent: {args.agent_id}")
        sys.exit(0)

    # Берём задачу
    task = bus.claim_next_task(agent_id=args.agent_id, direction=args.direction)

    if not task:
        bus.heartbeat(args.agent_id, AgentStatus.IDLE)
        print(f"Нет задач для направления '{args.direction}'. Ожидайте.")

        # Выводим статус шины
        snap = bus.get_project_snapshot()
        t = snap["tasks"]
        print(f"\nСтатус шины:")
        print(f"  pending={t['pending']}  active={t['active']}  "
              f"done={t['done']}  blocked={t['blocked']}  failed={t['failed']}")
        sys.exit(1)  # exit code 1 = no task

    # Обновим heartbeat
    bus.heartbeat(args.agent_id, AgentStatus.WORKING, task.task_id)

    # Сформируем prompt-файл для Copilot
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_content = _build_prompt(task.to_dict(), args.agent_id)
    out_path.write_text(prompt_content, encoding="utf-8")

    # Параллельно — сохраним task_id в .current_task_id для bus_report.py
    state_file = Path(".agent-bus-state.json")
    state_file.write_text(json.dumps({
        "agent_id": args.agent_id,
        "direction": args.direction,
        "task_id": task.task_id,
        "bus_dir": str(args.bus_dir),
        "claimed_at": datetime.utcnow().isoformat() + "Z",
    }), encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"  ЗАДАЧА ПОЛУЧЕНА")
    print(f"  Task ID:    {task.task_id}")
    print(f"  Заголовок:  {task.command.title if task.command else '—'}")
    print(f"  Направление:{task.direction}")
    print(f"{'='*60}")
    print(f"\nФайл задачи сохранён: {out_path}")
    print(f"Откройте этот файл в VS Code и запустите через Copilot Agent Mode.")
    print(f"\nПосле выполнения задачи запустите:")
    print(f"  python scripts/agent_bus/bus_report.py --success")
    print(f"  python scripts/agent_bus/bus_report.py --failed 'описание ошибки'")


def _build_prompt(task: dict, agent_id: str) -> str:
    cmd = task.get("command", {})
    criteria = cmd.get("acceptance_criteria", [])
    files    = cmd.get("files_scope", [])
    constraints = cmd.get("constraints", [])

    criteria_str    = "\n".join(f"- {c}" for c in criteria) if criteria else "— не указаны"
    files_str       = "\n".join(f"- `{f}`" for f in files)  if files    else "— не ограничен"
    constraints_str = "\n".join(f"- {c}" for c in constraints) if constraints else "— нет"
    depends_str     = ", ".join(cmd.get("depends_on", [])) or "нет"
    blocks_str      = ", ".join(cmd.get("blocks", []))     or "нет"

    return f"""---
mode: agent
description: "Agent Bus Task: {cmd.get('title', task['task_id'])}"
---

# Задача агента — {cmd.get('title', task['task_id'])}

> **Agent ID:** `{agent_id}` | **Task ID:** `{task['task_id']}`  
> **Направление:** `{task.get('direction', '—')}` | **Приоритет:** {task.get('priority', 3)}

## Описание

{cmd.get('description', '— описание не задано')}

## Критерии приёмки

{criteria_str}

## Файлы в области изменений

{files_str}

## Ограничения

{constraints_str}

## Зависимости

- **Зависит от:** {depends_str}
- **Блокирует:** {blocks_str}

---

## Инструкция для агента

1. Прочитай описание задачи и критерии приёмки выше.
2. Изучи файлы в области изменений (если указаны).
3. Реализуй задачу — напиши код, внеси изменения в файлы.
4. Убедись что все критерии приёмки выполнены.
5. **После завершения** запусти в терминале:
   ```
   python scripts/agent_bus/bus_report.py --success --summary "краткое описание что сделано"
   ```
6. **При ошибке** запусти:
   ```
   python scripts/agent_bus/bus_report.py --failed "описание проблемы"
   ```

> Не завершай работу без явного `bus_report.py` — оркестратор не узнает о результате.
"""


if __name__ == "__main__":
    main()
