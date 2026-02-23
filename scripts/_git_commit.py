# -*- coding: utf-8 -*-
"""
Git commit helper — обходит проблему кириллицы в PowerShell.

Workflow использования агентом:
  1. Написать сообщение коммита в файл scripts/_commit_msg.txt (через create_file)
  2. Запустить: python scripts\\_git_commit.py

Файл _commit_msg.txt сохраняется в UTF-8 через create_file, PowerShell его не повреждает.
"""
import subprocess
import pathlib
import sys
import os

ROOT = pathlib.Path(__file__).parent.parent  # D:\Git\Public_Trade_Module
MSG_FILE = ROOT / "scripts" / "_commit_msg.txt"

def run(cmd, **kwargs):
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", **kwargs)
    if result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())
    return result.returncode

def main():
    os.chdir(ROOT)

    # Прочитать сообщение коммита
    if not MSG_FILE.exists():
        print(f"[ОШИБКА] Файл сообщения не найден: {MSG_FILE}")
        print("Создайте файл scripts/_commit_msg.txt с текстом коммита")
        sys.exit(1)

    message = MSG_FILE.read_text(encoding="utf-8").strip()
    if not message:
        print("[ОШИБКА] Файл _commit_msg.txt пустой")
        sys.exit(1)

    print(f"=== Git commit ===")
    print(f"Сообщение: {message}")
    print()

    # git add -A
    print("--- git add -A ---")
    code = run(["git", "add", "-A"])
    if code != 0:
        print("[ОШИБКА] git add завершился с ошибкой")
        sys.exit(code)

    # git commit
    print("--- git commit ---")
    code = run(["git", "commit", "-m", message])
    if code != 0:
        print("[ИНФО] Нечего коммитить или ошибка")
        # Не прерываем — может уже всё добавлено

    # git push
    print("--- git push ---")
    code = run(["git", "push"])
    if code != 0:
        print("[ОШИБКА] git push завершился с ошибкой")
        sys.exit(code)

    print()
    print("=== Готово ===")

    # Очистить файл после успешного коммита
    MSG_FILE.write_text("", encoding="utf-8")

if __name__ == "__main__":
    main()
