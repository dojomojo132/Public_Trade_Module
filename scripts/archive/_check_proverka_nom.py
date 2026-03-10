# -*- coding: utf-8 -*-
"""List all files in Проверка/Catalogs/Номенклатура"""
import os

base = r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Catalogs"

# Find the Номенклатура folder (handle encoding)
nom_folder = None
for item in os.listdir(base):
    full = os.path.join(base, item)
    if os.path.isdir(full) and "оменклатур" in item:
        nom_folder = full
        break

if not nom_folder:
    print("Номенклатура folder NOT FOUND in Проверка/Catalogs")
    print(f"Available: {os.listdir(base)}")
else:
    print(f"Found: {os.path.basename(nom_folder)}")
    for root, dirs, files in os.walk(nom_folder):
        rel = os.path.relpath(root, nom_folder)
        if rel == '.':
            rel = ''
        for f in files:
            if rel:
                print(f"  {rel}/{f}")
            else:
                print(f"  {f}")
    
    # Check Forms specifically
    forms_path = os.path.join(nom_folder, "Forms")
    if os.path.exists(forms_path):
        print(f"\nForms directory:")
        items = os.listdir(forms_path)
        print(f"  Contents ({len(items)} items): {items}")
    else:
        print(f"\nForms directory does NOT exist")
