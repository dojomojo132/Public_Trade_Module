# -*- coding: utf-8 -*-
"""List ALL catalogs in Проверка"""
import os

base = r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Catalogs"
print("Catalogs in Проверка:")
for item in sorted(os.listdir(base)):
    full = os.path.join(base, item)
    if os.path.isdir(full):
        print(f"  [DIR] {item}")
    else:
        print(f"  [FILE] {item}")

# Also check if Номенклатура (exact match) exists
nom = os.path.join(base, "Номенклатура")
print(f"\nНоменклатура exact path exists: {os.path.exists(nom)}")

nom_xml = os.path.join(base, "Номенклатура.xml")
print(f"Номенклатура.xml exists: {os.path.exists(nom_xml)}")

# Check base Конфигурация
base2 = r"D:\Git\Public_Trade_Module\Конфигурация\Catalogs"
print(f"\n\nCatalogs in base Конфигурация:")
for item in sorted(os.listdir(base2)):
    full = os.path.join(base2, item)
    if os.path.isdir(full):
        print(f"  [DIR] {item}")
    else:
        print(f"  [FILE] {item}")
