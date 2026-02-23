# -*- coding: utf-8 -*-
"""
Мердж ConfigDumpInfo.xml v2: правильный парсинг с учётом ns0 namespace.
"""
import subprocess
import os
import xml.etree.ElementTree as ET

os.chdir(r"D:\Git\Public_Trade_Module")
os.environ["GIT_CONFIG_PARAMETERS"] = "'core.quotePath=false'"

ns_url = 'http://v8.1c.ru/8.3/xcf/dumpinfo'
ET.register_namespace('', ns_url)

# 1. Получить БПО ConfigDumpInfo.xml
result = subprocess.run(
    ["git", "show", "f8d6d1a:Конфигурация/ConfigDumpInfo.xml"],
    capture_output=True, encoding="utf-8", errors="replace"
)
bpo_cdi = result.stdout

# 2. Прочитать текущий
with open(r"Конфигурация\ConfigDumpInfo.xml", "r", encoding="utf-8-sig") as f:
    current_cdi = f.read()

# 3. Парсинг
bpo_tree = ET.fromstring(bpo_cdi)
current_tree = ET.fromstring(current_cdi)

# Найти ConfigVersions
config_versions_tag = f'{{{ns_url}}}ConfigVersions'
metadata_tag = f'{{{ns_url}}}Metadata'

bpo_cv = bpo_tree.find(config_versions_tag)
current_cv = current_tree.find(config_versions_tag)

if current_cv is None:
    print("ОШИБКА: ConfigVersions не найден в текущем файле!")
    exit(1)
if bpo_cv is None:
    print("ОШИБКА: ConfigVersions не найден в БПО файле!")
    exit(1)

# Собрать существующие записи верхнего уровня
existing_names = set()
for elem in current_cv.findall(metadata_tag):
    name = elem.get('name', '')
    if name:
        existing_names.add(name)

print(f"Существующих записей PTM: {len(existing_names)}")

# Собрать записи из БПО
bpo_entries = bpo_cv.findall(metadata_tag)
print(f"Записей в БПО: {len(bpo_entries)}")

new_entries = []
skipped = 0
for elem in bpo_entries:
    name = elem.get('name', '')
    if name not in existing_names:
        new_entries.append(elem)
    else:
        skipped += 1

print(f"Пропущено (уже есть в PTM): {skipped}")
print(f"Новых для добавления: {len(new_entries)}")

# Группируем
by_type = {}
total_sub = 0
for elem in new_entries:
    name = elem.get('name', '')
    parts = name.split('.')
    obj_type = parts[0] if parts else 'Unknown'
    if obj_type not in by_type:
        by_type[obj_type] = 0
    by_type[obj_type] += 1
    # Считаем вложенные
    for sub in elem.findall(f'.//{metadata_tag}'):
        total_sub += 1

print(f"Вложенных записей (атрибуты, формы, ТЧ): {total_sub}")
for t, c in sorted(by_type.items(), key=lambda x: -x[1]):
    print(f"  {t}: {c}")

# 4. Добавить
for entry in new_entries:
    current_cv.append(entry)

# 5. Записать
output = ET.tostring(current_tree, encoding='unicode', xml_declaration=True)
output = output.replace("<?xml version='1.0' encoding='us-ascii'?>", '<?xml version="1.0" encoding="UTF-8"?>')

for path in [r"Конфигурация\ConfigDumpInfo.xml", r"Конфигурация\Проверка\ConfigDumpInfo.xml"]:
    with open(path, "w", encoding="utf-8-sig") as f:
        f.write(output)
    print(f"\n✓ Записан: {path}")

print(f"\n=== ИТОГ ===")
print(f"Добавлено {len(new_entries)} записей верхнего уровня + {total_sub} вложенных записей")
