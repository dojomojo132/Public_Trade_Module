# -*- coding: utf-8 -*-
"""Verify UUID replacement"""
import os

base = r'd:\Git\Public_Trade_Module'
old_uuid = 'a1b2c3d4-e5f6-4789-abcd-ef0123456789'
new_uuid = '56e1f87e-e895-4024-9d83-9e94d5e0a94f'
files = [
    os.path.join(base, 'Конфигурация', 'Catalogs', 'НалоговыеГруппы.xml'),
    os.path.join(base, 'Конфигурация', 'ConfigDumpInfo.xml'),
    os.path.join(base, 'Конфигурация', 'DataProcessors', 'ИнформацияНоменклатуры.xml'),
]
for fp in files:
    if not os.path.exists(fp):
        print(f'NOT FOUND: {fp}')
        continue
    with open(fp, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    old_count = content.count(old_uuid)
    new_count = content.count(new_uuid)
    fname = os.path.basename(fp)
    status = 'OK' if old_count == 0 else 'STILL HAS OLD UUID'
    print(f'{fname}: old={old_count}, new={new_count} [{status}]')
    if old_count > 0:
        for i, line in enumerate(content.split('\n'), 1):
            if old_uuid in line:
                print(f'  Line {i}: {line.strip()[:150]}')

# Also check НалоговыеГруппы has correct СтавкаНДС block
ng_path = os.path.join(base, 'Конфигурация', 'Catalogs', 'НалоговыеГруппы.xml')
with open(ng_path, 'r', encoding='utf-8-sig') as f:
    content = f.read()
if new_uuid in content:
    print(f'\nNew UUID found in НалоговыеГруппы.xml: OK')
else:
    print(f'\nNew UUID NOT found in НалоговыеГруппы.xml: ERROR')
if 'СтавкаНДС' in content:
    print('СтавкаНДС attribute exists: OK')
