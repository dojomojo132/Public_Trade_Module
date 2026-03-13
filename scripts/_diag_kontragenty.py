# -*- coding: utf-8 -*-
import os
import xml.etree.ElementTree as ET

base = r"D:\Git\Public_Trade_Module\Конфигурация\Catalogs\Контрагенты"
print("=== FILES ===")
for dp, dn, fn in os.walk(base):
    for f in fn:
        print(os.path.join(dp, f))

# Check ConfigDumpInfo for ФормаВыбора references
cdi = r"D:\Git\Public_Trade_Module\Конфигурация\ConfigDumpInfo.xml"
print("\n=== CDI entries for Контрагенты ===")
tree = ET.parse(cdi)
root = tree.getroot()
ns = root.tag.split('}')[0] + '}' if '}' in root.tag else ''
for elem in root.iter(f'{ns}MDObject'):
    name = elem.get('name', '')
    if 'Контрагенты' in name:
        print(f"  {name}")

# Check Configuration.xml for Контрагенты forms
cfg = r"D:\Git\Public_Trade_Module\Конфигурация\Configuration.xml"
print("\n=== Configuration.xml forms for Контрагенты ===")
with open(cfg, 'r', encoding='utf-8-sig') as f:
    content = f.read()
# Find lines mentioning Контрагенты
for i, line in enumerate(content.split('\n'), 1):
    if 'Контрагент' in line and ('Form' in line or 'form' in line):
        print(f"  L{i}: {line.strip()}")

# Also check what forms are defined in the catalog XML in Проверка (IB dump)
proverka = r"D:\Git\Public_Trade_Module\Проверка\Catalogs\Контрагенты"
if os.path.exists(proverka):
    print(f"\n=== Проверка Контрагенты files ===")
    for dp, dn, fn in os.walk(proverka):
        for f in fn:
            print(os.path.join(dp, f))
