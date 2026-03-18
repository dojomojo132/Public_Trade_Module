"""Rename handlers to Latin in XML and BSL, restore full backup"""
import os, shutil

base_ext = os.path.join(r'D:\Git\Public_Trade_Module', 'Конфигурация_PTM_Analytics', 'HTTPServices', 'Анл_МобильнаяКасса', 'Ext')
bak = os.path.join(base_ext, 'Module.bsl.full_backup')
bsl = os.path.join(base_ext, 'Module.bsl')

xml_path = os.path.join(r'D:\Git\Public_Trade_Module', 'Конфигурация_PTM_Analytics', 'HTTPServices', 'Анл_МобильнаяКасса.xml')

# Handler rename map: Cyrillic -> Latin
rename_map = {
    'ГлавнаяСтраницаGET': 'mainGET',
    'КорзинаGET': 'cartGET',
    'КорзинаPOST': 'cartPOST',
    'КорзинаDELETE': 'cartDELETE',
    'ОтправкаPOST': 'sendPOST',
}

# 1. Update XML handlers
with open(xml_path, 'r', encoding='utf-8-sig') as f:
    xml_content = f.read()

for old, new in rename_map.items():
    xml_content = xml_content.replace(f'<Handler>{old}</Handler>', f'<Handler>{new}</Handler>')
    print(f'XML: {old} -> {new}')

# Write back with BOM
with open(xml_path, 'wb') as f:
    f.write('\ufeff'.encode('utf-8') + xml_content.lstrip('\ufeff').encode('utf-8'))
print(f'XML updated: {os.path.getsize(xml_path)} bytes')

# 2. Restore full BSL from backup and rename functions
with open(bak, 'rb') as f:
    bsl_data = f.read()

bsl_content = bsl_data.decode('utf-8-sig')

for old, new in rename_map.items():
    bsl_content = bsl_content.replace(f'Функция {old}(', f'Функция {new}(')
    count = bsl_content.count(new)
    print(f'BSL: Функция {old} -> Функция {new}')

# Write back with BOM + CRLF
bsl_bytes = ('\ufeff' + bsl_content.lstrip('\ufeff')).encode('utf-8')
with open(bsl, 'wb') as f:
    f.write(bsl_bytes)
print(f'BSL updated: {os.path.getsize(bsl)} bytes')

# Verify
with open(bsl, 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()
    
print('\nFunctions found in BSL:')
for i, line in enumerate(lines, 1):
    if line.startswith('Функция '):
        print(f'  L{i}: {line.rstrip()[:80]}')
