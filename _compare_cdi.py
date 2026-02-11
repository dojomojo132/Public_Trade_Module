# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET

NS = '{http://v8.1c.ru/8.3/xcf/dumpinfo}'

def get_all_metadata(root):
    result = {}
    for elem in root.iter(NS + 'Metadata'):
        name = elem.get('name', '')
        mid = elem.get('id', '')
        cv = elem.get('configVersion', '')
        result[name] = {'id': mid, 'configVersion': cv}
    return result

orig = ET.parse(r'D:\Git\Public_Trade_Module\Конфигурация\ConfigDumpInfo.xml')
work = ET.parse(r'D:\Git\Public_Trade_Module\Конфигурация\Проверка\ConfigDumpInfo.xml')

orig_meta = get_all_metadata(orig.getroot())
work_meta = get_all_metadata(work.getroot())

orig_names = set(orig_meta.keys())
work_names = set(work_meta.keys())

added = work_names - orig_names
removed = orig_names - work_names
common = orig_names & work_names

changed_id = []
for name in sorted(common):
    if orig_meta[name]['id'] != work_meta[name]['id']:
        changed_id.append((name, orig_meta[name]['id'], work_meta[name]['id']))

print(f'=== CDI COMPARISON ===')
print(f'Original entries: {len(orig_meta)}')
print(f'Working entries:  {len(work_meta)}')
print(f'Added: {len(added)}, Removed: {len(removed)}, Changed ID: {len(changed_id)}')

if added:
    print(f'\n--- ADDED ({len(added)}) ---')
    for n in sorted(added):
        print(f'  + {n}')
        print(f'    id={work_meta[n]["id"]}')
        cv = work_meta[n]['configVersion']
        if cv:
            print(f'    cv={cv}')

if removed:
    print(f'\n--- REMOVED ({len(removed)}) ---')
    for n in sorted(removed):
        print(f'  - {n}')
        print(f'    id={orig_meta[n]["id"]}')

if changed_id:
    print(f'\n--- CHANGED ID ({len(changed_id)}) ---')
    for name, old_val, new_val in changed_id:
        print(f'  ~ {name}')
        print(f'    OLD: {old_val}')
        print(f'    NEW: {new_val}')

# Check nesting: find entries that are top-level (have configVersion)
orig_top = {n for n, v in orig_meta.items() if v['configVersion']}
work_top = {n for n, v in work_meta.items() if v['configVersion']}
added_top = work_top - orig_top
if added_top:
    print(f'\n--- NEW TOP-LEVEL ENTRIES ---')
    for n in sorted(added_top):
        print(f'  + {n}  cv={work_meta[n]["configVersion"]}')
