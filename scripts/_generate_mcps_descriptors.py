# -*- coding: utf-8 -*-
"""
Генерирует дескрипторы инструментов MCP в mcps/<server>/tools/*.json
для прямого вызова через CallMcpTool в Cursor.

Запуск: python scripts/_generate_mcps_descriptors.py [--dry-run]
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

PROJ_ROOT = Path(__file__).resolve().parent.parent
MCPS_ROOT = PROJ_ROOT / "mcps"
VENV_PYTHON = PROJ_ROOT / ".venv" / "Scripts" / "python.exe"

STDIO_SERVERS = {
    "context-mcp": "scripts/context_mcp_server.py",
    "dev-mcp": "scripts/dev_mcp_server.py",
    "tg-dashboard": "scripts/tg_dashboard_mcp_server.py",
    "onec-configurator": "scripts/configurator_bridge.py",
    "ptm-debug": "scripts/debug/debug_mcp_server.py",
}

SERVER_INSTRUCTIONS = {
    "context-mcp": (
        "Первый источник разведки по задачам 1С. "
        "Порядок: context_resolve → context_get (при необходимости context_moc). "
        "Использует graph_index.json из vault .copilot/."
    ),
    "dev-mcp": (
        "Инфраструктура разработки: backup, dump, validate, deploy, monitor, sync_obsidian. "
        "Операции с ИБ и графом — только через этот сервер, не через терминал."
    ),
    "tg-dashboard": (
        "Telegram-дашборд прогресса задач. Токены из .env (TG_BOT_TOKEN, TG_CHAT_ID)."
    ),
    "onec-configurator": (
        "UI-автоматизация окна Конфигуратора 1С: скриншоты, клики, ввод текста."
    ),
    "ptm-debug": (
        "RDBG-отладка BSL: debug_connect первым, затем breakpoints/step/continue."
    ),
    "onec-mcp": (
        "HTTP MCP 1С через stdio-прокси: метаданные и данные ИБ. "
        "Источник истины — ИБ, не файлы на диске."
    ),
}

EXTRACT_TOOLS = r"""
import importlib.util, json, pathlib, sys
root = pathlib.Path(sys.argv[1])
script = root / sys.argv[2]
spec = importlib.util.spec_from_file_location("_mcp", script)
mod = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(root / "scripts"))
spec.loader.exec_module(mod)
if hasattr(mod, "_active_tools"):
    tools = mod._active_tools()
else:
    tools = mod.TOOLS
print(json.dumps(tools, ensure_ascii=False))
"""


def load_tools_from_script(rel_script: str) -> list[dict]:
    result = subprocess.run(
        [str(VENV_PYTHON), "-c", EXTRACT_TOOLS, str(PROJ_ROOT), rel_script],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(PROJ_ROOT),
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Не удалось извлечь TOOLS из {rel_script}: {(result.stderr or result.stdout)[-400:]}"
        )
    return json.loads(result.stdout.strip())


def write_tool(server_dir: Path, tool: dict, dry_run: bool) -> None:
    name = tool.get("name")
    if not name:
        return
    out = server_dir / "tools" / f"{name}.json"
    payload = {
        "name": name,
        "description": tool.get("description", ""),
        "inputSchema": tool.get("inputSchema", {"type": "object", "properties": {}}),
    }
    if dry_run:
        print(f"  would write {out.relative_to(MCPS_ROOT)}")
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_instructions(server_dir: Path, server_name: str, dry_run: bool) -> None:
    text = SERVER_INSTRUCTIONS.get(server_name, "")
    if not text:
        return
    out = server_dir / "INSTRUCTIONS.md"
    content = f"# {server_name}\n\n{text}\n"
    if dry_run:
        print(f"  would write {out.relative_to(MCPS_ROOT)}")
        return
    out.write_text(content, encoding="utf-8")


def generate(dry_run: bool = False) -> None:
    MCPS_ROOT.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}

    for server_name, rel_script in STDIO_SERVERS.items():
        server_dir = MCPS_ROOT / server_name
        tools = load_tools_from_script(rel_script)
        active_names = {t.get("name") for t in tools if t.get("name")}
        tools_dir = server_dir / "tools"
        if tools_dir.exists() and not dry_run:
            for stale in tools_dir.glob("*.json"):
                if stale.stem not in active_names:
                    stale.unlink()
        for tool in tools:
            write_tool(server_dir, tool, dry_run)
        write_instructions(server_dir, server_name, dry_run)
        counts[server_name] = len(tools)
        print(f"  OK    {server_name}: {len(tools)} tool(s)")

    # Инструменты HTTP 1С — копируем из legacy-папки 1c-mcp → onec-mcp
    legacy_dir = MCPS_ROOT / "1c-mcp" / "tools"
    onec_dir = MCPS_ROOT / "onec-mcp" / "tools"
    if legacy_dir.exists():
        onec_dir.mkdir(parents=True, exist_ok=True)
        for src in legacy_dir.glob("*.json"):
            dst = onec_dir / src.name
            if dry_run:
                print(f"  would copy {src.name} -> onec-mcp/tools/")
            else:
                dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        counts["onec-mcp"] = len(list(onec_dir.glob("*.json")))
        write_instructions(MCPS_ROOT / "onec-mcp", "onec-mcp", dry_run)
        print(f"  OK    onec-mcp: {counts['onec-mcp']} tool(s)")
    else:
        print("  WARN  1c-mcp/tools не найден — пропущен")

    total = sum(counts.values())
    action = "DRY RUN" if dry_run else "сгенерировано"
    print(f"\n  Итого {action}: {total} дескрипторов в {MCPS_ROOT}")


if __name__ == "__main__":
    generate(dry_run="--dry-run" in sys.argv)