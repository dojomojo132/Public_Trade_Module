# -*- coding: utf-8 -*-
"""Check XML validity of all files in Проверка"""
import pathlib
import xml.etree.ElementTree as ET

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка")
errors = []
total = 0

for xml_file in sorted(base.rglob("*.xml")):
    total += 1
    try:
        ET.parse(xml_file)
    except ET.ParseError as e:
        errors.append((xml_file.relative_to(base), str(e)))
    except Exception as e:
        errors.append((xml_file.relative_to(base), str(e)))

print(f"Total XML files: {total}")
print(f"Parsing errors: {len(errors)}")
for path, err in errors:
    print(f"  ERROR: {path}")
    print(f"    {err}")
