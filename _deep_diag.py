# -*- coding: utf-8 -*-
"""Deep diagnosis: compare working forms vs broken ФормаГруппы"""
import pathlib
import hashlib

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Catalogs\Номенклатура\Forms")

forms = ["ФормаЭлемента", "ФормаСписка", "ФормаГруппы"]

print("=" * 70)
print("1. FILE TREE FOR EACH FORM")
print("=" * 70)
for form in forms:
    form_dir = base / form
    print(f"\n--- {form} ---")
    if not (base / f"{form}.xml").exists():
        print(f"  DESCRIPTOR: MISSING!")
    else:
        desc = base / f"{form}.xml"
        data = desc.read_bytes()
        print(f"  DESCRIPTOR: {desc.name} ({len(data)} bytes, BOM={'YES' if data[:3]==b'\\xef\\xbb\\xbf' else 'NO'}, MD5={hashlib.md5(data).hexdigest()})")
    
    if form_dir.exists():
        for f in sorted(form_dir.rglob("*")):
            if f.is_file():
                data = f.read_bytes()
                rel = f.relative_to(base)
                print(f"  {rel} ({len(data)} bytes, BOM={'YES' if data[:3]==b'\\xef\\xbb\\xbf' else 'NO'})")
    else:
        print(f"  DIRECTORY: MISSING!")

print("\n" + "=" * 70)
print("2. DESCRIPTOR COMPARISON (hex first 200 bytes)")
print("=" * 70)
for form in forms:
    desc = base / f"{form}.xml"
    if desc.exists():
        data = desc.read_bytes()
        print(f"\n--- {form}.xml (first 200 bytes hex) ---")
        for i in range(0, min(200, len(data)), 16):
            hex_str = " ".join(f"{b:02x}" for b in data[i:i+16])
            ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in data[i:i+16])
            print(f"  {i:04d}: {hex_str:<48} {ascii_str}")

print("\n" + "=" * 70)
print("3. DESCRIPTOR XML CONTENT")
print("=" * 70)
for form in forms:
    desc = base / f"{form}.xml"
    if desc.exists():
        text = desc.read_text(encoding="utf-8-sig")
        print(f"\n--- {form}.xml ---")
        print(text)

print("\n" + "=" * 70)
print("4. Form.xml FIRST 30 LINES")
print("=" * 70)
for form in forms:
    fxml = base / form / "Ext" / "Form.xml"
    if fxml.exists():
        lines = fxml.read_text(encoding="utf-8-sig").splitlines()
        print(f"\n--- {form}/Ext/Form.xml (first 30 lines) ---")
        for i, line in enumerate(lines[:30], 1):
            print(f"  {i:3d}: {line}")
    else:
        print(f"\n--- {form}/Ext/Form.xml: MISSING ---")

print("\n" + "=" * 70)
print("5. CHECK OWNER UUIDs")
print("=" * 70)
import re
# Читаем UUID каталога Номенклатура
nom_xml = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Catalogs\Номенклатура.xml")
nom_text = nom_xml.read_text(encoding="utf-8-sig")
cat_uuid_match = re.search(r'<Catalog uuid="([^"]+)"', nom_text)
if cat_uuid_match:
    print(f"Catalog UUID: {cat_uuid_match.group(1)}")

for form in forms:
    desc = base / f"{form}.xml"
    if desc.exists():
        text = desc.read_text(encoding="utf-8-sig")
        uuid_match = re.search(r'uuid="([^"]+)"', text)
        owner_match = re.search(r'owner="([^"]+)"', text)
        print(f"  {form}: uuid={uuid_match.group(1) if uuid_match else 'N/A'}, owner={owner_match.group(1) if owner_match else 'N/A'}")

print("\n" + "=" * 70)
print("6. LINE ENDINGS CHECK")
print("=" * 70)
for form in forms:
    desc = base / f"{form}.xml"
    if desc.exists():
        data = desc.read_bytes()
        crlf_count = data.count(b"\r\n")
        lf_only = data.count(b"\n") - crlf_count
        cr_only = data.count(b"\r") - crlf_count
        print(f"  {form}.xml: CRLF={crlf_count}, LF-only={lf_only}, CR-only={cr_only}")
    
    fxml = base / form / "Ext" / "Form.xml"
    if fxml.exists():
        data = fxml.read_bytes()
        crlf_count = data.count(b"\r\n")
        lf_only = data.count(b"\n") - crlf_count
        cr_only = data.count(b"\r") - crlf_count
        print(f"  {form}/Ext/Form.xml: CRLF={crlf_count}, LF-only={lf_only}, CR-only={cr_only}")
