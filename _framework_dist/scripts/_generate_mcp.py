"""
_generate_mcp.py
Генерирует .vscode/mcp.json из настроек .github/project-config.yml.
Запуск: python scripts/_generate_mcp.py [--dry-run]

Читает секцию mcp.* из project-config.yml и собирает .vscode/mcp.json
только с включёнными серверами (enabled: true).

Поддерживаемые серверы:
  1c-mcp          — 1С HTTP MCP (SSE), проверка метаданных ИБ
  1c-configurator — управление окном Конфигуратора (stdio Python)
  ptm-debug       — RDBG отладчик BSL (stdio Python)
  obsidian-vault  — Obsidian Knowledge Graph (SSE)
"""

import sys
import json
import pathlib

PROJ_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJ_ROOT / "scripts"))
from _project_config import get

MCP_OUT = PROJ_ROOT / ".vscode" / "mcp.json"


def _read_existing() -> dict:
    """Читает существующий mcp.json (для сохранения ручных настроек пользователя)."""
    if MCP_OUT.exists():
        try:
            import re
            text = MCP_OUT.read_text(encoding="utf-8")
            # Убираем JSONC комментарии //...
            text = re.sub(r"//[^\n]*", "", text)
            return json.loads(text).get("servers", {})
        except Exception:
            return {}
    return {}


def build_servers() -> dict:
    """Строит словарь серверов на основе project-config.yml."""
    servers = {}

    # ── 1С MCP (SSE) ────────────────────────────────────────────────────────
    onec_url = get("mcp.onec.url") or ""
    if onec_url:
        servers["1c-mcp"] = {
            "type": "sse",
            "url": onec_url.rstrip("/")
        }

    # ── Управление Конфигуратором (stdio) ───────────────────────────────────
    if get("mcp.configurator.enabled"):
        servers["1c-configurator"] = {
            "type": "stdio",
            "command": "${workspaceFolder}\\.venv\\Scripts\\python.exe",
            "args": ["scripts/configurator_bridge.py"],
            "cwd": "${workspaceFolder}",
            "env": {"PYTHONPATH": "${workspaceFolder}"}
        }

    # ── RDBG Отладчик BSL (stdio) ────────────────────────────────────────────
    if get("mcp.debug.enabled"):
        servers["ptm-debug"] = {
            "type": "stdio",
            "command": "${workspaceFolder}\\.venv\\Scripts\\python.exe",
            "args": ["scripts/debug/debug_mcp_server.py"],
            "cwd": "${workspaceFolder}",
            "env": {"PYTHONPATH": "${workspaceFolder}"}
        }

    # ── Obsidian Knowledge Graph (SSE) ───────────────────────────────────────
    obsidian_enabled = get("mcp.obsidian.enabled")
    obsidian_url = get("mcp.obsidian.url") or "http://localhost:3001/mcp"
    obsidian_token = get("mcp.obsidian.token") or ""
    if obsidian_enabled and obsidian_token:
        servers["obsidian-vault"] = {
            "type": "sse",
            "url": obsidian_url,
            "headers": {"Authorization": f"Bearer {obsidian_token}"}
        }
    elif obsidian_enabled and not obsidian_token:
        print("  WARN  mcp.obsidian.enabled=true но mcp.obsidian.token не задан — сервер пропущен")

    return servers


def generate(dry_run: bool = False) -> None:
    servers = build_servers()

    if not servers:
        print("  INFO  Нет включённых MCP-серверов (проверь project-config.yml)")
        print("        Для включения сервера задай URL/token и enabled: true")
        return

    result = {"servers": servers}
    out_text = json.dumps(result, ensure_ascii=False, indent=4)

    # Добавляем заголовок-комментарий (JSONC)
    header = (
        "// Сгенерировано автоматически: python scripts/_generate_mcp.py\n"
        "// Источник настроек: .github/project-config.yml (секция mcp.*)\n"
        "// Для пересоздания: python scripts/_generate_mcp.py\n"
    )

    content = header + out_text + "\n"

    if dry_run:
        print("=== DRY RUN: .vscode/mcp.json ===")
        print(content)
        return

    MCP_OUT.parent.mkdir(parents=True, exist_ok=True)
    MCP_OUT.write_text(content, encoding="utf-8")

    enabled = list(servers.keys())
    print(f"  OK    .vscode/mcp.json сгенерирован ({len(enabled)} сервер(ов)): {', '.join(enabled)}")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    generate(dry_run=dry)
