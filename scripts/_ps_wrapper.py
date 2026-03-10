# -*- coding: utf-8 -*-
"""
Универсальный Python-wrapper для вызова PowerShell-скриптов с кириллическими путями.

Решает проблему: PowerShell в VS Code терминале ломает кириллицу в путях из-за
рассогласования кодировок (cp866 OEM vs cp1251 vs UTF-8).

Использование:
    python scripts/_ps_wrapper.py deploy -Action Full
    python scripts/_ps_wrapper.py deploy -Action Dump
    python scripts/_ps_wrapper.py deploy -Action Load
    python scripts/_ps_wrapper.py deploy -Action Rollback
    python scripts/_ps_wrapper.py deploy -Action Info
    python scripts/_ps_wrapper.py deploy -Action Designer
    python scripts/_ps_wrapper.py validate
    python scripts/_ps_wrapper.py monitor -Action Check -LastMinutes 5
    python scripts/_ps_wrapper.py monitor -Action Setup
"""
import subprocess
import sys
import pathlib
import base64
import os

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "Документация" / "Валидация"

SCRIPT_MAP = {
    "deploy": SCRIPTS_DIR / "deploy-config.ps1",
    "validate": SCRIPTS_DIR / "validate-config.ps1",
    "monitor": SCRIPTS_DIR / "monitor-errors.ps1",
}


def _quote_ps_arg(arg: str) -> str:
    """Оборачивает аргумент в кавычки если содержит пробелы или кириллицу."""
    if arg.startswith("-"):
        return arg  # PS-параметр типа -Action, -User — без кавычек
    # Значение параметра — оборачиваем в одинарные кавычки
    if " " in arg or any(ord(c) > 127 for c in arg):
        return f"'{arg}'"
    return arg


def run_ps_script(script_path: pathlib.Path, extra_args: list[str]) -> int:
    """Вызывает PS-скрипт через -EncodedCommand (Base64 UTF-16LE).

    Это единственный надёжный способ передать кириллические пути в PowerShell
    из subprocess — минуя все проблемы с кодировками терминала.
    """

    if not script_path.exists():
        print(f"ОШИБКА: Скрипт не найден: {script_path}", file=sys.stderr)
        return 1

    args_str = " ".join(_quote_ps_arg(a) for a in extra_args) if extra_args else ""

    # PowerShell-команда с принудительным UTF-8 выводом
    ps_command = (
        '[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; '
        '[Console]::InputEncoding  = [System.Text.Encoding]::UTF8; '
        '$OutputEncoding = [System.Text.Encoding]::UTF8; '
        f'& "{script_path}" {args_str}; '
        'exit $LASTEXITCODE'
    )

    # Кодируем в Base64 UTF-16LE для -EncodedCommand
    encoded = base64.b64encode(ps_command.encode("utf-16-le")).decode("ascii")

    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-EncodedCommand", encoded,
        ],
        cwd=str(PROJECT_ROOT),
    )
    return result.returncode


def main():
    if len(sys.argv) < 2:
        print("Использование: python scripts/_ps_wrapper.py <deploy|validate|monitor> [аргументы PS-скрипта]")
        print()
        print("Примеры:")
        print("  python scripts/_ps_wrapper.py deploy -Action Full")
        print("  python scripts/_ps_wrapper.py deploy -Action Dump")
        print("  python scripts/_ps_wrapper.py deploy -Action Rollback")
        print("  python scripts/_ps_wrapper.py validate")
        print("  python scripts/_ps_wrapper.py monitor -Action Check -LastMinutes 5")
        sys.exit(1)

    script_name = sys.argv[1].lower()
    extra_args = sys.argv[2:]

    if script_name not in SCRIPT_MAP:
        print(f"ОШИБКА: Неизвестный скрипт '{script_name}'. Доступные: {', '.join(SCRIPT_MAP.keys())}")
        sys.exit(1)

    # Подхватываем учётные данные из .env если -User не передан явно
    if script_name == "deploy" and "-User" not in extra_args:
        env_file = PROJECT_ROOT / ".env"
        if env_file.exists():
            env_vars = {}
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, val = line.partition("=")
                    env_vars[key.strip()] = val.strip()
            user = env_vars.get("PTM_1C_USER", "")
            password = env_vars.get("PTM_1C_PASSWORD", "")
            if user:
                extra_args = ["-User", user] + (["-Password", password] if password else []) + extra_args

    script_path = SCRIPT_MAP[script_name]
    exit_code = run_ps_script(script_path, extra_args)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
