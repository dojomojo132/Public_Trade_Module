# -*- coding: utf-8 -*-
"""Check if ConfigDumpInfo.xml exists in Проверка and try to find what's different"""
import pathlib

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка")

cdi = base / "ConfigDumpInfo.xml"
print(f"ConfigDumpInfo.xml exists: {cdi.exists()}")
if cdi.exists():
    data = cdi.read_bytes()
    print(f"  Size: {len(data)} bytes")
    text = cdi.read_text(encoding="utf-8-sig")
    # Check for ФормаГруппы
    if "ФормаГруппы" in text:
        print("  Contains ФормаГруппы: YES")
    else:
        print("  Contains ФормаГруппы: NO")
    if "ФормаЭлемента" in text:
        print("  Contains ФормаЭлемента: YES")
    if "ФормаСписка" in text:
        print("  Contains ФормаСписка: YES")

# Also check Конфигурация version
cdi2 = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\ConfigDumpInfo.xml")
print(f"\nConfigDumpInfo.xml in Конфигурация: {cdi2.exists()}")

# Check if there's any difference in the file trees
print("\n--- ALL files in ФормаГруппы directory ---")
fg_dir = base / "Catalogs" / "Номенклатура" / "Forms" / "ФормаГруппы"
if fg_dir.exists():
    for f in sorted(fg_dir.rglob("*")):
        print(f"  {f.relative_to(fg_dir)} ({'DIR' if f.is_dir() else f'{f.stat().st_size} bytes'})")
else:
    print("  DIRECTORY MISSING!")

# Check ФормаЭлемента directory for comparison
print("\n--- ALL files in ФормаЭлемента directory ---")
fe_dir = base / "Catalogs" / "Номенклатура" / "Forms" / "ФормаЭлемента"
if fe_dir.exists():
    for f in sorted(fe_dir.rglob("*")):
        print(f"  {f.relative_to(fe_dir)} ({'DIR' if f.is_dir() else f'{f.stat().st_size} bytes'})")

# Check UUID collision
print("\n--- UUID collision check ---")
import re
target_uuid = "b96d6d98-dfdc-4fa7-9250-48fd8d13eae7"
found = []
for xml_file in base.rglob("*.xml"):
    try:
        text = xml_file.read_text(encoding="utf-8-sig")
        if target_uuid in text:
            found.append(str(xml_file.relative_to(base)))
    except:
        pass
print(f"UUID {target_uuid} found in:")
for f in found:
    print(f"  {f}")
