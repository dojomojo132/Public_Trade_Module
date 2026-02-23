# -*- coding: utf-8 -*-
"""
Находит и удаляет файлы, которые были добавлены при внедрении БПО.
git checkout не удаляет новые файлы - нужно сделать это вручную.
"""
import subprocess
import os
import pathlib
import shutil

os.chdir(r"D:\Git\Public_Trade_Module")

# Файлы, ДОБАВЛЕННЫЕ между 960be69 и c07b62c (HEAD до отката)
# Формат: A\tfilename
result = subprocess.run(
    ["git", "diff", "--name-status", "960be69", "c07b62c", "--", "Конфигурация/"],
    capture_output=True, text=True, encoding="utf-8"
)

lines = result.stdout.strip().split("\n")
added_files = []
for line in lines:
    if line.startswith("A\t"):
        added_files.append(line.split("\t", 1)[1])

print(f"=== Файлы, ДОБАВЛЕННЫЕ при БПО (будут удалены) ===")
print(f"Количество: {len(added_files)}")

deleted_count = 0
not_found = 0

for f in added_files:
    filepath = pathlib.Path(r"D:\Git\Public_Trade_Module") / f
    print(f"  {f}")
    if filepath.exists():
        filepath.unlink()
        deleted_count += 1
        print(f"    ✓ Удалён")
    else:
        not_found += 1
        print(f"    - Не найден (уже удалён?)")

# Удалить пустые папки, оставшиеся после удаления файлов
config_path = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")
empty_dirs_removed = 0
for dirpath in sorted(config_path.rglob("*"), reverse=True):
    if dirpath.is_dir() and not any(dirpath.iterdir()):
        dirpath.rmdir()
        empty_dirs_removed += 1
        print(f"  ✓ Пустая папка удалена: {dirpath.name}/")

print(f"\n=== Итого ===")
print(f"Удалено файлов: {deleted_count}")
print(f"Не найдено: {not_found}")
print(f"Пустых папок удалено: {empty_dirs_removed}")
