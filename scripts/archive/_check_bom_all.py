# -*- coding: utf-8 -*-
"""Check BOM for all Form.xml files and compare encoding details"""
import pathlib

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Catalogs\Номенклатура\Forms")

forms = ["ФормаЭлемента", "ФормаСписка", "ФормаГруппы"]

print("=== BOM CHECK FOR Form.xml FILES ===\n")
for form in forms:
    fxml = base / form / "Ext" / "Form.xml"
    if fxml.exists():
        data = fxml.read_bytes()
        has_bom = data[:3] == b'\xef\xbb\xbf'
        print(f"{form}/Ext/Form.xml:")
        print(f"  Size: {len(data)} bytes")
        print(f"  BOM: {'YES' if has_bom else 'NO'}")
        print(f"  First 3 bytes: {data[0]:02x} {data[1]:02x} {data[2]:02x}")
        
        # Check if tabs or spaces
        text = data.decode('utf-8-sig')
        has_tabs = '\t' in text
        has_spaces_indent = '    ' in text  # 4 spaces
        print(f"  Uses tabs: {has_tabs}")
        print(f"  Uses 4-space indent: {has_spaces_indent}")
        print()

print("\n=== BOM CHECK FOR DESCRIPTORS ===\n")
for form in forms:
    desc = base / f"{form}.xml"
    if desc.exists():
        data = desc.read_bytes()
        has_bom = data[:3] == b'\xef\xbb\xbf'
        print(f"{form}.xml: BOM={'YES' if has_bom else 'NO'}, first 3: {data[0]:02x} {data[1]:02x} {data[2]:02x}")

print("\n=== BOM CHECK FOR Module.bsl FILES ===\n")
for form in forms:
    mod = base / form / "Ext" / "Form" / "Module.bsl"
    if mod.exists():
        data = mod.read_bytes()
        has_bom = data[:3] == b'\xef\xbb\xbf'
        print(f"{form}/Module.bsl: BOM={'YES' if has_bom else 'NO'}, first 3: {data[0]:02x} {data[1]:02x} {data[2]:02x}")
