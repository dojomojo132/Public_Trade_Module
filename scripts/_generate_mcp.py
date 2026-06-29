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
  context-mcp     — контекст 1С: resolve/get/moc/feedback (stdio Python)
  dev-mcp         — backup/dump/deploy/sync_obsidian (stdio Python)
  tg-dashboard    — Telegram-дашборд задач (stdio Python)
  obsidian-vault  — Obsidian Knowledge Graph (SSE)
"""

import base64
import sys
import json
import pathlib

PROJ_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJ_ROOT / "scripts"))
from _project_config import get

MCP_OUT = PROJ_ROOT / ".vscode" / "mcp.json"
REPO_ROOT = PROJ_ROOT  # git root = корень проекта (PTM)
CURSOR_MCP_OUT = REPO_ROOT / ".cursor" / "mcp.json"
# Git root = PROJ_ROOT; Grok ищет .grok/config.toml до git root, не выше
GROK_CONFIG_OUT = PROJ_ROOT / ".grok" / "config.toml"
GROK_HOOK_OUT = PROJ_ROOT / ".grok" / "hooks" / "sync-graph-after-edit.json"
STANDARD_MCP_OUT = PROJ_ROOT / ".mcp.json"


def _paths() -> tuple[str, str]:
    py = str((PROJ_ROOT / ".venv" / "Scripts" / "python.exe").resolve())
    root = str(PROJ_ROOT.resolve())
    return py, root


def _abs_script(rel_script: str) -> str:
    return str((PROJ_ROOT / rel_script).resolve())


def _stdio_server(script: str) -> dict:
    """Шаблон stdio MCP-сервера с абсолютными путями (работает из любого workspace root)."""
    py, root = _paths()
    return {
        "type": "stdio",
        "command": py,
        "args": [_abs_script(script)],
        "cwd": root,
        "env": {"PYTHONPATH": root, "PYTHONIOENCODING": "utf-8"},
    }


def _cursor_stdio_server(script: str) -> dict:
    py, root = _paths()
    return {
        "command": py,
        "args": [_abs_script(script)],
        "cwd": root,
        "env": {"PYTHONPATH": root, "PYTHONIOENCODING": "utf-8"},
    }


def _grok_stdio_toml(name: str, script: str) -> list[str]:
    py, root = _paths()
    key = f'"{name}"' if "-" in name else name
    root_fwd = root.replace("\\", "/")
    lines = [
        f"[mcp_servers.{key}]",
        f'command = "{py.replace(chr(92), "/")}"',
        "args = [",
        f'  "{_abs_script(script).replace(chr(92), "/")}"',
        "]",
        f'env = {{ PYTHONPATH = "{root_fwd}", PYTHONIOENCODING = "utf-8" }}',
        "enabled = true",
        "",
    ]
    return lines


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

    # ── 1С HTTP MCP → stdio-прокси (CallMcpTool не поднимает url/sse напрямую) ──
    onec_url = get("mcp.onec.url") or ""
    if onec_url:
        servers["onec-mcp"] = _stdio_server("scripts/onec_http_mcp_proxy.py")

    # ── Контекст 1С (stdio) ─────────────────────────────────────────────────
    if get("mcp.context.enabled"):
        servers["context-mcp"] = _stdio_server("scripts/context_mcp_server.py")

    # ── Инфраструктура разработки (stdio) ─────────────────────────────────
    if get("mcp.dev.enabled"):
        servers["dev-mcp"] = _stdio_server("scripts/dev_mcp_server.py")

    # ── Telegram dashboard (stdio) ────────────────────────────────────────
    if get("mcp.tg_dashboard.enabled"):
        servers["tg-dashboard"] = _stdio_server("scripts/tg_dashboard_mcp_server.py")

    # ── Управление Конфигуратором (stdio) ───────────────────────────────────
    if get("mcp.configurator.enabled"):
        servers["onec-configurator"] = _stdio_server("scripts/configurator_bridge.py")

    # ── RDBG Отладчик BSL (stdio) ────────────────────────────────────────────
    if get("mcp.debug.enabled"):
        servers["ptm-debug"] = _stdio_server("scripts/debug/debug_mcp_server.py")

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

    # Cursor: отдельный формат mcpServers (абсолютные пути)
    cursor_servers = {}
    for name, cfg in servers.items():
        if cfg.get("type") == "stdio":
            cursor_servers[name] = _cursor_stdio_server(cfg["args"][0])
        elif cfg.get("type") == "sse":
            cursor_entry = {"type": "sse", "url": cfg["url"]}
            if cfg.get("headers"):
                cursor_entry["headers"] = cfg["headers"]
            cursor_servers[name] = cursor_entry

    CURSOR_MCP_OUT.parent.mkdir(parents=True, exist_ok=True)
    CURSOR_MCP_OUT.write_text(
        json.dumps({"mcpServers": cursor_servers}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # Grok native config (приоритетнее .cursor/mcp.json; cwd не требуется — абсолютные args)
    grok_lines = [
        "# Сгенерировано: python scripts/_generate_mcp.py",
        "# Grok читает из <git-root>/.grok/config.toml",
        "",
        "[skills]",
        'paths = [".github/skills"]',
        "",
    ]
    script_map = {
        "context-mcp": "scripts/context_mcp_server.py",
        "dev-mcp": "scripts/dev_mcp_server.py",
        "tg-dashboard": "scripts/tg_dashboard_mcp_server.py",
        "onec-configurator": "scripts/configurator_bridge.py",
        "onec-mcp": "scripts/onec_http_mcp_proxy.py",
        "ptm-debug": "scripts/debug/debug_mcp_server.py",
    }
    for name, rel in script_map.items():
        if name in servers:
            grok_lines.extend(_grok_stdio_toml(name, rel))
    GROK_CONFIG_OUT.parent.mkdir(parents=True, exist_ok=True)
    GROK_CONFIG_OUT.write_text("\n".join(grok_lines), encoding="utf-8")

    # MCP standard .mcp.json (fallback для Grok compat)
    std_servers = {}
    for name, cfg in servers.items():
        if cfg.get("type") == "stdio":
            std_servers[name] = {
                "command": cfg["command"],
                "args": cfg["args"],
                "env": cfg.get("env", {}),
            }
        elif cfg.get("type") == "sse":
            entry = {"type": "sse", "url": cfg["url"]}
            if cfg.get("headers"):
                entry["headers"] = cfg["headers"]
            std_servers[name] = entry
    for out_path in (STANDARD_MCP_OUT, REPO_ROOT / ".mcp.json"):
        out_path.write_text(
            json.dumps({"mcpServers": std_servers}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    py, _root = _paths()
    hooks_dir = PROJ_ROOT / ".grok" / "hooks" / "scripts"
    bsl_hook_script = (hooks_dir / "bsl_post_edit.py").resolve()
    sync_hook_script = (hooks_dir / "sync_graph_after_edit.py").resolve()
    py_cmd = py.replace(chr(92), "/")
    hook_payload = {
        "hooks": {
            "PostToolUse": [
                {
                    "matcher": "search_replace|edit_files|create_file|Write|Edit|MultiEdit|StrReplace",
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"{py_cmd} {bsl_hook_script.as_posix()}",
                            "timeout": 5,
                            "env": {"PYTHONIOENCODING": "utf-8"},
                        },
                        {
                            "type": "command",
                            "command": f"{py_cmd} {sync_hook_script.as_posix()}",
                            "timeout": 15,
                            "env": {"PYTHONIOENCODING": "utf-8"},
                        },
                    ],
                }
            ]
        }
    }
    GROK_HOOK_OUT.parent.mkdir(parents=True, exist_ok=True)
    GROK_HOOK_OUT.write_text(json.dumps(hook_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    enabled = list(servers.keys())
    print(f"  OK    .vscode/mcp.json сгенерирован ({len(enabled)} сервер(ов)): {', '.join(enabled)}")
    print(f"  OK    .cursor/mcp.json сгенерирован для Cursor ({len(cursor_servers)} сервер(ов))")
    print(f"  OK    {GROK_CONFIG_OUT} — Grok project MCP")
    print(f"  OK    {GROK_HOOK_OUT} — Grok hook")
    print(f"  OK    {STANDARD_MCP_OUT} (+ workspace .mcp.json) — MCP standard")

    # Дескрипторы CallMcpTool в mcps/
    try:
        import _generate_mcps_descriptors as gen_desc  # noqa: PLC0415
        gen_desc.generate(dry_run=False)
    except Exception as exc:  # noqa: BLE001
        print(f"  WARN  mcps descriptors: {exc}")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    generate(dry_run=dry)
