# -*- coding: utf-8 -*-
"""
PostToolUse hook (только AdminReport):
после утверждённого редактирования файлов 1С — синхронизировать graph_index.json.

Запускается Grok/Cursor из .grok/hooks/sync-graph-after-edit.json
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

DEBOUNCE_SEC = 45
EDIT_TOOL_KEYWORDS = (
    "search_replace",
    "strreplace",
    "edit",
    "write",
    "create_file",
    "multi_replace",
    "replace",
)
CONFIG_MARKERS = (
    "конфигурация/",
    "конфигурация_техинструменты/",
    "configuration/",
)
GRAPH_EXTENSIONS = (".bsl", ".xml")


def repo_root() -> Path:
    for key in ("GROK_WORKSPACE_ROOT", "CLAUDE_PROJECT_DIR", "CURSOR_WORKSPACE_ROOT"):
        val = os.environ.get(key)
        if val:
            return Path(val).resolve()
    return Path(__file__).resolve().parents[3]


def project_root(repo: Path) -> Path:
    candidate = repo / "AdminReport_Project"
    return candidate if candidate.exists() else repo


def load_hook_input() -> dict:
    try:
        return json.load(sys.stdin)
    except Exception:
        return {}


def is_edit_tool(tool_name: str) -> bool:
    lower = (tool_name or "").lower()
    return any(kw in lower for kw in EDIT_TOOL_KEYWORDS)


def extract_paths(tool_input: object) -> list[str]:
    paths: list[str] = []
    if not isinstance(tool_input, dict):
        return paths

    for key in ("filePath", "file_path", "path", "target_file"):
        val = tool_input.get(key)
        if isinstance(val, str) and val:
            paths.append(val)

    for key in ("replacements", "edits", "files"):
        val = tool_input.get(key)
        if isinstance(val, list):
            for item in val:
                if isinstance(item, dict):
                    for k in ("filePath", "file_path", "path"):
                        p = item.get(k)
                        if isinstance(p, str) and p:
                            paths.append(p)
                elif isinstance(item, str):
                    paths.append(item)

    return paths


def affects_graph(file_path: str) -> bool:
    norm = file_path.replace("\\", "/").lower()
    if not norm.endswith(GRAPH_EXTENSIONS):
        return False
    return any(marker in norm for marker in CONFIG_MARKERS)


def should_sync(hook_input: dict) -> tuple[bool, str]:
    tool_name = hook_input.get("tool_name") or hook_input.get("toolName") or ""
    if not is_edit_tool(tool_name):
        return False, "not_edit_tool"

    tool_input = hook_input.get("tool_input") or hook_input.get("toolInput") or {}
    paths = extract_paths(tool_input)
    if not paths:
        return False, "no_paths"

    graph_paths = [p for p in paths if affects_graph(p)]
    if not graph_paths:
        return False, "not_config_graph_file"

    return True, graph_paths[0]


def debounce_ok(state_file: Path) -> bool:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    now = time.time()
    if state_file.exists():
        try:
            last = float(state_file.read_text(encoding="utf-8").strip())
            if now - last < DEBOUNCE_SEC:
                return False
        except ValueError:
            pass
    state_file.write_text(str(now), encoding="utf-8")
    return True


def spawn_sync(proj: Path, log_file: Path) -> None:
    venv_python = proj / ".venv" / "Scripts" / "python.exe"
    sync_script = proj / "sync_1c_obsidian.py"
    if not venv_python.exists() or not sync_script.exists():
        return

    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("a", encoding="utf-8") as log:
        log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} START sync_1c_obsidian.py\n")
        log.flush()
        proc = subprocess.Popen(
            [str(venv_python), str(sync_script)],
            cwd=str(proj),
            stdout=log,
            stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} PID={proc.pid}\n")


def main() -> None:
    hook_input = load_hook_input()
    ok, detail = should_sync(hook_input)
    if not ok:
        json.dump({}, sys.stdout)
        return

    repo = repo_root()
    proj = project_root(repo)
    state_file = repo / ".grok" / "state" / "last_graph_sync_trigger"
    log_file = proj / "logs" / "graph_sync_hook.log"

    if not debounce_ok(state_file):
        json.dump(
            {"systemMessage": "[AdminReport] Graph sync отложен (debounce 45с)"},
            sys.stdout,
            ensure_ascii=False,
        )
        return

    spawn_sync(proj, log_file)
    json.dump(
        {
            "systemMessage": (
                f"[AdminReport] Запущена синхронизация графа после правки: {detail}"
            )
        },
        sys.stdout,
        ensure_ascii=False,
    )


if __name__ == "__main__":
    main()