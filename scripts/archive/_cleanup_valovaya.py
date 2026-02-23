# -*- coding: utf-8 -*-
import pathlib
import shutil

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Reports\ВаловаяПрибыль")

# Удаляем старые папки
folders_to_remove = [
    base / "Ext",        # ObjectModule.bsl
    base / "Forms",      # ФормаОтчета и все подпапки
    base / "Templates",  # Старый Макет
]

print("=== Удаление старых файлов отчёта ВаловаяПрибыль ===\n")

for folder in folders_to_remove:
    if folder.exists():
        shutil.rmtree(folder)
        print(f"  ✓ Удалена папка: {folder.name}/")
    else:
        print(f"  - Не найдена: {folder.name}/")

print("\nГотово!")
