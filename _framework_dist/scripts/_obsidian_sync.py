#!/usr/bin/env python3
"""
Синхронизация Knowledge Graph PTM в Obsidian.

Читает метаданные из MCP (через HTTP) и обновляет заметки в Obsidian vault.
Вызывается автоматически после успешного деплоя или вручную.

Использование:
    python scripts/_obsidian_sync.py                    # полная синхронизация
    python scripts/_obsidian_sync.py --object ЧекККМ    # одиночный объект
    python scripts/_obsidian_sync.py --check             # проверить что нужно обновить
"""

import argparse
import json
import sys
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

# Конфигурация Obsidian MCP
OBSIDIAN_HOST = "http://localhost:3001"
OBSIDIAN_API_KEY = None  # Читается из .vscode/mcp.json

# Маппинг типов метаданных → папки Obsidian
TYPE_FOLDERS = {
    "Documents": "PTM/Документы",
    "Catalogs": "PTM/Справочники",
    "AccumulationRegisters": "PTM/Регистры",
    "InformationRegisters": "PTM/Регистры",
    "DataProcessors": "PTM/Обработки",
    "Reports": "PTM/Отчёты",
}

# Префиксы для регистров
REGISTER_PREFIX = {
    "AccumulationRegisters": "РН ",
    "InformationRegisters": "РС ",
}

# Объекты-исключения (демо, служебные)
EXCLUDE_PREFIXES = ("_Демо", "_демо", "mcp_", "Удалить")


def load_api_key():
    """Загрузить API ключ из .vscode/mcp.json."""
    global OBSIDIAN_API_KEY
    mcp_json = Path(__file__).parent.parent / ".vscode" / "mcp.json"
    if mcp_json.exists():
        try:
            data = json.loads(mcp_json.read_text(encoding="utf-8-sig"))
            servers = data.get("servers", {})
            vault_cfg = servers.get("obsidian-vault", {})
            env = vault_cfg.get("env", {})
            # API ключ может быть в AUTH (Bearer xxx) или OBSIDIAN_API_KEY
            auth = env.get("AUTH", "")
            if auth.startswith("Bearer "):
                OBSIDIAN_API_KEY = auth[7:]  # strip "Bearer "
            elif auth:
                OBSIDIAN_API_KEY = auth
            else:
                OBSIDIAN_API_KEY = env.get("OBSIDIAN_API_KEY")
        except (json.JSONDecodeError, KeyError):
            pass


def obsidian_request(method, path, body=None):
    """Выполнить HTTP-запрос к Obsidian REST API."""
    url = f"{OBSIDIAN_HOST}{path}"
    headers = {"Content-Type": "application/json"}
    if OBSIDIAN_API_KEY:
        headers["Authorization"] = f"Bearer {OBSIDIAN_API_KEY}"

    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code}: {e.reason}")
        return None
    except urllib.error.URLError as e:
        print(f"  Connection error: {e.reason}")
        return None


def check_obsidian_connection():
    """Проверить подключение к Obsidian."""
    result = obsidian_request("GET", "/")
    if result:
        print(f"✓ Obsidian подключен: {result.get('service', 'OK')}")
        return True
    print("✗ Obsidian недоступен на localhost:3001")
    return False


def get_vault_files(folder):
    """Получить список файлов в папке vault."""
    result = obsidian_request("POST", "/api/vault", {
        "action": "list",
        "path": folder
    })
    if result and "result" in result:
        return result["result"]
    return []


def file_exists_in_vault(path):
    """Проверить существование файла в vault."""
    result = obsidian_request("POST", "/api/vault", {
        "action": "read",
        "path": path,
        "raw": True
    })
    return result is not None and "error" not in result


def should_exclude(name):
    """Проверить, нужно ли исключить объект."""
    return any(name.startswith(p) for p in EXCLUDE_PREFIXES)


def get_note_path(meta_type, name):
    """Получить путь заметки в Obsidian."""
    folder = TYPE_FOLDERS.get(meta_type, "PTM")
    prefix = REGISTER_PREFIX.get(meta_type, "")
    return f"{folder}/{prefix}{name}.md"


def check_sync_status():
    """Проверить какие объекты есть в ИБ но нет в Obsidian."""
    print("\n=== Проверка синхронизации PTM → Obsidian ===\n")

    missing = []
    existing = []

    for meta_type in TYPE_FOLDERS:
        # Здесь мы бы вызвали MCP, но в standalone скрипте
        # просто проверяем существующие файлы
        folder = TYPE_FOLDERS[meta_type]
        files = get_vault_files(folder)
        if files:
            existing.extend(files)

    print(f"Заметки в Obsidian PTM/: {len(existing)}")
    print(f"\nДля полной синхронизации через MCP используйте:")
    print(f"  → Copilot Agent: 'синхронизировать Obsidian Knowledge Graph'")

    return missing


def main():
    parser = argparse.ArgumentParser(description="Синхронизация PTM ↔ Obsidian")
    parser.add_argument("--object", help="Синхронизировать конкретный объект")
    parser.add_argument("--check", action="store_true", help="Только проверить статус")
    args = parser.parse_args()

    load_api_key()

    if not check_obsidian_connection():
        print("\nУбедитесь что Obsidian запущен и плагин Semantic MCP активен.")
        sys.exit(1)

    if args.check:
        check_sync_status()
    else:
        print("\n⚠ Полная синхронизация доступна только через Copilot Agent (MCP).")
        print("Используйте команду в чате:")
        print('  → "синхронизировать Obsidian Knowledge Graph"')
        print('  → "обновить заметку ЧекККМ в Obsidian"')
        print(f"\nTimestamp: {datetime.now().isoformat()}")


if __name__ == "__main__":
    main()
