# -*- coding: utf-8 -*-
"""Check GeneratedType TypeId/ValueId uniqueness and other internal IDs."""
import pathlib
import re
from collections import defaultdict

BASE = pathlib.Path(r'D:\Git\Public_Trade_Module\Конфигурация\Проверка')

# Search all XML files for TypeId and ValueId
type_ids = defaultdict(list)
value_ids = defaultdict(list)

typeid_re = re.compile(r'<xr:TypeId>([a-f0-9-]+)</xr:TypeId>', re.IGNORECASE)
valueid_re = re.compile(r'<xr:ValueId>([a-f0-9-]+)</xr:ValueId>', re.IGNORECASE)

for xml_file in BASE.rglob('*.xml'):
    try:
        content = xml_file.read_text(encoding='utf-8')
    except:
        continue
    
    rel = str(xml_file.relative_to(BASE))
    
    for m in typeid_re.finditer(content):
        type_ids[m.group(1).lower()].append(rel)
    
    for m in valueid_re.finditer(content):
        value_ids[m.group(1).lower()].append(rel)

print("=" * 70)
print("CHECK: TypeId uniqueness")
print("=" * 70)
dup_type = {k: v for k, v in type_ids.items() if len(v) > 1}
if dup_type:
    for uid, files in sorted(dup_type.items()):
        unique = set(files)
        if len(unique) > 1:
            print(f"  DUPLICATE TypeId: {uid}")
            for f in sorted(unique):
                print(f"    - {f}")
    if not any(len(set(v)) > 1 for v in dup_type.values()):
        print("  All TypeId duplicates are within same file (OK)")
else:
    print("  All TypeIds unique")

print()
print("=" * 70)
print("CHECK: ValueId uniqueness")
print("=" * 70)
dup_val = {k: v for k, v in value_ids.items() if len(v) > 1}
if dup_val:
    for uid, files in sorted(dup_val.items()):
        unique = set(files)
        if len(unique) > 1:
            print(f"  DUPLICATE ValueId: {uid}")
            for f in sorted(unique):
                print(f"    - {f}")
    if not any(len(set(v)) > 1 for v in dup_val.values()):
        print("  All ValueId duplicates are within same file (OK)")
else:
    print("  All ValueIds unique")

print()
print(f"Total TypeIds: {len(type_ids)}")
print(f"Total ValueIds: {len(value_ids)}")

# ============================================================
# Check for any uuid= attribute that appears in multiple files
# ============================================================
print()
print("=" * 70)
print("CHECK: All uuid= attributes cross-file uniqueness")
print("=" * 70)

uuid_re = re.compile(r'uuid="([a-f0-9-]+)"', re.IGNORECASE)
uuid_files = defaultdict(set)

for xml_file in BASE.rglob('*.xml'):
    if xml_file.name == 'ConfigDumpInfo.xml':
        continue
    # Skip Form.xml inside Ext/ (they don't have uuid attrs for metadata)
    if xml_file.name == 'Form.xml' and 'Ext' in str(xml_file):
        continue
    
    try:
        content = xml_file.read_text(encoding='utf-8')
    except:
        continue
    
    rel = str(xml_file.relative_to(BASE))
    
    for m in uuid_re.finditer(content):
        uuid_files[m.group(1).lower()].add(rel)

dups = {k: v for k, v in uuid_files.items() if len(v) > 1}
for uid, files in sorted(dups.items()):
    print(f"  UUID {uid} in multiple files:")
    for f in sorted(files):
        print(f"    - {f}")

if not dups:
    print("  No cross-file UUID duplicates")

# ============================================================
# Extra: List ALL file types in the config dir
# ============================================================
print()
print("=" * 70)
print("ALL file extensions in config directory")
print("=" * 70)

ext_count = defaultdict(int)
for f in BASE.rglob('*'):
    if f.is_file():
        ext_count[f.suffix.lower()] += 1

for ext, count in sorted(ext_count.items()):
    print(f"  {ext or '(no ext)'}: {count}")
