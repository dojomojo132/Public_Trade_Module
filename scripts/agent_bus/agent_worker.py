"""
Agent Worker — процесс агента.

Запускать на каждой агент-машине:
    python -m scripts.agent_bus.agent_worker \
        --agent-id agent-1 \
        --direction frontend \
        --bus-dir /shared/agent-bus \
        --handler my_project.handlers:execute_task

Агент:
 1. Регистрируется в шине
 2. Отправляет heartbeat каждые N сек
 3. Читает inbox — обрабатывает команды оркестратора
 4. Забирает первую доступную задачу своего направления
 5. Вызывает handler(task) → result
 6. Сообщает результат или ошибку
"""
from __future__ import annotations

import argparse
import importlib
import json
import logging
import platform
import signal
import sys
import threading
import time
import traceback
from pathlib import Path
from typing import Callable, Optional

from .bus import TaskBus
from .protocol import (
    AgentState, AgentStatus, CommandType, Task,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)


class AgentWorker:
    """
    Агент-воркер. Работает в одном потоке (один агент = один процесс).

    Параметр `task_handler`:
        Функция с сигнатурой: handler(task: Task) -> dict
        Должна вернуть словарь с результатом или бросить исключение.
        Может быть долгой (агент блокируется на ней).

    Пример handler:
        def my_handler(task: Task) -> dict:
            # task.command.description содержит инструкцию для агента
            # ... выполнить работу ...
            return {"files_changed": [...], "summary": "..."}
    """

    HEARTBEAT_INTERVAL = 15   # сек
    POLL_INTERVAL      = 5    # сек (когда нет задач)

    def __init__(
        self,
        agent_id: str,
        direction: str,
        task_handler: Callable[[Task], dict],
        bus_dir: str | Path = ".agent-bus",
        capabilities: Optional[list] = None,
    ):
        self.agent_id     = agent_id
        self.direction    = direction
        self.handler      = task_handler
        self.bus          = TaskBus(bus_dir)
        self.capabilities = capabilities or []

        self._stop         = False
        self._paused       = False
        self._current_task: Optional[Task] = None
        self._status       = AgentStatus.IDLE
        self._ctx_used     = 0.0

        self.log = logging.getLogger(f"agent.{agent_id}")

        signal.signal(signal.SIGINT,  self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    # ── Запуск ────────────────────────────────────────────────────────────────
    def run(self) -> None:
        self._register()
        heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop, daemon=True, name="heartbeat"
        )
        heartbeat_thread.start()

        self.log.info("Agent started. Direction: %s | Bus: %s",
                      self.direction, self.bus.bus_dir)

        while not self._stop:
            try:
                self._tick()
            except Exception as exc:
                self.log.error("Tick error: %s", exc, exc_info=True)
                time.sleep(self.POLL_INTERVAL)

        self.log.info("Agent stopped.")

    # ── Основной цикл ─────────────────────────────────────────────────────────
    def _tick(self) -> None:
        # 1. Читаем inbox
        commands = self.bus.read_inbox(self.agent_id)
        for cmd in commands:
            self._dispatch_command(cmd)

        # 2. Если остановлен или на паузе — ждём
        if self._stop:
            return
        if self._paused:
            time.sleep(self.POLL_INTERVAL)
            return

        # 3. Берём задачу
        task = self.bus.claim_next_task(self.agent_id, self.direction)
        if not task:
            time.sleep(self.POLL_INTERVAL)
            return

        # 4. Выполняем
        self._execute(task)

    def _execute(self, task: Task) -> None:
        self._current_task = task
        self._status       = AgentStatus.WORKING

        title = task.command.title if task.command else task.task_id
        self.log.info("Starting task %s: %s", task.task_id[:8], title)
        start = time.time()

        try:
            result = self.handler(task)
            elapsed = time.time() - start

            if not isinstance(result, dict):
                result = {"value": result}
            result["_elapsed_sec"] = round(elapsed, 1)

            self.bus.complete_task(task.task_id, self.agent_id, result)
            self.log.info("Task %s DONE in %.1f sec", task.task_id[:8], elapsed)

        except Exception as exc:
            elapsed = time.time() - start
            error_text = traceback.format_exc()
            self.bus.fail_task(task.task_id, self.agent_id, error_text)
            self.log.error("Task %s FAILED (%.1f sec): %s",
                           task.task_id[:8], elapsed, exc)
        finally:
            self._current_task = None
            self._status       = AgentStatus.IDLE

    # ── Команды оркестратора ──────────────────────────────────────────────────
    def _dispatch_command(self, cmd) -> None:
        t = cmd.type
        self.log.info("Inbox command: %s — %s", t.value, cmd.reason)

        if t == CommandType.PAUSE:
            self._paused = True
            self._status = AgentStatus.PAUSED
            self.log.info("PAUSED by orchestrator")

        elif t == CommandType.RESUME:
            self._paused = False
            self._status = AgentStatus.IDLE
            self.log.info("RESUMED by orchestrator")

        elif t == CommandType.STOP:
            self.log.info("STOP received — finishing current task, then exit")
            self._stop = True

        elif t == CommandType.CANCEL_TASK:
            if self._current_task:
                # Мягкая отмена: отмечаем флаг, handler должен на него реагировать
                self.log.warning("CANCEL requested for current task %s",
                                 self._current_task.task_id[:8])
                # TODO: если handler поддерживает cancellation token — передать
                self.bus.cancel_task(self._current_task.task_id)
                self._current_task = None
                self._status = AgentStatus.IDLE

        elif t == CommandType.CONTEXT_SYNC:
            branch = cmd.payload.get("branch", "main")
            self.log.info("CONTEXT_SYNC → branch %s (skipped: implement git sync)", branch)
            # Здесь можно вызвать git_sync.pull(branch) при необходимости

        elif t == CommandType.PRIORITY_OVERRIDE:
            task_id = cmd.payload.get("task_id")
            self.log.info("PRIORITY_OVERRIDE: task %s — claim immediately", task_id)
            # Логика: force-claim конкретной задачи независимо от очереди

    # ── Heartbeat ─────────────────────────────────────────────────────────────
    def _heartbeat_loop(self) -> None:
        while not self._stop:
            try:
                self.bus.heartbeat(
                    agent_id=self.agent_id,
                    status=self._status,
                    current_task_id=self._current_task.task_id if self._current_task else None,
                    context_window_used=self._ctx_used,
                )
            except Exception as exc:
                self.log.warning("Heartbeat failed: %s", exc)
            time.sleep(self.HEARTBEAT_INTERVAL)

    def _register(self) -> None:
        agent = AgentState(
            agent_id=self.agent_id,
            direction=self.direction,
            capabilities=self.capabilities,
            machine=platform.node(),
        )
        self.bus.register_agent(agent)
        self.log.info("Registered agent %s on machine %s", self.agent_id, agent.machine)

    def _handle_signal(self, sig, frame) -> None:
        self.log.info("Signal received — stopping...")
        self._stop = True


# ── Демо-хендлер (для тестирования без реального AI) ─────────────────────────
def demo_handler(task: Task) -> dict:
    """
    Заглушка-хендлер. Имитирует выполнение задачи.
    Замените на реальный вызов AI-агента (Copilot, Claude, GPT и т.д.).
    """
    desc = task.command.description if task.command else "(no description)"
    print(f"\n{'='*60}")
    print(f"TASK: {task.command.title if task.command else task.task_id}")
    print(f"DIRECTION: {task.direction}")
    print(f"DESCRIPTION:\n{desc}")
    print(f"{'='*60}\n")

    # Имитируем работу
    import random
    work_time = random.uniform(3, 8)
    time.sleep(work_time)

    return {
        "summary": f"Demo: completed '{task.command.title if task.command else '—'}'",
        "files_changed": [],
        "notes": "Demo handler — replace with real AI agent call",
    }


# ── CLI ───────────────────────────────────────────────────────────────────────
def _load_handler(handler_path: Optional[str]) -> Callable:
    if not handler_path:
        return demo_handler
    module_path, func_name = handler_path.rsplit(":", 1)
    module = importlib.import_module(module_path)
    return getattr(module, func_name)


def main():
    parser = argparse.ArgumentParser(description="Agent Bus Worker")
    parser.add_argument("--agent-id",   required=True,
                        help="Уникальный ID агента, напр. agent-1")
    parser.add_argument("--direction",  required=True,
                        help="Направление: frontend | backend | tests | docs | ...")
    parser.add_argument("--bus-dir",    default=".agent-bus",
                        help="Путь к шине (та же папка, что у оркестратора)")
    parser.add_argument("--handler",    default=None,
                        metavar="module:function",
                        help="Хендлер задачи, напр. myproject.agent:run_task")
    parser.add_argument("--capabilities", nargs="*", default=[],
                        help="Возможности агента: vue python jest ...")
    args = parser.parse_args()

    handler = _load_handler(args.handler)
    worker  = AgentWorker(
        agent_id=args.agent_id,
        direction=args.direction,
        task_handler=handler,
        bus_dir=args.bus_dir,
        capabilities=args.capabilities,
    )
    worker.run()


if __name__ == "__main__":
    main()
