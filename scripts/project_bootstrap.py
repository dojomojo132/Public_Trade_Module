# -*- coding: utf-8 -*-
"""
Bootstrap окружения проекта 1С при открытии workspace (читает config.json текущего репозитория).

Проверяет venv, vault, graph_index; при необходимости запускает sync.
Запуск: python scripts/project_bootstrap.py [--sync] [--json]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

PROJ_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = PROJ_ROOT / "config.json"
VENV_PYTHON = PROJ_ROOT / ".venv" / "Scripts" / "python.exe"
SYNC_SCRIPT = PROJ_ROOT / "sync_1c_obsidian.py"


def load_config() -> dict:
    return json.loads(CONFIG_FILE.read_text(encoding="utf-8-sig"))


def newest_config_mtime(cfg: dict) -> float:
    latest = 0.0
    for path_str in cfg.get("project_paths", {}).values():
        root = Path(path_str)
        if not root.exists():
            continue
        for pattern in ("**/*.xml", "**/*.bsl"):
            for f in root.glob(pattern):
                try:
                    latest = max(latest, f.stat().st_mtime)
                except OSError:
                    pass
    return latest


def run_sync() -> dict:
    result = subprocess.run(
        [str(VENV_PYTHON), str(SYNC_SCRIPT)],
        cwd=str(PROJ_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )
    return {
        "ok": result.returncode == 0,
        "exit_code": result.returncode,
        "stdout_tail": (result.stdout or "")[-500:],
        "stderr_tail": (result.stderr or "")[-500:],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sync", action="store_true", help="Принудительный sync")
    parser.add_argument("--json", action="store_true", help="JSON-вывод")
    args = parser.parse_args()

    report: dict = {
        "project_root": str(PROJ_ROOT),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "checks": {},
        "actions": [],
    }

    report["checks"]["venv_python"] = VENV_PYTHON.exists()
    if not VENV_PYTHON.exists():
        report["ok"] = False
        report["error"] = f"Не найден {VENV_PYTHON}. Создайте: python -m venv .venv && pip install -r requirements.txt"
        print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else report["error"])
        return 1

    cfg = load_config()
    vault = Path(cfg["obsidian_vault_path"])
    graph_index = vault / ".copilot" / "graph_index.json"

    report["checks"]["vault_exists"] = vault.exists()
    report["checks"]["graph_index_exists"] = graph_index.exists()

    stale = False
    if graph_index.exists():
        idx_mtime = graph_index.stat().st_mtime
        cfg_mtime = newest_config_mtime(cfg)
        stale = cfg_mtime > idx_mtime + 1
        report["checks"]["graph_index_stale"] = stale
    else:
        stale = True
        report["checks"]["graph_index_stale"] = True

    if args.sync or stale:
        reason = "forced" if args.sync else "stale_index"
        report["actions"].append({"sync": reason})
        sync_result = run_sync()
        report["sync"] = sync_result
        if not sync_result["ok"]:
            report["ok"] = False
            msg = f"Sync failed (exit {sync_result['exit_code']})"
            print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else msg)
            return 1

    report["ok"] = True
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        status = "sync выполнен" if report["actions"] else "всё актуально"
        print(f"✅ Bootstrap OK — vault={vault.name}, {status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())