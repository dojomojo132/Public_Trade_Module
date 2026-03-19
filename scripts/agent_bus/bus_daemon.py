"""
bus_daemon.py — Запуск оркестратора/агента в фоновом режиме (Windows + Linux).

Использование:
    # Запустить оркестратор в фоне, вывод → файл
    python scripts/agent_bus/bus_daemon.py start orchestrator --bus-dir .agent-bus

    # Запустить агента в фоне
    python scripts/agent_bus/bus_daemon.py start agent --agent-id copilot-backend --direction backend

    # Проверить статус всех фоновых процессов
    python scripts/agent_bus/bus_daemon.py status

    # Остановить процесс по имени
    python scripts/agent_bus/bus_daemon.py stop orchestrator
    python scripts/agent_bus/bus_daemon.py stop copilot-backend

    # Показать хвост лог-файла
    python scripts/agent_bus/bus_daemon.py logs orchestrator --lines 50
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

# Папка для PID-файлов и логов фоновых процессов
DAEMON_DIR = Path(".agent-bus-daemon")

# ──────────────────────────────────────────────────────────────────────────────
# Утилиты
# ──────────────────────────────────────────────────────────────────────────────

def _pid_file(name: str) -> Path:
    DAEMON_DIR.mkdir(exist_ok=True)
    return DAEMON_DIR / f"{name}.pid.json"


def _log_file(name: str) -> Path:
    DAEMON_DIR.mkdir(exist_ok=True)
    return DAEMON_DIR / f"{name}.log"


def _save_pid(name: str, pid: int, cmd: list[str]) -> None:
    data = {"name": name, "pid": pid, "cmd": cmd, "started": time.strftime("%Y-%m-%dT%H:%M:%S")}
    _pid_file(name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_pid(name: str) -> dict | None:
    p = _pid_file(name)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _is_running(pid: int) -> bool:
    """Проверить, жив ли процесс с указанным PID."""
    try:
        if sys.platform == "win32":
            import ctypes
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            h = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
            if not h:
                return False
            exitcode = ctypes.c_ulong()
            ctypes.windll.kernel32.GetExitCodeProcess(h, ctypes.byref(exitcode))
            ctypes.windll.kernel32.CloseHandle(h)
            return exitcode.value == 259  # STILL_ACTIVE
        else:
            os.kill(pid, 0)
            return True
    except (OSError, ProcessLookupError):
        return False


def _kill(pid: int) -> None:
    """Завершить процесс."""
    try:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/PID", str(pid), "/F"], check=False,
                           capture_output=True)
        else:
            os.kill(pid, signal.SIGTERM)
            time.sleep(1)
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    except Exception as e:
        print(f"  Ошибка завершения PID {pid}: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# Команды
# ──────────────────────────────────────────────────────────────────────────────

def cmd_start(args: argparse.Namespace) -> None:
    # Собрать команду для запуска
    this_dir = Path(__file__).parent
    bus_dir  = args.bus_dir

    if args.component == "orchestrator":
        name = "orchestrator"
        cmd  = [
            sys.executable, "-m", "scripts.agent_bus.orchestrator_loop",
            "--bus-dir", bus_dir,
        ]
    elif args.component == "agent":
        if not args.agent_id:
            print("Укажите --agent-id для агента")
            sys.exit(1)
        name = args.agent_id
        cmd  = [
            sys.executable, str(this_dir / "agent_worker.py"),
            "--agent-id", args.agent_id,
            "--direction", args.direction or "general",
            "--bus-dir", bus_dir,
        ]
    elif args.component == "monitor":
        name = "monitor"
        cmd  = [
            sys.executable, str(this_dir / "bus_monitor.py"),
            "--bus-dir", bus_dir,
            "--interval", str(args.interval or 3),
        ]
    elif args.component == "api":
        name = "api-server"
        cmd  = [
            sys.executable, str(this_dir / "api_server.py"),
            "--bus-dir", bus_dir,
            "--host", args.host or "0.0.0.0",
            "--port", str(args.port or 8765),
        ]
    else:
        print(f"Неизвестный компонент: {args.component}")
        sys.exit(1)

    # Проверить — не запущен ли уже
    existing = _load_pid(name)
    if existing and _is_running(existing["pid"]):
        print(f"  ⚠ {name} уже запущен (PID {existing['pid']})")
        return

    log_path = _log_file(name)
    print(f"  Запуск {name} → лог: {log_path}")

    # Запустить процесс в фоне
    log_f = open(log_path, "a", encoding="utf-8")
    if sys.platform == "win32":
        # Windows: DETACHED_PROCESS — у процесса нет консоли
        CREATE_NO_WINDOW   = 0x08000000
        DETACHED_PROCESS   = 0x00000008
        proc = subprocess.Popen(
            cmd,
            stdout=log_f,
            stderr=log_f,
            creationflags=CREATE_NO_WINDOW | DETACHED_PROCESS,
            close_fds=True,
        )
    else:
        # Linux/Mac: start_new_session=True
        proc = subprocess.Popen(
            cmd,
            stdout=log_f,
            stderr=log_f,
            start_new_session=True,
            close_fds=True,
        )

    _save_pid(name, proc.pid, cmd)
    print(f"  ✓ {name} запущен (PID {proc.pid})")
    print(f"    Логи: python scripts/agent_bus/bus_daemon.py logs {name}")


def cmd_stop(args: argparse.Namespace) -> None:
    name = args.name
    data = _load_pid(name)
    if not data:
        print(f"  {name}: нет PID-файла (не запускался через daemon)")
        return
    pid = data["pid"]
    if not _is_running(pid):
        print(f"  {name}: процесс PID {pid} уже не работает")
        _pid_file(name).unlink(missing_ok=True)
        return
    print(f"  Завершение {name} (PID {pid})...")
    _kill(pid)
    time.sleep(0.5)
    if _is_running(pid):
        print(f"  ⚠ Процесс {pid} ещё жив — попробуйте taskkill /PID {pid} /F")
    else:
        print(f"  ✓ {name} остановлен")
    _pid_file(name).unlink(missing_ok=True)


def cmd_status(args: argparse.Namespace) -> None:
    if not DAEMON_DIR.exists():
        print("  Нет запущенных фоновых процессов (папка .agent-bus-daemon не существует)")
        return

    pid_files = list(DAEMON_DIR.glob("*.pid.json"))
    if not pid_files:
        print("  Нет запущенных фоновых процессов")
        return

    print(f"\n  {'NAME':<25} {'PID':<8} {'STATUS':<12} STARTED")
    print(f"  {'─'*25} {'─'*8} {'─'*12} {'─'*20}")
    for pf in sorted(pid_files):
        try:
            data = json.loads(pf.read_text(encoding="utf-8"))
        except Exception:
            continue
        pid    = data.get("pid", 0)
        name   = data.get("name", pf.stem)
        started = data.get("started", "—")
        status = "🟢 running" if _is_running(pid) else "🔴 stopped"
        print(f"  {name:<25} {pid:<8} {status:<12} {started}")
    print()


def cmd_logs(args: argparse.Namespace) -> None:
    name  = args.name
    lines = args.lines or 30
    log_p = _log_file(name)
    if not log_p.exists():
        print(f"  Лог-файл не найден: {log_p}")
        return
    # Последние N строк
    text = log_p.read_text(encoding="utf-8", errors="replace").splitlines()
    tail = text[-lines:] if len(text) > lines else text
    print(f"\n  === {log_p} (последние {lines} строк) ===\n")
    print("\n".join(tail))
    print()


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Управление фоновыми процессами agent-bus"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # start
    p_start = sub.add_parser("start", help="Запустить компонент в фоне")
    p_start.add_argument("component", choices=["orchestrator", "agent", "monitor", "api"],
                         help="Что запустить")
    p_start.add_argument("--bus-dir",   default=".agent-bus")
    p_start.add_argument("--agent-id",  help="ID агента (только для agent)")
    p_start.add_argument("--direction", help="Направление агента", default="general")
    p_start.add_argument("--interval",  type=int, help="Интервал монитора (сек)", default=3)
    p_start.add_argument("--host",      help="Хост API-сервера", default="0.0.0.0")
    p_start.add_argument("--port",      type=int, help="Порт API-сервера", default=8765)

    # stop
    p_stop = sub.add_parser("stop", help="Остановить фоновый процесс")
    p_stop.add_argument("name", help="Имя процесса (orchestrator / agent-id / monitor / api-server)")

    # status
    sub.add_parser("status", help="Показать статус всех фоновых процессов")

    # logs
    p_logs = sub.add_parser("logs", help="Показать лог-файл процесса")
    p_logs.add_argument("name", help="Имя процесса")
    p_logs.add_argument("--lines", type=int, default=30, help="Последние N строк")

    args = parser.parse_args()

    if args.command == "start":
        cmd_start(args)
    elif args.command == "stop":
        cmd_stop(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "logs":
        cmd_logs(args)


if __name__ == "__main__":
    main()
