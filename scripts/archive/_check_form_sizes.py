# -*- coding: utf-8 -*-
import pathlib

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Catalogs\Номенклатура\Forms")

forms = ["ФормаЭлемента.xml", "ФормаСписка.xml", "ФормаГруппы.xml"]

print("=== FILE SIZES ===")
for name in forms:
    f = base / name
    if f.exists():
        size = f.stat().st_size
        # Check BOM
        with open(f, 'rb') as fh:
            first3 = fh.read(3)
        has_bom = first3 == b'\xef\xbb\xbf'
        print(f"  {name}: {size} bytes, BOM={has_bom}")
    else:
        print(f"  {name}: NOT FOUND!")

print("\n=== FORM.XML SIZES ===")
for name in ["ФормаЭлемента", "ФормаСписка", "ФормаГруппы"]:
    f = base / name / "Ext" / "Form.xml"
    if f.exists():
        size = f.stat().st_size
        with open(f, 'rb') as fh:
            first3 = fh.read(3)
        has_bom = first3 == b'\xef\xbb\xbf'
        print(f"  {name}/Ext/Form.xml: {size} bytes, BOM={has_bom}")
    else:
        print(f"  {name}/Ext/Form.xml: NOT FOUND!")

print("\n=== MODULE.BSL CHECK ===")
for name in ["ФормаЭлемента", "ФормаСписка", "ФормаГруппы"]:
    f = base / name / "Ext" / "Form" / "Module.bsl"
    if f.exists():
        size = f.stat().st_size
        print(f"  {name}/Ext/Form/Module.bsl: {size} bytes")
    else:
        print(f"  {name}/Ext/Form/Module.bsl: NOT FOUND!")

print("\n=== FULL RECURSIVE DIR ===")
for name in ["ФормаГруппы", "ФормаЭлемента", "ФормаСписка"]:
    d = base / name
    print(f"\n  {name}/")
    if d.exists():
        for p in sorted(d.rglob("*")):
            rel = p.relative_to(d)
            prefix = "    " if p.is_file() else "    "
            suffix = "/" if p.is_dir() else f" ({p.stat().st_size} bytes)"
            print(f"  {prefix}{rel}{suffix}")
    else:
        print(f"    NOT FOUND!")
