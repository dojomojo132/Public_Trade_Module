# -*- coding: utf-8 -*-
"""
Находит и удаляет файлы БПО, используя git diff -z для корректной работы с кириллицей.
"""
import subprocess
import os
import pathlib
import shutil

os.chdir(r"D:\Git\Public_Trade_Module")

# Отключить экранирование путей в git
subprocess.run(["git", "config", "core.quotePath", "false"], check=True)

# Файлы, ДОБАВЛЕННЫЕ между 960be69 и c07b62c
result = subprocess.run(
    ["git", "diff", "--name-status", "--diff-filter=A", "960be69", "c07b62c", "--", "Конфигурация/"],
    capture_output=True, text=True, encoding="utf-8"
)

lines = result.stdout.strip().split("\n")
added_files = []
for line in lines:
    if not line.strip():
        continue
    parts = line.split("\t", 1)
    if len(parts) == 2 and parts[0] == "A":
        added_files.append(parts[1])

print(f"=== Файлы, ДОБАВЛЕННЫЕ при БПО ===")
print(f"Количество: {len(added_files)}")

# Показать первые 10 для проверки
for f in added_files[:10]:
    print(f"  + {f}")
if len(added_files) > 10:
    print(f"  ... и ещё {len(added_files) - 10}")

# Удаление
deleted_count = 0
not_found = 0
errors = []

for f in added_files:
    filepath = pathlib.Path(r"D:\Git\Public_Trade_Module") / f
    if filepath.exists():
        try:
            filepath.unlink()
            deleted_count += 1
        except Exception as e:
            errors.append(f"{f}: {e}")
    else:
        not_found += 1

# Удалить пустые папки
config_path = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")
empty_dirs_removed = 0
for dirpath in sorted(config_path.rglob("*"), reverse=True):
    if dirpath.is_dir():
        try:
            if not any(dirpath.iterdir()):
                dirpath.rmdir()
                empty_dirs_removed += 1
        except:
            pass

print(f"\n=== Итого ===")
print(f"Удалено файлов: {deleted_count}")
print(f"Не найдено: {not_found}")
print(f"Пустых папок удалено: {empty_dirs_removed}")
if errors:
    print(f"Ошибки: {len(errors)}")
    for e in errors:
        print(f"  ! {e}")
print("\n✓ Очистка от файлов БПО завершена!")
