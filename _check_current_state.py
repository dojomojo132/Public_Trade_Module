# -*- coding: utf-8 -*-
"""Check CURRENT state of all ФормаГруппы files"""
import pathlib

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Catalogs\Номенклатура\Forms")

# Check descriptor
desc = base / "ФормаГруппы.xml"
print(f"=== DESCRIPTOR: {desc.name} ===")
if desc.exists():
    data = desc.read_bytes()
    print(f"Size: {len(data)} bytes")
    print(f"First 20 bytes hex: {' '.join(f'{b:02x}' for b in data[:20])}")
    try:
        text = data.decode('utf-8-sig')
        print(f"Content:\n{text}")
    except:
        print("DECODE ERROR!")
        print(f"Raw bytes: {data[:500]}")
else:
    print("FILE MISSING!")

# Check Form.xml
fxml = base / "ФормаГруппы" / "Ext" / "Form.xml"
print(f"\n=== FORM.XML ===")
if fxml.exists():
    data = fxml.read_bytes()
    print(f"Size: {len(data)} bytes")
    print(f"First 20 bytes hex: {' '.join(f'{b:02x}' for b in data[:20])}")
else:
    print("FILE MISSING!")

# Check Module.bsl
mod = base / "ФормаГруппы" / "Ext" / "Form" / "Module.bsl"
print(f"\n=== MODULE.BSL ===")
if mod.exists():
    data = mod.read_bytes()
    print(f"Size: {len(data)} bytes")
else:
    print("FILE MISSING!")

# Also check: list ALL directories in Forms/
print(f"\n=== ALL entries in Forms/ ===")
if base.exists():
    for entry in sorted(base.iterdir()):
        kind = "DIR" if entry.is_dir() else f"FILE ({entry.stat().st_size} bytes)"
        print(f"  {entry.name}  [{kind}]")

# Check if maybe 1C created a ConfigDumpInfo
cdi = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\ConfigDumpInfo.xml")
print(f"\nConfigDumpInfo.xml: {'EXISTS' if cdi.exists() else 'MISSING'}")
