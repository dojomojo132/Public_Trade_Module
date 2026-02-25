# -*- coding: utf-8 -*-
"""Синхронизация ПриходТовара в Проверка/"""
import pathlib
import shutil

root = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")
proverka = root / "Проверка"

files = [
    "Documents/ПриходТовара/Forms/ФормаДокумента/Ext/Form.xml",
    "Documents/ПриходТовара/Forms/ФормаДокумента/Ext/Form/Module.bsl",
]

for rel in files:
    src = root / rel
    dst = proverka / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"  ✓ {rel}")

print("\n✓ Синхронизация ПриходТовара завершена")
