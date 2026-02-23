# -*- coding: utf-8 -*-
"""
Ищем ПОСТОРОННИЕ файлы в Конфигурация/Проверка/ которые:
1. Не являются стандартными для 1С (не xml, не bsl)
2. Или созданы временно скриптами
"""
import subprocess, pathlib

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")
PROVERKA = ROOT / "Конфигурация" / "Проверка"

# Шаг 1: git status --short для Проверка/
print("=== git status —— Конфигурация/Проверка/ ===")
result = subprocess.run(
    ["git", "status", "--short", "--", "Конфигурация/Проверка"],
    capture_output=True, text=True, encoding="utf-8",
    cwd=str(ROOT)
)
print(result.stdout[:3000])
if result.returncode != 0:
    print("ERR:", result.stderr[:200])

# Шаг 2: Список всех НЕ-XML/BSL файлов в Проверка/
print()
print("=== Не-XML/BSL файлы в Проверка/ ===")
for f in PROVERKA.rglob("*"):
    if f.is_file() and f.suffix.lower() not in ('.xml', '.bsl', '.mdo'):
        print(f"  {f.relative_to(PROVERKA)} ({f.stat().st_size}b)")

# Шаг 3: Список НОВЫХ (untracked или ? в git status) файлов
print()
print("=== Untracked файлы в Конфигурация/ ===")
result2 = subprocess.run(
    ["git", "status", "--short", "--", "Конфигурация"],
    capture_output=True, text=True, encoding="utf-8",
    cwd=str(ROOT)
)
for line in result2.stdout.splitlines():
    if line.startswith("?? ") or line.startswith(" ? ") or "?" in line[:3]:
        print(f"  UNTRACKED: {line}")
    elif line.strip():
        print(f"  {line}")

# Шаг 4: Список папок с необычными именами
print()
print("=== Папки в Проверка/ ===")
top_dirs = sorted([f.name for f in PROVERKA.iterdir() if f.is_dir()])
print(f"  Папки верхнего уровня ({len(top_dirs)}): {top_dirs}")

# Шаг 5: Проверяем ТестыРМК структуру
tests_dir = PROVERKA / "DataProcessors" / "ТестыРМК"
print()
print(f"=== ТестыРМК структура ({tests_dir}) ===")
if tests_dir.exists():
    for f in sorted(tests_dir.rglob("*")):
        if f.is_file():
            b = f.read_bytes()
            bom = "BOM✓" if b[:3] == b'\xef\xbb\xbf' else "BOM✗"
            crlf = b.count(b'\r\n')
            lf = b.count(b'\n')
            print(f"  {f.relative_to(tests_dir)}: {len(b)}b {bom} CRLF={crlf} LF={lf}")
else:
    print("  Папка не найдена!")
