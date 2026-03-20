# -*- coding: utf-8 -*-
"""Check if duplicate UUIDs existed BEFORE our changes (in backup)"""
import os
import re
from collections import defaultdict

# Check BACKUP directory for same duplicate UUIDs
backup_base = r'd:\Git\Public_Trade_Module\_backups\2026-03-20_224120'
backup_config = os.path.join(backup_base, 'Конфигурация')

if not os.path.exists(backup_config):
    print(f'Backup config dir not found: {backup_config}')
    exit()

uuid_pattern = re.compile(r'''uuid="([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"''', re.I)
suspect_uuids = [
    'a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d',  # Кассы + ТоварыАПИ
    'b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e',  # ЧекККМ + ТоварыАПИ
    '2adf9e37-b933-48d8-99c2-95dde4f844c2',  # ОткрытьКассу forms
    '606b7b80-9b17-48af-a399-8484b56597f3',  # Контрагенты forms
]

uuid_registry = defaultdict(list)
for root, dirs, files in os.walk(backup_config):
    for fname in files:
        if fname == 'ConfigDumpInfo.xml':
            continue
        if not fname.endswith('.xml'):
            continue
        fpath = os.path.join(root, fname)
        rel = os.path.relpath(fpath, backup_base)
        try:
            with open(fpath, 'r', encoding='utf-8-sig') as f:
                for i, line in enumerate(f, 1):
                    for m in uuid_pattern.finditer(line):
                        uid = m.group(1).lower()
                        if uid in suspect_uuids:
                            uuid_registry[uid].append((rel, i, line.strip()[:120]))
        except:
            pass

print("=== Duplicate UUIDs in BACKUP (before our changes) ===")
for uid in suspect_uuids:
    occurrences = uuid_registry[uid]
    files_set = set(o[0] for o in occurrences)
    status = 'PRE-EXISTING' if len(files_set) > 1 else ('SINGLE FILE' if files_set else 'NOT FOUND')
    print(f'\nUUID: {uid} [{status}]')
    for rel, lineno, line in occurrences:
        print(f'  {rel}:{lineno}: {line}')

# Now check the current state of НалоговыеГруппы - make sure our new UUID is clean
print('\n=== New НалоговыеГруппы.Attribute.СтавкаНДС UUID check ===')
new_uuid = '56e1f87e-e895-4024-9d83-9e94d5e0a94f'
current_config = os.path.join(r'd:\Git\Public_Trade_Module', 'Конфигурация')
new_uuid_files = []
for root, dirs, files in os.walk(current_config):
    for fname in files:
        if fname.endswith('.xml'):
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                if new_uuid in content:
                    rel = os.path.relpath(fpath, r'd:\Git\Public_Trade_Module')
                    new_uuid_files.append(rel)
            except:
                pass
print(f'New UUID {new_uuid} found in:')
for f in new_uuid_files:
    print(f'  {f}')
if len(new_uuid_files) <= 2:  # НалоговыеГруппы.xml + ConfigDumpInfo.xml
    print('CLEAN - used only in expected files')
else:
    print('WARNING - used in unexpected files too!')
