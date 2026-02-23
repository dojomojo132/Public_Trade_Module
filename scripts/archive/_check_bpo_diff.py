# -*- coding: utf-8 -*-
import subprocess
import os

os.chdir(r"D:\Git\Public_Trade_Module")

# Найти файлы, которые были ДОБАВЛЕНЫ между 960be69 и c07b62c (HEAD до отката)
# Эти файлы нужно УДАЛИТЬ, т.к. их не было до БПО
result = subprocess.run(
    ["git", "diff", "--name-status", "960be69", "c07b62c", "--", "Конфигурация/"],
    capture_output=True, text=True, encoding="utf-8"
)

lines = result.stdout.strip().split("\n")
added_files = [l.split("\t", 1)[1] for l in lines if l.startswith("A\t")]
deleted_files = [l.split("\t", 1)[1] for l in lines if l.startswith("D\t")]

print(f"=== Файлы, ДОБАВЛЕННЫЕ при БПО (нужно удалить) ===")
print(f"Количество: {len(added_files)}")
for f in added_files:
    print(f"  + {f}")

print(f"\n=== Файлы, УДАЛЁННЫЕ при БПО (нужно восстановить) ===")
print(f"Количество: {len(deleted_files)}")
for f in deleted_files:
    print(f"  - {f}")
