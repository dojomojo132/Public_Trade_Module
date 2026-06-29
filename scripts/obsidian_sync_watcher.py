# -*- coding: utf-8 -*-
"""
Фоновый watcher: при изменениях в Конфигурация/ запускает sync_1c_obsidian.py.

Запуск: python scripts/obsidian_sync_watcher.py [--interval 15] [--debounce 45]
Останавливается: Ctrl+C
"""
import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

PROJ_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = PROJ_ROOT / "config.json"
VENV_PYTHON = PROJ_ROOT / ".venv" / "Scripts" / "python.exe"
SYNC_SCRIPT = PROJ_ROOT / "sync_1c_obsidian.py"
LOG_FILE = PROJ_ROOT / "logs" / "obsidian_watcher.log"


def log(msg: str) -> None:
    line = f"{datetime.now().isoformat(timespec='seconds')} {msg}"
    print(line, flush=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_watch_roots() -> list[Path]:
    cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8-sig"))
    return [Path(p) for p in cfg.get("project_paths", {}).values() if Path(p).exists()]


def snapshot_mtimes(roots: list[Path]) -> float:
    latest = 0.0
    for root in roots:
        for pattern in ("**/*.xml", "**/*.bsl"):
            for f in root.glob(pattern):
                try:
                    latest = max(latest, f.stat().st_mtime)
                except OSError:
                    pass
    return latest


def run_sync() -> bool:
    log("Запуск sync_1c_obsidian.py …")
    result = subprocess.run(
        [str(VENV_PYTHON), str(SYNC_SCRIPT)],
        cwd=str(PROJ_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )
    if result.returncode == 0:
        log("✅ Sync завершён")
        return True
    log(f"❌ Sync exit={result.returncode}: {(result.stderr or result.stdout)[-300:]}")
    return False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=15, help="Интервал опроса, сек")
    parser.add_argument("--debounce", type=int, default=45, help="Пауза после изменения, сек")
    args = parser.parse_args()

    roots = load_watch_roots()
    if not roots:
        log("Нет папок project_paths — выход")
        sys.exit(1)

    log(f"Watcher старт: roots={[str(r.name) for r in roots]}, interval={args.interval}s, debounce={args.debounce}s")

    last_seen = snapshot_mtimes(roots)
    pending_since: float | None = None

    while True:
        time.sleep(args.interval)
        current = snapshot_mtimes(roots)
        if current <= last_seen:
            continue

        if pending_since is None:
            pending_since = time.time()
            log("Обнаружены изменения, ожидание debounce …")
            continue

        if time.time() - pending_since < args.debounce:
            continue

        if run_sync():
            last_seen = snapshot_mtimes(roots)
        pending_since = None


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("Watcher остановлен")