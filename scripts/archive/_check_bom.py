# -*- coding: utf-8 -*-
"""Проверка BOM и диагностика ошибки формата потока."""
import pathlib

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")

files_to_check = [
    ROOT / "DataProcessors" / "ТестовоеЗаполнениеДанных" / "Forms" / "Форма" / "Ext" / "Form.xml",
    ROOT / "DataProcessors" / "ТестовоеЗаполнениеДанных" / "Forms" / "Форма" / "Ext" / "Form" / "Module.bsl",
    ROOT / "DataProcessors" / "ТестыРМК" / "Forms" / "Форма" / "Ext" / "Form.xml",
    ROOT / "DataProcessors" / "ТестыРМК" / "Forms" / "Форма" / "Ext" / "Form" / "Module.bsl",
    ROOT / "DataProcessors" / "ТестыРМК.xml",
    ROOT / "DataProcessors" / "ТестыРМК" / "Forms" / "Форма.xml",
]

print("=== BOM проверка ===")
for f in files_to_check:
    if not f.exists():
        print(f"  НЕТ: {f.name}")
        continue
    b = f.read_bytes()
    bom = "BOM" if b[:3] == b"\xef\xbb\xbf" else "no-BOM"
    first8 = b[:8].hex()
    name = str(f.relative_to(ROOT))
    print(f"  {bom} [{first8}] {name}")
