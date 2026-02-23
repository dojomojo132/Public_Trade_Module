# -*- coding: utf-8 -*-
"""
Мердж ConfigDumpInfo.xml: добавить записи БПО в текущий PTM файл.
Сохраняем все существующие PTM-записи, добавляем только новые из БПО.
"""
import subprocess
import os
import xml.etree.ElementTree as ET

os.chdir(r"D:\Git\Public_Trade_Module")
os.environ["GIT_CONFIG_PARAMETERS"] = "'core.quotePath=false'"

# 1. Получить БПО ConfigDumpInfo.xml
result = subprocess.run(
    ["git", "show", "f8d6d1a:Конфигурация/ConfigDumpInfo.xml"],
    capture_output=True, encoding="utf-8", errors="replace"
)
bpo_cdi = result.stdout

# 2. Прочитать текущий ConfigDumpInfo.xml
with open(r"Конфигурация\ConfigDumpInfo.xml", "r", encoding="utf-8-sig") as f:
    current_cdi = f.read()

# 3. Парсинг
# ConfigDumpInfo использует свой namespace
ns_url = 'http://v8.1c.ru/8.3/config/dump'
ET.register_namespace('', ns_url)

bpo_tree = ET.fromstring(bpo_cdi)
current_tree = ET.fromstring(current_cdi)

# Собрать существующие записи (по name атрибуту)
existing_names = set()
for elem in current_tree.iter(f'{{{ns_url}}}Metadata'):
    name = elem.get('name', '')
    if name:
        existing_names.add(name)

print(f"Существующих записей PTM: {len(existing_names)}")

# Собрать записи из БПО
bpo_new_entries = []
bpo_existing_count = 0
for child in bpo_tree:
    tag = child.tag.replace(f'{{{ns_url}}}', '')
    if tag == 'Metadata':
        name = child.get('name', '')
        if name and name not in existing_names:
            bpo_new_entries.append(child)
        else:
            bpo_existing_count += 1

print(f"Существующих записей (пропущено): {bpo_existing_count}")
print(f"Новых записей БПО для добавления: {len(bpo_new_entries)}")

# Группируем по типу
by_type = {}
for elem in bpo_new_entries:
    name = elem.get('name', '')
    parts = name.split('.')
    obj_type = parts[0] if parts else 'Unknown'
    if obj_type not in by_type:
        by_type[obj_type] = 0
    by_type[obj_type] += 1
    # Считаем вложенные Metadata
    for sub in elem.iter(f'{{{ns_url}}}Metadata'):
        if sub is not elem:
            by_type[obj_type] += 1

for t, c in sorted(by_type.items(), key=lambda x: -x[1]):
    print(f"  {t}: {c} записей")

# 4. Добавить новые записи
for entry in bpo_new_entries:
    current_tree.append(entry)

# 5. Записать результат
output = ET.tostring(current_tree, encoding='unicode', xml_declaration=True)
output = output.replace("<?xml version='1.0' encoding='us-ascii'?>", '<?xml version="1.0" encoding="UTF-8"?>')

for path in [r"Конфигурация\ConfigDumpInfo.xml", r"Конфигурация\Проверка\ConfigDumpInfo.xml"]:
    with open(path, "w", encoding="utf-8-sig") as f:
        f.write(output)
    print(f"\n✓ Записан: {path}")

print(f"\n=== ИТОГ ===")
print(f"Добавлено {len(bpo_new_entries)} записей верхнего уровня БПО в ConfigDumpInfo.xml")
