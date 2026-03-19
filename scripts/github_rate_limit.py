#!/usr/bin/env python3
"""
Проверка текущих лимитов GitHub API.
Использование:
    python scripts/github_rate_limit.py
    python scripts/github_rate_limit.py --token ghp_xxx...
    Или задать переменную окружения: GITHUB_TOKEN=ghp_xxx...
"""

import os
import sys
import argparse
from datetime import datetime, timezone
import urllib.request
import urllib.error
import json

# ─── ТОКЕН: задай через переменную окружения GITHUB_TOKEN ────────────────────
# Пример: set GITHUB_TOKEN=ghp_xxx...  (или передай --token ghp_xxx...)
_TOKEN = ""
# ──────────────────────────────────────────────────────────────────────────────



def get_rate_limit(token: str | None = None) -> dict:
    url = "https://api.github.com/rate_limit"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "PTM-RateLimit-Check/1.0",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            rate_headers = {
                "limit": resp.headers.get("X-RateLimit-Limit"),
                "remaining": resp.headers.get("X-RateLimit-Remaining"),
                "reset": resp.headers.get("X-RateLimit-Reset"),
                "used": resp.headers.get("X-RateLimit-Used"),
            }
            return {"resources": data.get("resources", {}), "headers": rate_headers}
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"HTTP {e.code}: {body}")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)


def format_reset_time(unix_ts: int | None) -> str:
    if not unix_ts:
        return "—"
    dt = datetime.fromtimestamp(unix_ts, tz=timezone.utc)
    now = datetime.now(tz=timezone.utc)
    diff_sec = max(0, int((dt - now).total_seconds()))
    minutes, seconds = divmod(diff_sec, 60)
    return f"{dt.strftime('%H:%M:%S')} UTC (через {minutes}м {seconds}с)"


def bar(used: int, limit: int, width: int = 30) -> str:
    if limit == 0:
        return "[" + "?" * width + "]"
    filled = int(width * used / limit)
    pct = used / limit * 100
    color = ""
    if pct >= 90:
        color = "\033[91m"  # красный
    elif pct >= 70:
        color = "\033[93m"  # жёлтый
    else:
        color = "\033[92m"  # зелёный
    reset = "\033[0m"
    return f"{color}[{'█' * filled}{'░' * (width - filled)}]{reset} {pct:5.1f}%"


def main():
    parser = argparse.ArgumentParser(description="GitHub API Rate Limit checker")
    parser.add_argument("--token", help="GitHub Personal Access Token (или $GITHUB_TOKEN)")
    args = parser.parse_args()

    token = args.token or os.environ.get("GITHUB_TOKEN") or (_TOKEN if _TOKEN else None)
    if not token:
        print("⚠️  Токен не передан — анонимный режим (лимит 60 запросов/час)")
        print("   Заполни _TOKEN в скрипте, или: --token ghp_... / $env:GITHUB_TOKEN='ghp_...'\n")

    data = get_rate_limit(token)
    resources = data["resources"]

    RESOURCE_NAMES = {
        "core": "Core (REST API)",
        "search": "Search",
        "graphql": "GraphQL",
        "integration_manifest": "Integration manifest",
        "source_import": "Source import",
        "code_scanning_upload": "Code scanning upload",
        "actions_runner_registration": "Actions runner reg.",
        "scim": "SCIM",
        "dependency_snapshots": "Dependency snapshots",
        "audit_log": "Audit log",
        "code_search": "Code search",
    }

    print("=" * 65)
    print("  GitHub API Rate Limit")
    print(f"  Время проверки: {datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("=" * 65)

    for key, values in resources.items():
        limit = values.get("limit", 0)
        remaining = values.get("remaining", 0)
        used = values.get("used", limit - remaining)
        reset_ts = values.get("reset")
        name = RESOURCE_NAMES.get(key, key)

        print(f"\n  {name}")
        print(f"    Использовано: {used:>6} / {limit:<6}  Осталось: {remaining}")
        print(f"    {bar(used, limit)}")
        print(f"    Сброс: {format_reset_time(reset_ts)}")

    print("\n" + "=" * 65)

    # Совет по токену
    core = resources.get("core", {})
    if core.get("limit", 0) <= 60:
        print("\n💡 Совет: авторизуйтесь через PAT для лимита 5000/час:")
        print("   $env:GITHUB_TOKEN = 'ghp_ваш_токен'")
        print("   python scripts/github_rate_limit.py")


if __name__ == "__main__":
    main()
