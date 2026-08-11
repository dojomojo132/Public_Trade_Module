# -*- coding: utf-8 -*-
"""
Применяет профиль MCP к project-config.yml и перегенерирует конфиги Grok/Cursor.
Опционально включает/выключает глобальные плагины Grok.

Запуск:
  python scripts/mcp_apply_profile.py standard
  python scripts/mcp_apply_profile.py minimal --no-plugins
  python scripts/mcp_apply_profile.py --list
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

PROJ_ROOT = Path(__file__).resolve().parent.parent
PROFILES_FILE = Path(__file__).resolve().parent / "mcp_profiles.yml"
CONFIG_FILE = PROJ_ROOT / ".github" / "project-config.yml"
ACTIVE_PROFILE_FILE = PROJ_ROOT / ".grok" / "mcp-profile.active"

SERVER_KEYS = ("context", "dev", "tg_dashboard", "configurator", "debug")
_RESERVED_KEYS = frozenset({"servers", "plugins", "enable", "disable", "description", "profiles"})


def _parse_profiles(text: str) -> tuple[str, dict[str, dict]]:
    default = "standard"
    profiles: dict[str, dict] = {}
    current: str | None = None
    section: str | None = None
    in_plugins = False
    list_target: str | None = None

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("default:"):
            default = line.split(":", 1)[1].strip()
            continue
        if line == "profiles:":
            continue
        if re.match(r"^[a-z][a-z0-9_-]*:$", line):
            candidate = line[:-1]
            if candidate in _RESERVED_KEYS:
                if candidate == "servers":
                    section = "servers"
                    in_plugins = False
                    list_target = None
                elif candidate == "plugins":
                    section = "plugins"
                    in_plugins = True
                    list_target = None
                elif candidate == "enable" and in_plugins:
                    list_target = "enable"
                elif candidate == "disable" and in_plugins:
                    list_target = "disable"
                continue
            current = candidate
            profiles[current] = {"description": "", "servers": {}, "plugins": {"enable": [], "disable": []}}
            section = None
            in_plugins = False
            list_target = None
            continue
        if current is None:
            continue
        if line.startswith("description:"):
            profiles[current]["description"] = line.split(":", 1)[1].strip().strip('"')
            continue
        if line == "servers:":
            section = "servers"
            in_plugins = False
            continue
        if line == "plugins:":
            section = "plugins"
            in_plugins = True
            continue
        if in_plugins and line.startswith("enable:"):
            list_target = "enable"
            rest = line.split(":", 1)[1].strip()
            if rest.startswith("["):
                profiles[current]["plugins"]["enable"] = _parse_inline_list(rest)
                list_target = None
            continue
        if in_plugins and line.startswith("disable:"):
            list_target = "disable"
            rest = line.split(":", 1)[1].strip()
            if rest.startswith("["):
                profiles[current]["plugins"]["disable"] = _parse_inline_list(rest)
                list_target = None
            continue
        if in_plugins and line.startswith("- ") and list_target:
            profiles[current]["plugins"][list_target].append(line[2:].strip())
            continue
        if section == "servers" and ":" in line:
            key, _, val = line.partition(":")
            profiles[current]["servers"][key.strip()] = val.strip().lower() == "true"

    return default, profiles


def _parse_inline_list(value: str) -> list[str]:
    inner = value.strip("[]")
    if not inner.strip():
        return []
    return [item.strip().strip('"').strip("'") for item in inner.split(",") if item.strip()]


def _load_profiles() -> tuple[str, dict[str, dict]]:
    text = PROFILES_FILE.read_text(encoding="utf-8")
    return _parse_profiles(text)


def _set_server_enabled(config_text: str, server_key: str, enabled: bool) -> str:
    flag = "true" if enabled else "false"
    pattern = (
        rf"(^  {re.escape(server_key)}:\s*\n"
        rf"(?:    .+\n)*?"
        rf"    enabled:\s*)(true|false)"
    )
    new_text, count = re.subn(pattern, rf"\g<1>{flag}", config_text, count=1, flags=re.MULTILINE)
    if count == 0:
        raise RuntimeError(f"Не найден блок mcp.{server_key}.enabled в {CONFIG_FILE}")
    return new_text


def apply_servers(profile_servers: dict[str, bool]) -> None:
    text = CONFIG_FILE.read_text(encoding="utf-8")
    for key in SERVER_KEYS:
        if key not in profile_servers:
            raise RuntimeError(f"Профиль не задаёт servers.{key}")
        text = _set_server_enabled(text, key, bool(profile_servers[key]))
    CONFIG_FILE.write_text(text, encoding="utf-8")


def regenerate_mcp_configs() -> None:
    subprocess.run(
        [sys.executable, str(PROJ_ROOT / "scripts" / "_generate_mcp.py")],
        cwd=str(PROJ_ROOT),
        check=True,
    )


def apply_plugins(profile_plugins: dict[str, list[str]], skip_plugins: bool) -> None:
    if skip_plugins:
        print("  INFO  Плагины Grok не трогали (--no-plugins)")
        return
    for name in profile_plugins.get("disable", []):
        _run_grok_plugin("disable", name)
    for name in profile_plugins.get("enable", []):
        _run_grok_plugin("enable", name)


def _run_grok_plugin(action: str, name: str) -> None:
    result = subprocess.run(
        ["grok", "plugin", action, name],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode == 0:
        print(f"  OK    grok plugin {action} {name}")
        return
    stderr = (result.stderr or "").strip()
    stdout = (result.stdout or "").strip()
    msg = stderr or stdout or f"exit {result.returncode}"
    print(f"  WARN  grok plugin {action} {name}: {msg}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Применить MCP-профиль проекта")
    parser.add_argument("profile", nargs="?", help="minimal | standard | debug | full | extras")
    parser.add_argument("--list", action="store_true", help="Показать профили")
    parser.add_argument("--no-plugins", action="store_true", help="Не менять глобальные плагины Grok")
    parser.add_argument("--no-generate", action="store_true", help="Только project-config.yml, без _generate_mcp.py")
    args = parser.parse_args()

    default, profiles = _load_profiles()
    if args.list:
        print(f"default: {default}")
        for name, cfg in profiles.items():
            desc = cfg.get("description", "")
            servers = ", ".join(f"{k}={'on' if v else 'off'}" for k, v in cfg["servers"].items())
            print(f"  {name}: {desc}")
            print(f"    servers: {servers}")
        return 0

    profile_name = args.profile or default
    if profile_name not in profiles:
        print(f"Неизвестный профиль: {profile_name}. Доступны: {', '.join(profiles)}", file=sys.stderr)
        return 1

    profile = profiles[profile_name]
    print(f"Профиль: {profile_name} — {profile.get('description', '')}")
    apply_servers(profile["servers"])
    print(f"  OK    {CONFIG_FILE.name} обновлён")

    if not args.no_generate:
        regenerate_mcp_configs()

    ACTIVE_PROFILE_FILE.parent.mkdir(parents=True, exist_ok=True)
    ACTIVE_PROFILE_FILE.write_text(profile_name + "\n", encoding="utf-8")
    print(f"  OK    {ACTIVE_PROFILE_FILE}")

    apply_plugins(profile.get("plugins", {}), skip_plugins=args.no_plugins)
    print("Готово. Запускайте Grok из корня этого проекта (scripts/Start-Grok.ps1).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())