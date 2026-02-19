# -*- coding: utf-8 -*-
"""Копирует файлы ФормаСписка Номенклатуры из Конфигурация/ в Конфигурация/Проверка/"""
import pathlib
import shutil

BASE = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")
SRC  = BASE / "Catalogs" / "Номенклатура"
DST  = BASE / "Проверка" / "Catalogs" / "Номенклатура"

files = [
    ("Forms/ФормаСписка.xml",               "Forms/ФормаСписка.xml"),
    ("Forms/ФормаСписка/Ext/Form.xml",       "Forms/ФормаСписка/Ext/Form.xml"),
    ("Forms/ФормаСписка/Ext/Form/Module.bsl","Forms/ФормаСписка/Ext/Form/Module.bsl"),
]

for src_rel, dst_rel in files:
    src_path = SRC / src_rel.replace("/", "\\")
    dst_path = DST / dst_rel.replace("/", "\\")
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_path, dst_path)
    print(f"  ✓ {dst_rel}")

print("\nГотово!")
