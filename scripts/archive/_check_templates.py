# -*- coding: utf-8 -*-
"""Check which CommonTemplate files are expected by ConfigDumpInfo.xml but missing on disk."""
import xml.etree.ElementTree as ET
import pathlib

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")
CDI = ROOT / "Конфигурация" / "ConfigDumpInfo.xml"
CT_DIR = ROOT / "Конфигурация" / "CommonTemplates"

tree = ET.parse(CDI)
root = tree.getroot()
ns = root.tag.split('}')[0] + '}' if '}' in root.tag else ''

expected = set()
for md in root.iter(f'{ns}Metadata'):
    name = md.text if md.text else md.get('name', '')
    if 'CommonTemplate.' in name:
        tpl_name = name.split('CommonTemplate.')[-1]
        expected.add(tpl_name)

# Check what's actually on disk (XML files)
on_disk = set()
if CT_DIR.exists():
    for f in CT_DIR.iterdir():
        if f.suffix == '.xml' and f.is_file():
            on_disk.add(f.stem)

missing = expected - on_disk
extra = on_disk - expected

print(f"Expected by CDI: {len(expected)}")
print(f"On disk:         {len(on_disk)}")
print(f"Missing:         {len(missing)}")
print(f"Extra:           {len(extra)}")

if missing:
    print("\n--- Missing files ---")
    for m in sorted(missing)[:20]:
        print(f"  {m}")
    if len(missing) > 20:
        print(f"  ... and {len(missing) - 20} more")

if extra:
    print("\n--- Extra files (on disk but not in CDI) ---")
    for e in sorted(extra)[:10]:
        print(f"  {e}")
