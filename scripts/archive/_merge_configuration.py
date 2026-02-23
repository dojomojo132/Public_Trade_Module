# -*- coding: utf-8 -*-
"""
Мердж Configuration.xml: добавить объекты БПО в текущий PTM Configuration.xml
без удаления/замены существующих PTM объектов.
"""
import subprocess
import os
import xml.etree.ElementTree as ET

os.chdir(r"D:\Git\Public_Trade_Module")
os.environ["GIT_CONFIG_PARAMETERS"] = "'core.quotePath=false'"

# 1. Получить БПО Configuration.xml
result = subprocess.run(
    ["git", "show", "f8d6d1a:Конфигурация/Configuration.xml"],
    capture_output=True, encoding="utf-8", errors="replace"
)
bpo_config = result.stdout

# 2. Прочитать текущий Configuration.xml
with open(r"Конфигурация\Configuration.xml", "r", encoding="utf-8-sig") as f:
    current_config = f.read()

# 3. Парсинг
ns = {'': 'http://v8.1c.ru/8.3/MDClasses', 'xr': 'http://v8.1c.ru/8.3/xcf/readable'}
ET.register_namespace('', 'http://v8.1c.ru/8.3/MDClasses')
ET.register_namespace('v8', 'http://v8.1c.ru/8.1/data/core')
ET.register_namespace('xr', 'http://v8.1c.ru/8.3/xcf/readable')

# Получить все дочерние элементы из BPO ChildObjects
bpo_tree = ET.fromstring(bpo_config)
current_tree = ET.fromstring(current_config)

# Найти ChildObjects
ns_url = 'http://v8.1c.ru/8.3/MDClasses'
bpo_conf = bpo_tree.find(f'{{{ns_url}}}Configuration')
current_conf = current_tree.find(f'{{{ns_url}}}Configuration')

bpo_children = bpo_conf.find(f'{{{ns_url}}}ChildObjects')
current_children = current_conf.find(f'{{{ns_url}}}ChildObjects')

# Собрать существующие объекты в текущем файле
existing = set()
for child in current_children:
    tag = child.tag.replace(f'{{{ns_url}}}', '')
    name = child.text.strip() if child.text else ''
    existing.add(f"{tag}:{name}")

print(f"Существующих объектов PTM: {len(existing)}")

# Собрать объекты из БПО
bpo_objects = []
for child in bpo_children:
    tag = child.tag.replace(f'{{{ns_url}}}', '')
    name = child.text.strip() if child.text else ''
    key = f"{tag}:{name}"
    if key not in existing:
        bpo_objects.append((tag, name, child))

print(f"Новых объектов БПО для добавления: {len(bpo_objects)}")

# Группируем по типу для красивого вывода
by_type = {}
for tag, name, elem in bpo_objects:
    if tag not in by_type:
        by_type[tag] = []
    by_type[tag].append(name)

for tag, names in sorted(by_type.items()):
    print(f"  {tag}: {len(names)} объектов")
    for n in sorted(names)[:5]:
        print(f"    - {n}")
    if len(names) > 5:
        print(f"    ... и ещё {len(names)-5}")

# 4. Добавить новые объекты в текущий ChildObjects
for tag, name, elem in bpo_objects:
    current_children.append(elem)

# 5. Записать результат
output = ET.tostring(current_tree, encoding='unicode', xml_declaration=True)
# Фиксим XML declaration
output = output.replace("<?xml version='1.0' encoding='us-ascii'?>", '<?xml version="1.0" encoding="UTF-8"?>')

# Записываем в оба файла
for path in [r"Конфигурация\Configuration.xml", r"Конфигурация\Проверка\Configuration.xml"]:
    with open(path, "w", encoding="utf-8-sig") as f:
        f.write(output)
    print(f"\n✓ Записан: {path}")

print(f"\n=== ИТОГ ===")
print(f"Добавлено {len(bpo_objects)} новых объектов БПО в Configuration.xml")
