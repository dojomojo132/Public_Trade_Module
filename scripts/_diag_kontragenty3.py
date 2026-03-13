# -*- coding: utf-8 -*-
# Check Конфигурация/Catalogs/Контрагенты.xml for Form references
xml_path = r"D:\Git\Public_Trade_Module\Конфигурация\Catalogs\Контрагенты.xml"
print(f"=== {xml_path} ===")
with open(xml_path, 'r', encoding='utf-8-sig') as f:
    for i, line in enumerate(f, 1):
        if 'Form' in line or 'form' in line or 'Форма' in line:
            print(f"  L{i}: {line.rstrip()}")
