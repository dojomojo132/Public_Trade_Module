# -*- coding: utf-8 -*-
"""Extract CDI entries for ПродажиЗаСмену and Кассир from IB dump"""
import pathlib, re

root = pathlib.Path(r"D:\Git\Public_Trade_Module")
proverka = root / "Проверка"

# Get UUIDs from descriptors
report_xml = proverka / "Reports" / "ПродажиЗаСмену.xml"
role_xml = proverka / "Roles" / "Кассир.xml"

for f in [report_xml, role_xml]:
    content = f.read_text(encoding="utf-8-sig")
    print(f"--- {f.name} ---")
    uuids = re.findall(r'uuid="([^"]+)"', content)
    print(f"  UUID: {uuids}")
    names = re.findall(r"<Name>([^<]+)</Name>", content)
    print(f"  Names: {names}")

# CDI entries
cdi = (proverka / "ConfigDumpInfo.xml").read_text(encoding="utf-8-sig")
print("\n--- CDI entries ---")
for line in cdi.split("\n"):
    if "ПродажиЗаСмену" in line or ("Кассир" in line and "Role" in line):
        print(line.strip())
