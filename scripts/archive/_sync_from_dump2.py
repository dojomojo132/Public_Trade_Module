# -*- coding: utf-8 -*-
"""Sync Проверка from dump, then add ФормаГруппы"""
import pathlib
import shutil

dump_dir = pathlib.Path(r"D:\Git\Public_Trade_Module\_dump_clean")
proverka_dir = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка")
main_dir = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")

# Step 1: Sync Проверка from dump (full sync)
print("Step 1: Syncing Проверка from dump...")

if not dump_dir.exists():
    print("  ERROR: dump directory not found!")
    exit(1)

# Remove old Проверка and copy from dump
if proverka_dir.exists():
    shutil.rmtree(proverka_dir)
shutil.copytree(dump_dir, proverka_dir)
print("  ✓ Проверка synced from dump")

# Step 2: Verify key files
cdi = proverka_dir / "ConfigDumpInfo.xml"
nom = proverka_dir / "Catalogs" / "Номенклатура.xml"

if cdi.exists():
    text = cdi.read_text(encoding='utf-8-sig')
    nom_lines = [l.strip() for l in text.split('\n') if 'Catalog.Номенклатура' in l and 'ДемоНоменклатура' not in l and 'Dimension' not in l and 'Attribute.' not in l]
    for line in nom_lines:
        print(f"  CDI: {line}")

if nom.exists():
    text = nom.read_text(encoding='utf-8-sig')
    for line in text.split('\n'):
        if 'DefaultFolderForm' in line or 'DefaultObjectForm' in line:
            print(f"  Nom: {line.strip()}")
    for line in text.split('\n'):
        if '<Form>' in line:
            print(f"  Nom: {line.strip()}")

# Step 3: Also sync main Конфигурация files (Номенклатура + ConfigDumpInfo)
print("\nStep 3: Syncing main Конфигурация key files...")
# Copy Номенклатура.xml (contains uuid and configVersion)
src_nom = dump_dir / "Catalogs" / "Номенклатура.xml"
dst_nom = main_dir / "Catalogs" / "Номенклатура.xml"
if src_nom.exists():
    shutil.copy2(src_nom, dst_nom)
    print(f"  ✓ Catalogs/Номенклатура.xml synced")

# Copy ConfigDumpInfo.xml
src_cdi = dump_dir / "ConfigDumpInfo.xml"
dst_cdi = main_dir / "ConfigDumpInfo.xml"
if src_cdi.exists():
    shutil.copy2(src_cdi, dst_cdi)
    print(f"  ✓ ConfigDumpInfo.xml synced")

# Copy Номенклатура forms folder (ФормаЭлемента, ФормаСписка from IB)
src_forms = dump_dir / "Catalogs" / "Номенклатура"
dst_forms = main_dir / "Catalogs" / "Номенклатура"
if src_forms.exists():
    if dst_forms.exists():
        shutil.rmtree(dst_forms)
    shutil.copytree(src_forms, dst_forms)
    print(f"  ✓ Catalogs/Номенклатура/ folder synced")

print("\nDone! Both folders synced from ИБ dump.")
