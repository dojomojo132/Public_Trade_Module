# -*- coding: utf-8 -*-
"""Check for duplicate UUIDs and Configuration.xml differences."""
import pathlib
import xml.etree.ElementTree as ET
import re
from collections import defaultdict

BASE = pathlib.Path(r'D:\Git\Public_Trade_Module\Конфигурация\Проверка')
NS_CDI = '{http://v8.1c.ru/8.3/xcf/dumpinfo}'
NS_MD = '{http://v8.1c.ru/8.3/MDClasses}'

# ============================================================
# CHECK 1: Duplicate UUIDs in CDI
# ============================================================
print("=" * 70)
print("CHECK 1: Duplicate UUIDs in CDI")
print("=" * 70)

cdi = ET.parse(str(BASE / 'ConfigDumpInfo.xml'))
uuid_to_names = defaultdict(list)
for elem in cdi.getroot().iter(NS_CDI + 'Metadata'):
    name = elem.get('name', '')
    mid = elem.get('id', '')
    if mid:
        uuid_to_names[mid].append(name)

dupes = {k: v for k, v in uuid_to_names.items() if len(v) > 1}
if dupes:
    for uid, names in sorted(dupes.items()):
        print(f"  DUPLICATE UUID {uid}:")
        for n in names:
            print(f"    - {n}")
else:
    print("  No duplicate UUIDs in CDI")

# ============================================================
# CHECK 2: Duplicate UUIDs across ALL XML files
# ============================================================
print()
print("=" * 70)
print("CHECK 2: Duplicate UUIDs across all XML metadata files")
print("=" * 70)

uuid_sources = defaultdict(list)

# Scan all XML files for uuid= attributes
uuid_pattern = re.compile(r'uuid="([a-f0-9-]+)"', re.IGNORECASE)

for xml_file in BASE.rglob('*.xml'):
    if xml_file.name in ('ConfigDumpInfo.xml', 'Configuration.xml'):
        continue
    if 'Form.xml' in str(xml_file) and 'Ext' in str(xml_file):
        continue  # Skip form content XMLs - they don't have metadata UUIDs
    
    try:
        content = xml_file.read_text(encoding='utf-8')
        for match in uuid_pattern.finditer(content):
            uid = match.group(1).lower()
            rel_path = str(xml_file.relative_to(BASE))
            uuid_sources[uid].append(rel_path)
    except Exception:
        pass

dupes2 = {k: v for k, v in uuid_sources.items() if len(v) > 1 and not k.endswith('.0')}
if dupes2:
    print(f"  Found {len(dupes2)} duplicate UUIDs:")
    for uid, sources in sorted(dupes2.items()):
        # Filter: same UUID appearing in object.xml and its form descriptor is OK
        unique_sources = set(sources)
        if len(unique_sources) <= 1:
            continue
        print(f"\n  UUID: {uid}")
        for s in sorted(unique_sources):
            print(f"    - {s}")
else:
    print("  No duplicate UUIDs found")

# ============================================================
# CHECK 3: Compare Configuration.xml ChildObjects
# ============================================================
print()
print("=" * 70)
print("CHECK 3: Configuration.xml differences")
print("=" * 70)

orig_conf = pathlib.Path(r'D:\Git\Public_Trade_Module\Конфигурация\Configuration.xml')
work_conf = BASE / 'Configuration.xml'

# Extract ChildObjects entries from both
def get_child_objects(conf_path):
    tree = ET.parse(str(conf_path))
    root = tree.getroot()
    children = {}
    for elem in root.iter():
        tag = elem.tag.replace(NS_MD, '')
        if tag in ('Document', 'Catalog', 'DataProcessor', 'Report', 'Enum',
                    'CommonModule', 'AccumulationRegister', 'InformationRegister',
                    'Constant', 'Subsystem', 'Role', 'Language', 'CommonTemplate',
                    'CommonPicture', 'StyleItem', 'Style'):
            if elem.text:
                children.setdefault(tag, []).append(elem.text)
    return children

orig_children = get_child_objects(orig_conf)
work_children = get_child_objects(work_conf)

all_tags = set(list(orig_children.keys()) + list(work_children.keys()))
for tag in sorted(all_tags):
    orig_set = set(orig_children.get(tag, []))
    work_set = set(work_children.get(tag, []))
    added = work_set - orig_set
    removed = orig_set - work_set
    if added:
        for a in sorted(added):
            print(f"  + [{tag}] {a}")
    if removed:
        for r in sorted(removed):
            print(f"  - [{tag}] {r}")

if not any(set(work_children.get(t, [])) != set(orig_children.get(t, [])) for t in all_tags):
    print("  No differences in ChildObjects")

# ============================================================
# CHECK 4: InternalInfo presence in key XML files  
# ============================================================
print()
print("=" * 70)
print("CHECK 4: Objects missing InternalInfo/xr:GeneratedType")
print("=" * 70)

for obj_type in ['Documents', 'DataProcessors', 'Catalogs']:
    type_dir = BASE / obj_type
    if not type_dir.exists():
        continue
    for xml_file in type_dir.glob('*.xml'):
        if not xml_file.is_file():
            continue
        content = xml_file.read_text(encoding='utf-8')
        has_internal_info = 'InternalInfo' in content
        has_generated_type = 'GeneratedType' in content
        
        if not has_internal_info and not has_generated_type:
            print(f"  MISSING InternalInfo: {obj_type}/{xml_file.name}")
        elif has_internal_info and not has_generated_type:
            print(f"  MISSING GeneratedType (has InternalInfo): {obj_type}/{xml_file.name}")

print("  Check complete")
