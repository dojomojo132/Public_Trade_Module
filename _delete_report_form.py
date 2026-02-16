# -*- coding: utf-8 -*-
import pathlib
import shutil

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")

# Папки для удаления (Forms целиком)
folders = [
    base / "Reports" / "Взаиморасчеты" / "Forms",
    base / "Проверка" / "Reports" / "Взаиморасчеты" / "Forms",
]

print("Удаление папок Forms отчёта Взаиморасчеты...")
for folder in folders:
    if folder.exists():
        shutil.rmtree(folder)
        print(f"  ✓ {folder}")
    else:
        print(f"  - {folder} (не найдена)")

print("\nГотово!")
