# -*- coding: utf-8 -*-
"""Delete orphan report СправочникНоменклатуры from both Конфигурация and Проверка"""
import pathlib
import shutil

BASE = pathlib.Path(r"D:\Git\Public_Trade_Module")

files = [
    BASE / "Конфигурация" / "Reports" / "СправочникНоменклатуры.xml",
    BASE / "Конфигурация" / "Проверка" / "Reports" / "СправочникНоменклатуры.xml",
]

folders = [
    BASE / "Конфигурация" / "Reports" / "СправочникНоменклатуры",
    BASE / "Конфигурация" / "Проверка" / "Reports" / "СправочникНоменклатуры",
]

print("Удаление файлов...")
for f in files:
    if f.exists():
        f.unlink()
        print(f"  OK {f.name}")
    else:
        print(f"  - {f.name} (не найден)")

print("\nУдаление папок...")
for folder in folders:
    if folder.exists():
        shutil.rmtree(folder)
        print(f"  OK {folder.name}/")
    else:
        print(f"  - {folder.name}/ (не найдена)")

print("\nГотово!")
