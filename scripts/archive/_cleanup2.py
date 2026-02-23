# -*- coding: utf-8 -*-
import pathlib
import shutil

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")

# Удалить пустую сломанную папку 'окументация' (PowerShell урезал 'Документация')
broken = ROOT / "окументация"
if broken.exists():
    # Удаляем только если пустая (нет файлов)
    all_files = list(broken.rglob("*.*"))
    if not all_files:
        shutil.rmtree(str(broken))
        print(f"✓ Удалена пустая папка: окументация/")
    else:
        print(f"⚠️ Папка не пустая, не удаляем: {[str(f) for f in all_files]}")
else:
    print("- окументация/ не найдена")

# Переместить скрипт _check_folders.py в archive
src = ROOT / "_check_folders.py"
if src.exists():
    dst = ROOT / "scripts" / "archive" / "_check_folders.py"
    shutil.move(str(src), str(dst))
    print(f"✓ _check_folders.py → scripts/archive/")

print("Готово!")
