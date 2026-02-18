# -*- coding: utf-8 -*-
import subprocess
import os

os.chdir(r"D:\Git\Public_Trade_Module")

# Проверяем статус git после отката
result = subprocess.run(
    ["git", "status", "--short"],
    capture_output=True, text=True, encoding="utf-8"
)

lines = result.stdout.strip().split("\n")
print(f"Всего изменённых файлов: {len(lines)}")
print()

# Категоризация
modified = [l for l in lines if l.startswith(" M") or l.startswith("M ")]
added = [l for l in lines if l.startswith("A ") or l.startswith("?")]
deleted = [l for l in lines if l.startswith(" D") or l.startswith("D ")]

print(f"Изменено: {len(modified)}")
print(f"Добавлено: {len(added)}")
print(f"Удалено: {len(deleted)}")

print("\n--- Первые 50 строк ---")
for line in lines[:50]:
    print(line)
if len(lines) > 50:
    print(f"... и ещё {len(lines) - 50} файлов")
