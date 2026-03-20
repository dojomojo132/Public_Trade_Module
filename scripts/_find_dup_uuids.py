# -*- coding: utf-8 -*-
"""Find ALL duplicate UUIDs across all config XML files"""
import os
import re
from collections import defaultdict

base = r'd:\Git\Public_Trade_Module'
config_dir = os.path.join(base, 'Конфигурация')

uuid_pattern = re.compile(r'''uuid="([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"''', re.I)
id_pattern   = re.compile(r'''id="([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"''', re.I)

# uuid="" — это декларация объекта (главный атрибут)
# id="" — это тоже чаще всего ссылка на объект, но в CDI это декларация

# Collect all uuid= declarations across XML object files (NOT CDI)
uuid_registry = defaultdict(list)  # uuid -> [(file, line_num, line)]

for root, dirs, files in os.walk(config_dir):
    for fname in files:
        if fname == 'ConfigDumpInfo.xml':
            continue
        if not fname.endswith('.xml'):
            continue
        fpath = os.path.join(root, fname)
        rel = os.path.relpath(fpath, base)
        try:
            with open(fpath, 'r', encoding='utf-8-sig') as f:
                for i, line in enumerate(f, 1):
                    # Only look for uuid= attribute declarations (root-level object declarations)
                    for m in uuid_pattern.finditer(line):
                        uid = m.group(1).lower()
                        uuid_registry[uid].append((rel, i, line.strip()[:120]))
        except:
            pass

print("=== DUPLICATE UUIDs (uuid= attribute) ===")
duplicates_found = 0
for uid, occurrences in sorted(uuid_registry.items()):
    if len(occurrences) > 1:
        # Check if it's the same file (e.g., uuid appears twice in same file - unlikely but possible)
        files = [o[0] for o in occurrences]
        if len(set(files)) > 1:
            print(f'\nUUID: {uid}')
            for rel, lineno, line in occurrences:
                print(f'  {rel}:{lineno}: {line}')
            duplicates_found += 1

print(f'\nTotal duplicate UUIDs (across different files): {duplicates_found}')

# Also check Configuration.xml for any references to НалоговыеГруппы
print("\n=== Configuration.xml references to НалоговыеГруппы ===")
config_xml = os.path.join(config_dir, 'Configuration.xml')
with open(config_xml, 'r', encoding='utf-8-sig') as f:
    content = f.read()
if 'НалоговыеГруппы' in content:
    for i, line in enumerate(content.split('\n'), 1):
        if 'НалоговыеГруппы' in line:
            print(f'  Line {i}: {line.strip()}')
else:
    print('НалоговыеГруппы NOT FOUND in Configuration.xml - ERROR!')

# Check Enum СтавкиНДС exists in config 
enum_dir = os.path.join(config_dir, 'Enums')
stavki_nds = os.path.join(enum_dir, 'СтавкиНДС.xml')
if os.path.exists(stavki_nds):
    print(f'\nEnum СтавкиНДС exists: {stavki_nds}')
    with open(stavki_nds, 'r', encoding='utf-8-sig') as f:
        print(f'  Content: {f.read()[:500]}')
else:
    print(f'\nEnum СтавкиНДС XML NOT FOUND at {stavki_nds}')
    if os.path.exists(enum_dir):
        print(f'  Enums directory contents: {os.listdir(enum_dir)}')
    else:
        print('  Enums directory does not exist!')
