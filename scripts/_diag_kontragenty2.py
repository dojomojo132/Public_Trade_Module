# -*- coding: utf-8 -*-
import os
import xml.etree.ElementTree as ET

# Check if Контрагенты.xml descriptor exists
paths_to_check = [
    r"D:\Git\Public_Trade_Module\Конфигурация\Catalogs\Контрагенты.xml",
    r"D:\Git\Public_Trade_Module\Проверка\Catalogs\Контрагенты.xml",
]
for p in paths_to_check:
    print(f"EXISTS: {os.path.exists(p)} - {p}")

# Check Configuration.xml for Контрагенты
cfg = r"D:\Git\Public_Trade_Module\Конфигурация\Configuration.xml"
print("\n=== Configuration.xml: Контрагенты lines ===")
with open(cfg, 'r', encoding='utf-8-sig') as f:
    for i, line in enumerate(f, 1):
        if 'Контрагент' in line:
            print(f"  L{i}: {line.rstrip()}")

# Check ConfigDumpInfo.xml for Контрагенты
cdi = r"D:\Git\Public_Trade_Module\Конфигурация\ConfigDumpInfo.xml"
print("\n=== ConfigDumpInfo.xml: Контрагенты lines ===")
with open(cdi, 'r', encoding='utf-8-sig') as f:
    for i, line in enumerate(f, 1):
        if 'Контрагент' in line:
            print(f"  L{i}: {line.rstrip()}")

# Check what the IB dump (Проверка) Контрагенты.xml says about forms
proverka_xml = r"D:\Git\Public_Trade_Module\Проверка\Catalogs\Контрагенты.xml"
if os.path.exists(proverka_xml):
    print(f"\n=== Проверка/Catalogs/Контрагенты.xml - Form references ===")
    with open(proverka_xml, 'r', encoding='utf-8-sig') as f:
        for i, line in enumerate(f, 1):
            if 'Form' in line or 'form' in line or 'Форма' in line:
                print(f"  L{i}: {line.rstrip()}")

# Find ALL ФормаВыбора references in Конфигурация
print("\n=== All ФормаВыбора references anywhere ===")
for dp, dn, fn in os.walk(r"D:\Git\Public_Trade_Module\Конфигурация"):
    for f in fn:
        fp = os.path.join(dp, f)
        if 'ФормаВыбора' in f:
            print(f"  FILE: {fp}")
