# -*- coding: utf-8 -*-
"""Check CDI entries for Номенклатура and НалоговыеГруппы"""
import os

cdi_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "Конфигурация", "ConfigDumpInfo.xml")

with open(cdi_path, 'r', encoding='utf-8-sig') as f:
    lines = f.readlines()

print("=== CDI: Catalog.Номенклатура (без Демо) ===")
for i, line in enumerate(lines, 1):
    if 'Catalog.Номенклатура' in line and 'Демо' not in line:
        print(f"  {i}: {line.strip()}")

print("\n=== CDI: Catalog.НалоговыеГруппы ===")
for i, line in enumerate(lines, 1):
    if 'НалоговыеГруппы' in line:
        print(f"  {i}: {line.strip()}")

# Check Номенклатура.xml attributes
nom_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "Конфигурация", "Catalogs", "Номенклатура.xml")
with open(nom_path, 'r', encoding='utf-8-sig') as f:
    nom_lines = f.readlines()

print("\n=== Номенклатура.xml: Attributes/TabularSections ===")
for i, line in enumerate(nom_lines, 1):
    if 'Attribute uuid=' in line or 'TabularSection uuid=' in line:
        print(f"  {i}: {line.strip()}")

print("\n=== Номенклатура.xml: <Name> tags after Attribute/TabularSection ===")
in_attr = False
for i, line in enumerate(nom_lines, 1):
    stripped = line.strip()
    if 'Attribute uuid=' in stripped or 'TabularSection uuid=' in stripped:
        in_attr = True
        current = stripped
    elif in_attr and '<Name>' in stripped:
        print(f"  {current} --> {stripped}")
        in_attr = False

# Check backup for comparison
backup_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "_backups", "2026-03-20_224120")
if os.path.exists(backup_path):
    backup_nom = os.path.join(backup_path, "Конфигурация", "Catalogs", "Номенклатура.xml")
    if os.path.exists(backup_nom):
        with open(backup_nom, 'r', encoding='utf-8-sig') as f:
            backup_lines = f.readlines()
        print("\n=== BACKUP Номенклатура.xml: Attributes ===")
        in_attr = False
        for i, line in enumerate(backup_lines, 1):
            stripped = line.strip()
            if 'Attribute uuid=' in stripped or 'TabularSection uuid=' in stripped:
                in_attr = True
                current = stripped
            elif in_attr and '<Name>' in stripped:
                print(f"  {current} --> {stripped}")
                in_attr = False
