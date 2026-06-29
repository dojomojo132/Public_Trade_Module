# -*- coding: utf-8 -*-
"""
Проверка цепочки: sync_1c_obsidian → graph_index.json → get_context.py → context-mcp.

Запуск: python scripts/verify_graph_context.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJ_ROOT = Path(__file__).resolve().parent.parent
VENV_PYTHON = PROJ_ROOT / ".venv" / "Scripts" / "python.exe"
CONFIG_FILE = PROJ_ROOT / "config.json"
SYNC_SCRIPT = PROJ_ROOT / "sync_1c_obsidian.py"
GET_CONTEXT = PROJ_ROOT / "scripts" / "get_context.py"
CONTEXT_MCP = PROJ_ROOT / "scripts" / "context_mcp_server.py"

OK = "\033[92m✓\033[0m"
FAIL = "\033[91m✗\033[0m"
errors = 0


def check(label: str, ok: bool, detail: str = "") -> None:
    global errors
    if ok:
        print(f"  {OK} {label}")
    else:
        print(f"  {FAIL} {label}" + (f" — {detail}" if detail else ""))
        errors += 1


def main() -> int:
    print("=" * 60)
    print("Проверка: граф 1С + context-mcp")
    print("=" * 60)

    print("\n[1] Файлы и пути")
    check("config.json", CONFIG_FILE.exists())
    check("sync_1c_obsidian.py", SYNC_SCRIPT.exists())
    check("scripts/get_context.py", GET_CONTEXT.exists())
    check("scripts/context_mcp_server.py", CONTEXT_MCP.exists())
    check(".venv python", VENV_PYTHON.exists())

    if not CONFIG_FILE.exists():
        return 1

    cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8-sig"))
    vault = Path(cfg["obsidian_vault_path"])
    graph = vault / ".copilot" / "graph_index.json"
    index = vault / cfg.get("obsidian_index_folder", "99-Meta/1C-Index")

    print("\n[2] Obsidian vault")
    check(f"vault: {vault}", vault.exists())
    check(f"1C-Index: {index}", index.exists())
    check(f"graph_index.json: {graph}", graph.exists())

    print("\n[3] project_paths (источник графа)")
    for name, p in cfg.get("project_paths", {}).items():
        check(f"{name} → {p}", Path(p).exists())

    print("\n[4] Содержимое graph_index.json")
    if graph.exists():
        g = json.loads(graph.read_text(encoding="utf-8-sig"))
        n = len(g.get("objects", {}))
        check(f"объектов в графе: {n}", n > 0, "граф пуст — запустите sync_1c_obsidian.py")
        for name, src in g.get("source_config", {}).items():
            check(f"source_config.{name}", Path(src).exists(), src)
        print(f"      generated_at: {g.get('generated_at', '?')}")

    print("\n[5] get_context.py (чтение графа)")
    if VENV_PYTHON.exists() and graph.exists():
        r = subprocess.run(
            [str(VENV_PYTHON), str(GET_CONTEXT), "resolve", "ДневнойОтчет"],
            cwd=str(PROJ_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        check("resolve 'ДневнойОтчет'", r.returncode == 0, (r.stderr or r.stdout)[-200:])
        if r.returncode == 0 and "Status:" in r.stdout:
            print(f"      {r.stdout.strip().splitlines()[1] if len(r.stdout.strip().splitlines()) > 1 else ''}")

    print("\n[6] context-mcp (импорт ядра)")
    if VENV_PYTHON.exists():
        r = subprocess.run(
            [str(VENV_PYTHON), "-c", "import sys; sys.path.insert(0,'scripts'); import get_context as c; import context_mcp_server as s; print('CORE_LOADED=', s.CORE_LOADED)"],
            cwd=str(PROJ_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=15,
        )
        check("context_mcp_server импортирует get_context", "CORE_LOADED= True" in r.stdout, r.stderr[-200:])

    print("\n[7] MCP-конфигурация")
    cursor_mcp = PROJ_ROOT.parent / ".cursor" / "mcp.json"
    vscode_mcp = PROJ_ROOT / ".vscode" / "mcp.json"
    check(".cursor/mcp.json", cursor_mcp.exists())
    check(".vscode/mcp.json", vscode_mcp.exists())
    if cursor_mcp.exists():
        mcp = json.loads(cursor_mcp.read_text(encoding="utf-8"))
        servers = mcp.get("mcpServers", {})
        check("context-mcp в .cursor/mcp.json", "context-mcp" in servers)
        check("dev-mcp в .cursor/mcp.json", "dev-mcp" in servers)

    print("\n" + "=" * 60)
    if errors == 0:
        print(f"{OK} Цепочка граф → context-mcp настроена корректно.")
        print("\nЦепочка:")
        print("  sync_1c_obsidian.py  →  {vault}/.copilot/graph_index.json")
        print("  get_context.py       →  читает graph_index.json")
        print("  context-mcp (MCP)    →  context_resolve / context_get")
        print("  dev-mcp              →  dev_sync_obsidian (пересборка графа)")
    else:
        print(f"{FAIL} Ошибок: {errors}")
    print("=" * 60)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())