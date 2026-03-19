# Agent Bus — Групповая агентная параллельная разработка

Система координации нескольких AI-агентов (GitHub Copilot, Claude, GPT и др.)
для параллельной разработки проекта. Агенты могут находиться на разных ПК.

---

## Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR                             │
│  orchestrator_loop.py — главный цикл                       │
│  • Публикует план задач (граф зависимостей)               │
│  • Назначает задачи idle-агентам                           │
│  • Обнаруживает упавших агентов → возвращает задачи       │
│  • Обнаруживает зависшие задачи → переназначает            │
│  • Отправляет команды: pause/resume/stop/cancel            │
└────────────────────────┬────────────────────────────────────┘
                         │
                    bus.py (SQLite)           ← ЕДИНСТВЕННЫЙ ИСТОЧНИК ИСТИНЫ
                         │
         ┌───────────────┼───────────────┐
    ┌────▼────┐    ┌─────▼────┐    ┌────▼────┐
    │ Agent 1 │    │ Agent 2  │    │ Agent 3 │ ...
    │frontend │    │ backend  │    │  tests  │
    └─────────┘    └──────────┘    └─────────┘
```

## Уровни развёртывания

| Уровень | Транспорт | Когда использовать |
|---------|-----------|-------------------|
| **1. Локально** | SQLite на общем диске (SMB/NFS) | Агенты в одной сети |
| **2. Интернет** | REST API (api_server.py + Tailscale) | Агенты на разных ПК |
| **3. Git Bus** | git add/commit/push каждые N сек | Без общей сети, медленнее |

---

## Быстрый старт

### 1. Локальное демо (всё на одном ПК)

```bash
python scripts/agent_bus/demo_local.py
```

Увидите:
- 4 агента разбирают задачи параллельно
- frontend ждёт завершения backend (зависимость)
- tests ждут frontend
- live-дашборд статуса

### 2. Несколько ПК в одной сети

**Общая папка**: `\\server\agent-bus\` (Windows) или `/mnt/agent-bus/` (Linux)

**ПК-Оркестратор:**
```bash
python -m scripts.agent_bus.orchestrator_loop \
    --bus-dir "\\\\server\\agent-bus" \
    --load-plan my_sprint_plan.json
```

**ПК-Агент (frontend):**
```bash
python -m scripts.agent_bus.agent_worker \
    --agent-id agent-frontend \
    --direction frontend \
    --bus-dir "\\\\server\\agent-bus" \
    --handler myproject.handlers:copilot_handler \
    --capabilities vue typescript jest
```

**ПК-Агент (backend):**
```bash
python -m scripts.agent_bus.agent_worker \
    --agent-id agent-backend \
    --direction backend \
    --bus-dir "\\\\server\\agent-bus" \
    --handler myproject.handlers:copilot_handler
```

### 3. Кросс-интернет (разные сети)

**ПК-Оркестратор (сервер шины):**
```bash
# Установить зависимости: pip install fastapi uvicorn
python -m scripts.agent_bus.api_server \
    --bus-dir .agent-bus \
    --port 8765 \
    --api-key mysecretkey

# Пробросить через Tailscale или ngrok:
# tailscale up → магический IP
# ngrok http 8765 → публичный URL
```

**ПК-Агент (другая сеть):**
```python
# Вместо TaskBus используется BusHttpClient
from scripts.agent_bus.api_server import BusHttpClient
from scripts.agent_bus.agent_worker import AgentWorker

# Патчим AgentWorker для HTTP-транспорта
# (или создаём свой worker с BusHttpClient.claim_next_task)
bus = BusHttpClient(
    base_url="http://100.64.1.100:8765",  # Tailscale IP
    api_key="mysecretkey"
)
```

---

## Формат плана задач (JSON)

```json
[
  {
    "task_id": "uuid-backend-1",
    "direction": "backend",
    "priority": 1,
    "command": {
      "type": "implement",
      "title": "Создать API /api/orders",
      "description": "Полное описание для агента...",
      "acceptance_criteria": ["GET /api/orders возвращает 200", "Есть пагинация"],
      "files_scope": ["src/api/orders.py", "tests/test_orders.py"],
      "depends_on": [],
      "blocks": ["uuid-frontend-1"],
      "estimated_minutes": 20
    }
  },
  {
    "task_id": "uuid-frontend-1",
    "direction": "frontend",
    "priority": 1,
    "command": {
      "type": "implement",
      "title": "Страница заказов",
      "description": "Vue3 компонент OrdersPage...",
      "depends_on": ["uuid-backend-1"],
      "estimated_minutes": 15
    }
  }
]
```

---

## Написать свой handler

Handler — это функция, которую агент вызывает для каждой задачи.
Именно здесь интегрируется реальный AI (Copilot, Claude, GPT etc).

```python
# myproject/handlers.py
from scripts.agent_bus import Task

def copilot_handler(task: Task) -> dict:
    """
    Вызывается AgentWorker для каждой задачи.
    task.command.description содержит инструкцию.
    Верните словарь с результатом или бросьте исключение.
    """
    # Здесь: вызов VS Code Copilot API, subprocess, HTTP к AI, и т.д.
    print(f"Working on: {task.command.title}")
    print(f"Description: {task.command.description}")
    print(f"Files scope: {task.command.files_scope}")

    # ... ваша логика ...

    return {
        "summary": "Реализован endpoint /api/orders",
        "files_changed": ["src/api/orders.py"],
        "tests_passed": True,
    }
```

Указать handler при запуске:
```bash
python -m scripts.agent_bus.agent_worker \
    --handler myproject.handlers:copilot_handler \
    --agent-id agent-1 --direction backend --bus-dir .agent-bus
```

---

## Команды оркестратора (управление агентами)

```python
from scripts.agent_bus import Orchestrator

orc = Orchestrator(bus_dir=".agent-bus")

orc.send_pause("agent-1", reason="Ждём review")   # Приостановить
orc.send_resume("agent-1")                          # Возобновить
orc.send_stop("agent-1", reason="Спринт завершён") # Остановить
orc.send_context_sync("agent-1", branch="main")    # Синхронизировать контекст
```

---

## Файловая структура шины

```
.agent-bus/
├── bus.db          ← SQLite: задачи, статусы, inbox (ГЛАВНЫЙ ФАЙЛ)
├── tasks/          ← JSON-контексты задач (для агентов, read-only)
│   ├── <uuid>.json
│   └── ...
└── results/        ← JSON-результаты от агентов (для оркестратора)
    ├── <uuid>.json
    └── ...
```

---

## Структура файлов кода

```
scripts/agent_bus/
├── __init__.py          ← публичный API пакета
├── protocol.py          ← dataclasses: Task, AgentState, Command
├── bus.py               ← TaskBus: SQLite ядро (атомарные операции)
├── orchestrator_loop.py ← Orchestrator: главный цикл управления
├── agent_worker.py      ← AgentWorker: процесс агента + heartbeat
├── api_server.py        ← FastAPI REST шина (кросс-интернет)
├── demo_local.py        ← демо: 4 агента в одном процессе
└── README.md            ← этот файл
```
