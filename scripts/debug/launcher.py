"""
launcher.py — Запуск и остановка dbgs.exe и 1cv8c.exe.

Управляет жизненным циклом двух процессов:
  1. dbgs.exe  — RDBG-сервер (отладчик-демон)
  2. 1cv8c.exe — тонкий клиент 1С с включённым режимом отладки

Принцип: запуск через subprocess.Popen с явным управлением PID.
"""

import os
import shutil
import signal
import subprocess
import time
from pathlib import Path
from typing import Optional


class LaunchError(Exception):
    """Ошибка запуска процесса."""


class Launcher:
    """
    Управляет процессами dbgs.exe и 1cv8c.exe.

    Параметры
    ----------
    platform_root : str | Path
        Корень установки 1С (содержит bin\\dbgs.exe, bin\\1cv8c.exe).
    ib_path : str | Path
        Путь к файловой информационной базе.
    ib_user : str
        Имя пользователя ИБ.
    ib_password : str
        Пароль пользователя ИБ.
    debug_host : str
        Хост для dbgs.exe (обычно 'localhost').
    debug_port : int
        Порт для dbgs.exe.
    """

    def __init__(
        self,
        platform_root: str | Path,
        ib_path: str | Path,
        ib_user: str = "Admin",
        ib_password: str = "",
        debug_host: str = "localhost",
        debug_port: int = 1550,
    ) -> None:
        self.platform_root = Path(platform_root)
        self.ib_path = Path(ib_path)
        self.ib_user = ib_user
        self.ib_password = ib_password
        self.debug_host = debug_host
        self.debug_port = debug_port

        self._dbgs_proc: Optional[subprocess.Popen] = None
        self._client_proc: Optional[subprocess.Popen] = None

    # ------------------------------------------------------------------
    # Свойства путей
    # ------------------------------------------------------------------

    @property
    def dbgs_exe(self) -> Path:
        return self.platform_root / "bin" / "dbgs.exe"

    @property
    def client_exe(self) -> Path:
        return self.platform_root / "bin" / "1cv8c.exe"

    # ------------------------------------------------------------------
    # dbgs.exe
    # ------------------------------------------------------------------

    def start_dbgs(self, startup_wait: float = 2.0) -> None:
        """
        Запустить dbgs.exe на указанном порту.

        Параметры
        ----------
        startup_wait : float
            Секунды ожидания после запуска (dbgs.exe инициализируется асинхронно).
        """
        if self._dbgs_proc and self._dbgs_proc.poll() is None:
            return  # уже запущен

        if not self.dbgs_exe.exists():
            raise LaunchError(f"dbgs.exe не найден: {self.dbgs_exe}")

        cmd = [
            str(self.dbgs_exe),
            f"--addr={self.debug_host}:{self.debug_port}",
            "--debug-area=all",
        ]
        self._dbgs_proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        time.sleep(startup_wait)

        if self._dbgs_proc.poll() is not None:
            raise LaunchError(
                f"dbgs.exe завершился сразу с кодом {self._dbgs_proc.returncode}"
            )

    def stop_dbgs(self) -> None:
        """Остановить dbgs.exe."""
        _terminate_proc(self._dbgs_proc)
        self._dbgs_proc = None

    # ------------------------------------------------------------------
    # 1cv8c.exe
    # ------------------------------------------------------------------

    def start_client(self, extra_args: Optional[list[str]] = None) -> None:
        """
        Запустить 1С:Предприятие (тонкий клиент) в режиме отладки.

        Параметры
        ----------
        extra_args : list[str] | None
            Дополнительные аргументы командной строки 1С.
        """
        if not self.client_exe.exists():
            raise LaunchError(f"1cv8c.exe не найден: {self.client_exe}")

        ib_conn = f"/F{self.ib_path}"
        cmd = [
            str(self.client_exe),
            "ENTERPRISE",
            ib_conn,
            f"/N{self.ib_user}",
            f"/P{self.ib_password}",
            "/debug",
            f"/debuggerURL=http://{self.debug_host}:{self.debug_port}",
        ]
        if extra_args:
            cmd.extend(extra_args)

        self._client_proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )

    def stop_client(self) -> None:
        """Остановить тонкий клиент 1С."""
        _terminate_proc(self._client_proc)
        self._client_proc = None

    # ------------------------------------------------------------------
    # Утилиты
    # ------------------------------------------------------------------

    def is_dbgs_running(self) -> bool:
        return self._dbgs_proc is not None and self._dbgs_proc.poll() is None

    def is_client_running(self) -> bool:
        return self._client_proc is not None and self._client_proc.poll() is None

    def stop_all(self) -> None:
        """Остановить все управляемые процессы."""
        self.stop_client()
        self.stop_dbgs()

    @property
    def dbgs_pid(self) -> Optional[int]:
        return self._dbgs_proc.pid if self._dbgs_proc else None

    @property
    def client_pid(self) -> Optional[int]:
        return self._client_proc.pid if self._client_proc else None


# ------------------------------------------------------------------
# Вспомогательные функции
# ------------------------------------------------------------------

def _terminate_proc(proc: Optional[subprocess.Popen]) -> None:
    if proc is None or proc.poll() is not None:
        return
    try:
        proc.terminate()
        proc.wait(timeout=5)
    except (subprocess.TimeoutExpired, OSError):
        try:
            proc.kill()
        except OSError:
            pass
