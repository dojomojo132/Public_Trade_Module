"""
session.py — Менеджер сессии отладки с фоновым потоком опроса (polling).

Координирует:
  - Launcher (управление процессами dbgs.exe / 1cv8c.exe)
  - RdbgClient (HTTP/XML команды отладчику)
  - MetadataMapper (BSL-путь → UUID)
  - Polling thread (периодическая проверка статуса breakpoint-событий)
"""

import json
import logging
import threading
import time
from pathlib import Path
from typing import Any, Optional

from .launcher import Launcher, LaunchError
from .metadata_mapper import MetadataMapper
from .rdbg_client import RdbgClient, RdbgError

logger = logging.getLogger(__name__)


class SessionState:
    IDLE = "idle"
    CONNECTING = "connecting"
    ATTACHED = "attached"
    STOPPED = "stopped"        # остановлен на breakpoint
    RUNNING = "running"        # выполнение продолжено
    DISCONNECTING = "disconnecting"
    ERROR = "error"


class DebugSession:
    """
    Высокоуровневый менеджер сессии отладки ptm-debug.

    Создаётся один экземпляр на время работы MCP-сервера.
    Поток polling (опроса) проверяет, не сработал ли breakpoint,
    и обновляет внутреннее состояние.

    Параметры
    ----------
    config : dict
        Словарь конфигурации из debug_config.json.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        platform_root = config["platform"]["root"]
        ib_cfg = config["infoBase"]
        dbg_cfg = config["debug"]
        ws_cfg = config["workspace"]

        self._port: int = self._find_free_port(
            dbg_cfg.get("portRange", [1550, 1560])
        )

        self.launcher = Launcher(
            platform_root=platform_root,
            ib_path=ib_cfg["path"],
            ib_user=ib_cfg.get("user", "Admin"),
            ib_password=ib_cfg.get("password", ""),
            debug_host=dbg_cfg.get("host", "localhost"),
            debug_port=self._port,
        )
        self.rdbg = RdbgClient(
            host=dbg_cfg.get("host", "localhost"),
            port=self._port,
            timeout=dbg_cfg.get("attachTimeout", 10),
        )
        self.mapper = MetadataMapper(config_root=ws_cfg["configRoot"])

        self._poll_interval: float = dbg_cfg.get("pollInterval", 0.5)
        self._state: str = SessionState.IDLE
        self._last_error: str = ""
        self._stop_event = threading.Event()
        self._poll_thread: Optional[threading.Thread] = None
        self._state_lock = threading.Lock()

    # ------------------------------------------------------------------
    # Подключение / отключение
    # ------------------------------------------------------------------

    def connect(self) -> dict[str, Any]:
        """
        Запустить dbgs.exe, подключить отладчик, запустить polling.

        Возвращает
        ----------
        dict
            {'ok': bool, 'port': int, 'message': str}
        """
        with self._state_lock:
            if self._state not in (SessionState.IDLE, SessionState.ERROR):
                return {"ok": False, "message": f"Сессия уже в состоянии '{self._state}'"}

            self._set_state(SessionState.CONNECTING)

        try:
            self.launcher.start_dbgs()
            self.rdbg.attach()
            self._set_state(SessionState.ATTACHED)
            self._start_polling()
            return {"ok": True, "port": self._port, "message": "Отладчик подключён"}
        except (LaunchError, RdbgError) as exc:
            self._set_state(SessionState.ERROR, str(exc))
            return {"ok": False, "message": str(exc)}

    def disconnect(self) -> dict[str, Any]:
        """Отсоединить отладчик и остановить все процессы."""
        self._set_state(SessionState.DISCONNECTING)
        self._stop_polling()

        errors = []
        try:
            self.rdbg.detach()
        except RdbgError as exc:
            errors.append(f"detach: {exc}")
        finally:
            self.launcher.stop_all()

        self._set_state(SessionState.IDLE)
        msg = "Сессия завершена"
        if errors:
            msg += " (с предупреждениями: " + "; ".join(errors) + ")"
        return {"ok": True, "message": msg}

    # ------------------------------------------------------------------
    # Управление breakpoints
    # ------------------------------------------------------------------

    def set_breakpoints(self, file_path: str, lines: list[int]) -> dict[str, Any]:
        module_id = self.mapper.resolve(file_path)
        try:
            self.rdbg.set_breakpoints(module_id, lines)
            return {
                "ok": True,
                "module_id": module_id,
                "lines": lines,
            }
        except RdbgError as exc:
            return {"ok": False, "message": str(exc)}

    def clear_breakpoints(self, file_path: Optional[str] = None) -> dict[str, Any]:
        module_id = self.mapper.resolve(file_path) if file_path else None
        try:
            self.rdbg.clear_breakpoints(module_id)
            return {"ok": True}
        except RdbgError as exc:
            return {"ok": False, "message": str(exc)}

    # ------------------------------------------------------------------
    # Запуск клиента 1С
    # ------------------------------------------------------------------

    def launch(self) -> dict[str, Any]:
        """Запустить тонкий клиент 1С в режиме отладки."""
        try:
            self.launcher.start_client()
            return {"ok": True, "message": "1С:Предприятие запущен с отладкой"}
        except LaunchError as exc:
            return {"ok": False, "message": str(exc)}

    # ------------------------------------------------------------------
    # Управление выполнением
    # ------------------------------------------------------------------

    def step_over(self) -> dict[str, Any]:
        return self._exec_step(self.rdbg.step_over, "StepOver")

    def step_into(self) -> dict[str, Any]:
        return self._exec_step(self.rdbg.step_into, "StepIn")

    def step_out(self) -> dict[str, Any]:
        return self._exec_step(self.rdbg.step_out, "StepOut")

    def continue_execution(self) -> dict[str, Any]:
        try:
            self.rdbg.continue_execution()
            self._set_state(SessionState.RUNNING)
            return {"ok": True}
        except RdbgError as exc:
            return {"ok": False, "message": str(exc)}

    def _exec_step(self, fn, name: str) -> dict[str, Any]:
        try:
            fn()
            return {"ok": True, "step": name}
        except RdbgError as exc:
            return {"ok": False, "message": str(exc)}

    # ------------------------------------------------------------------
    # Инспекция
    # ------------------------------------------------------------------

    def get_call_stack(self) -> dict[str, Any]:
        try:
            frames = self.rdbg.get_call_stack()
            enriched = []
            for f in frames:
                enriched.append({
                    "module_id": f["module"],
                    "line": f["line"],
                    "name": f["name"],
                })
            return {"ok": True, "frames": enriched}
        except RdbgError as exc:
            return {"ok": False, "message": str(exc)}

    def get_variables(self) -> dict[str, Any]:
        try:
            variables = self.rdbg.get_local_variables()
            return {"ok": True, "variables": variables}
        except RdbgError as exc:
            return {"ok": False, "message": str(exc)}

    def evaluate(self, expression: str) -> dict[str, Any]:
        try:
            result = self.rdbg.evaluate(expression)
            return {"ok": True, "expression": expression, "result": result}
        except RdbgError as exc:
            return {"ok": False, "message": str(exc)}

    # ------------------------------------------------------------------
    # Статус
    # ------------------------------------------------------------------

    def get_status(self) -> dict[str, Any]:
        rdbg_status = self.rdbg.get_status()
        return {
            "session_state": self._state,
            "last_error": self._last_error,
            "rdbg": rdbg_status,
            "dbgs_running": self.launcher.is_dbgs_running(),
            "client_running": self.launcher.is_client_running(),
            "dbgs_pid": self.launcher.dbgs_pid,
            "client_pid": self.launcher.client_pid,
            "port": self._port,
        }

    # ------------------------------------------------------------------
    # Polling thread
    # ------------------------------------------------------------------

    def _start_polling(self) -> None:
        self._stop_event.clear()
        self._poll_thread = threading.Thread(
            target=self._poll_loop,
            name="ptm-debug-poll",
            daemon=True,
        )
        self._poll_thread.start()

    def _stop_polling(self) -> None:
        self._stop_event.set()
        if self._poll_thread and self._poll_thread.is_alive():
            self._poll_thread.join(timeout=5)
        self._poll_thread = None

    def _poll_loop(self) -> None:
        """Фоновый поток: периодически опрашивает статус отладчика."""
        while not self._stop_event.is_set():
            try:
                status = self.rdbg.get_status()
                if status.get("state") == "stopped":
                    with self._state_lock:
                        if self._state == SessionState.RUNNING:
                            self._state = SessionState.STOPPED
                            logger.info("Breakpoint hit — сессия остановлена")
            except RdbgError:
                pass  # dbgs.exe может быть временно недоступен
            time.sleep(self._poll_interval)

    # ------------------------------------------------------------------
    # Вспомогательные методы
    # ------------------------------------------------------------------

    def _set_state(self, state: str, error: str = "") -> None:
        with self._state_lock:
            self._state = state
            self._last_error = error

    @staticmethod
    def _find_free_port(port_range: list[int]) -> int:
        import socket
        start, end = port_range[0], port_range[1]
        for port in range(start, end + 1):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("localhost", port))
                    return port
                except OSError:
                    continue
        raise RuntimeError(f"Нет свободного порта в диапазоне {start}–{end}")


# ------------------------------------------------------------------
# Глобальная сессия (один экземпляр на процесс MCP-сервера)
# ------------------------------------------------------------------

_session: Optional[DebugSession] = None


def get_session() -> Optional[DebugSession]:
    return _session


def create_session(config: dict[str, Any]) -> DebugSession:
    global _session
    if _session is not None:
        try:
            _session.disconnect()
        except Exception:
            pass
    _session = DebugSession(config)
    return _session
