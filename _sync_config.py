# -*- coding: utf-8 -*-
import pathlib
import shutil
import os

# Пути
base_config = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")
test_config = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка")

# Папки для копирования
folders_to_copy = [
    "AccumulationRegisters",
    "Catalogs", 
    "CommonModules",
    "CommonTemplates",
    "Constants",
    "DataProcessors",
    "Documents",
    "Enums",
    "InformationRegisters",
    "Languages",
    "Reports",
    "Roles",
    "Styles",
    "StyleItems",
    "Subsystems",
]

print("Синхронизация конфигурации из основной папки...")
print(f"Источник: {base_config}")
print(f"Назначение: {test_config}\n")

copied = 0
skipped = 0

for folder_name in folders_to_copy:
    src_folder = base_config / folder_name
    dst_folder = test_config / folder_name
    
    if not src_folder.exists():
        print(f"  ⚠ {folder_name}/ - не найдена в источнике")
        continue
    
    if dst_folder.exists():
        print(f"  - {folder_name}/ - уже существует (пропуск)")
        skipped += 1
        continue
    
    try:
        shutil.copytree(src_folder, dst_folder)
        print(f"  ✓ {folder_name}/ - скопирована")
        copied += 1
    except Exception as e:
        print(f"  ✗ {folder_name}/ - ошибка: {e}")

print(f"\nИтого: скопировано {copied} папок, пропущено {skipped}")
print("Синхронизация завершена!")
