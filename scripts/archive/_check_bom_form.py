# -*- coding: utf-8 -*-
import pathlib

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")

files_to_check = [
    base / "Catalogs" / "Номенклатура" / "Forms" / "ФормаГруппы" / "Ext" / "Form" / "Module.bsl",
    base / "Catalogs" / "Номенклатура" / "Forms" / "ФормаГруппы" / "Ext" / "Form.xml",
    base / "Catalogs" / "Номенклатура" / "Forms" / "ФормаГруппы.xml",
    # Reference files (existing):
    base / "Catalogs" / "Номенклатура" / "Forms" / "ФормаЭлемента" / "Ext" / "Form" / "Module.bsl",
    base / "Catalogs" / "Номенклатура" / "Forms" / "ФормаЭлемента" / "Ext" / "Form.xml",
    base / "Catalogs" / "Номенклатура" / "Forms" / "ФормаЭлемента.xml",
    base / "Catalogs" / "Номенклатура" / "Forms" / "ФормаСписка" / "Ext" / "Form.xml",
    base / "Catalogs" / "Номенклатура" / "Forms" / "ФормаСписка.xml",
]

for f in files_to_check:
    if f.exists():
        data = f.read_bytes()
        has_bom = data[:3] == b'\xef\xbb\xbf'
        print(f"  {'BOM' if has_bom else 'NO-BOM'} | {f.name} ({f.parent.parent.name}/{f.parent.name}/)")
    else:
        print(f"  MISSING | {f}")
