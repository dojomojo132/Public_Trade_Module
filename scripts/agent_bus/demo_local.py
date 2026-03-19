"""
Демо: запуск полного цикла оркестратор + 2 агента в одном процессе.

Показывает полный цикл взаимодействия:
  1. Оркестратор публикует план задач с зависимостями
  2. Агенты параллельно разбирают задачи
  3. Зависимые задачи разблокируются автоматически
  4. Выводится лог назначений и завершений

Запуск:
    python scripts/agent_bus/demo_local.py
"""
from __future__ import annotations

import logging
import sys
import threading
import time
import uuid
from pathlib import Path

# Добавляем корень проекта в sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.agent_bus import (
    Orchestrator, AgentWorker,
    Task, TaskCommand, TaskType, TaskStatus,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)-18s] %(message)s",
    datefmt="%H:%M:%S",
)

BUS_DIR = Path(__file__).parent / "_demo_bus"


# ── Хендлер-заглушка (имитирует реального AI-агента) ─────────────────────────
def make_handler(agent_id: str):
    import random
    def handler(task: Task) -> dict:
        title = task.command.title if task.command else task.task_id
        work  = random.uniform(1, 4)
        print(f"\n  [{agent_id}] ▶ {title}")
        time.sleep(work)
        print(f"  [{agent_id}] ✓ {title} ({work:.1f}s)")
        return {"summary": f"Done: {title}", "files_changed": []}
    return handler


# ── Создать план задач ─────────────────────────────────────────────────────────
def build_plan():
    backend_id  = str(uuid.uuid4())
    frontend_id = str(uuid.uuid4())
    tests_id    = str(uuid.uuid4())
    docs_id     = str(uuid.uuid4())
    deploy_id   = str(uuid.uuid4())

    return [
        Task(
            task_id=backend_id,
            direction="backend",
            priority=1,
            command=TaskCommand(
                type=TaskType.IMPLEMENT,
                title="Создать API endpoint /api/analytics",
                description="Реализовать REST endpoint с агрегацией данных за период",
                acceptance_criteria=["GET /api/analytics?from=&to= работает",
                                     "Возвращает JSON с полями total, by_day"],
                estimated_minutes=5,
            ),
        ),
        Task(
            task_id=docs_id,
            direction="docs",
            priority=1,
            command=TaskCommand(
                type=TaskType.DOCUMENT,
                title="Написать документацию API /api/analytics",
                description="OpenAPI описание нового endpoint",
                estimated_minutes=3,
            ),
        ),
        Task(
            task_id=frontend_id,
            direction="frontend",
            priority=1,
            command=TaskCommand(
                type=TaskType.IMPLEMENT,
                title="Страница аналитики — компонент AnalyticsPage",
                description="Vue3 компонент, использующий /api/analytics",
                depends_on=[backend_id],   # ждёт backend
                estimated_minutes=4,
            ),
        ),
        Task(
            task_id=tests_id,
            direction="tests",
            priority=2,
            command=TaskCommand(
                type=TaskType.TEST,
                title="E2E тест страницы аналитики",
                description="Playwright тест: открыть страницу, проверить данные",
                depends_on=[frontend_id],  # ждёт frontend
                estimated_minutes=3,
            ),
        ),
        Task(
            task_id=deploy_id,
            direction="backend",
            priority=3,
            command=TaskCommand(
                type=TaskType.DEPLOY,
                title="Деплой в staging",
                description="Docker build + push staging",
                depends_on=[tests_id],     # ждёт тесты
                estimated_minutes=2,
            ),
        ),
    ]


def main():
    print("=" * 60)
    print("  AGENT BUS — DEMO LOCAL RUN")
    print("  Bus dir:", BUS_DIR)
    print("=" * 60)

    # Оркестратор
    orc = Orchestrator(bus_dir=BUS_DIR)

    # Публикуем план
    tasks = build_plan()
    ids   = orc.publish_plan(tasks)
    print(f"\nPublished {len(ids)} tasks\n")

    # Запускаем агентов в отдельных потоках
    agents_cfg = [
        ("agent-backend",  "backend",  ["python", "fastapi"]),
        ("agent-frontend", "frontend", ["vue", "typescript"]),
        ("agent-tests",    "tests",    ["playwright", "pytest"]),
        ("agent-docs",     "docs",     ["markdown", "openapi"]),
    ]

    workers = []
    threads = []
    for agent_id, direction, caps in agents_cfg:
        w = AgentWorker(
            agent_id=agent_id,
            direction=direction,
            task_handler=make_handler(agent_id),
            bus_dir=BUS_DIR,
            capabilities=caps,
        )
        workers.append(w)
        t = threading.Thread(target=w.run, name=agent_id, daemon=True)
        threads.append(t)
        t.start()

    # Даём оркестратору тикать пока не все задачи done/failed
    print("\nWaiting for all tasks to complete...\n")
    try:
        while True:
            time.sleep(orc.__class__.__dict__.get("POLL_INTERVAL", 5) if hasattr(orc, "_tick") else 3)
            orc._tick()
            snap = orc.bus.get_project_snapshot()
            t    = snap["tasks"]
            finished = t["done"] + t["failed"] + t["cancelled"]
            total    = t["total"]
            print(f"Progress: {finished}/{total} "
                  f"(done={t['done']} fail={t['failed']} "
                  f"active={t['active']} pending={t['pending']} blocked={t['blocked']})")
            if finished >= total:
                break
    except KeyboardInterrupt:
        pass

    # Финальный отчёт
    orc._print_dashboard()

    # Остановить агентов
    for w in workers:
        w._stop = True

    print("\nDemo finished. Bus files:", BUS_DIR)
    print("SQLite DB:", BUS_DIR / "bus.db")


if __name__ == "__main__":
    main()
