# -*- coding: utf-8 -*-
"""Добавление UTF-8 BOM ко всем новым файлам ТестыРМК в обеих папках."""
import pathlib

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")
CONFIGS = [
    ROOT / "Конфигурация",
    ROOT / "Конфигурация" / "Проверка",
]

BOM = b"\xef\xbb\xbf"

files_to_fix = [
    "DataProcessors/ТестыРМК.xml",
    "DataProcessors/ТестыРМК/Forms/Форма.xml",
    "DataProcessors/ТестыРМК/Forms/Форма/Ext/Form.xml",
    "DataProcessors/ТестыРМК/Forms/Форма/Ext/Form/Module.bsl",
]

print("=== Добавление BOM ===")
for cfg in CONFIGS:
    for rel in files_to_fix:
        p = cfg / rel.replace("/", "\\")
        if not p.exists():
            print(f"  НЕТ: {p.relative_to(ROOT)}")
            continue
        data = p.read_bytes()
        if data[:3] == BOM:
            print(f"  SKIP (уже есть BOM): {p.relative_to(ROOT)}")
        else:
            p.write_bytes(BOM + data)
            print(f"  OK (добавлен BOM): {p.relative_to(ROOT)}")

print()
print("=== ГОТОВО ===")
