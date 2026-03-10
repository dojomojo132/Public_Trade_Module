# -*- coding: utf-8 -*-
"""Analyze the dump to understand correct CDI and form structure"""
import os
import pathlib
import re

dump_dir = r"D:\Git\Public_Trade_Module\Конфигурация\_DumpVerify"

# 1. Find Номенклатура in dump CDI
cdi_path = os.path.join(dump_dir, "ConfigDumpInfo.xml")
cdi_content = pathlib.Path(cdi_path).read_text(encoding='utf-8-sig')

# Extract Номенклатура section
nom_pattern = r'(<Metadata name="Catalog\.Номенклатура".*?</Metadata>)'
nom_match = re.search(nom_pattern, cdi_content, re.DOTALL)
if nom_match:
    print("=== CDI: Catalog.Номенклатура block ===")
    print(nom_match.group(1))

# Find form entries outside the block
form_pattern = r'(<Metadata name="Catalog\.Номенклатура\.Form\.[^"]*"[^>]*/>)'
for m in re.finditer(form_pattern, cdi_content):
    print(f"\n=== CDI: Form entry ===")
    print(m.group(1))

# Also find ObjectModule entry
obj_pattern = r'(<Metadata name="Catalog\.Номенклатура\.ObjectModule"[^>]*/>)'
for m in re.finditer(obj_pattern, cdi_content):
    print(f"\n=== CDI: ObjectModule ===")
    print(m.group(1))

# 2. Check dump Номенклатура.xml for DefaultFolderForm
nom_xml = os.path.join(dump_dir, "Catalogs", "Номенклатура.xml")
if os.path.exists(nom_xml):
    nom_content = pathlib.Path(nom_xml).read_text(encoding='utf-8-sig')
    # Check for DefaultFolderForm
    if "DefaultFolderForm" in nom_content:
        m = re.search(r'<DefaultFolderForm>.*?</DefaultFolderForm>', nom_content)
        if m:
            print(f"\n=== Номенклатура.xml DefaultFolderForm ===")
            print(m.group(0))
    else:
        print(f"\n=== Номенклатура.xml: NO DefaultFolderForm ===")
    
    # Show ChildObjects Forms section
    forms_match = re.search(r'(<Form>.*</Form>)', nom_content, re.DOTALL)
    if forms_match:
        print(f"\n=== Forms in ChildObjects ===")
        for fm in re.finditer(r'<Form>.*?</Form>', nom_content):
            print(f"  {fm.group(0)}")

# 3. Check form structure in dump
print("\n\n=== Dump form files ===")
nom_forms = os.path.join(dump_dir, "Catalogs", "Номенклатура", "Forms")
if os.path.exists(nom_forms):
    for root, dirs, files in os.walk(nom_forms):
        for f in files:
            full = os.path.join(root, f)
            rel = os.path.relpath(full, nom_forms)
            size = os.path.getsize(full)
            print(f"  {rel} ({size} bytes)")
else:
    print("  Forms directory not found in dump")

# 4. Check another catalog's form structure for comparison (e.g. Контрагенты)
print("\n=== CDI: Контрагенты form entries ===")
kontr_pattern = r'(<Metadata name="Catalog\.Контрагенты\.Form\.[^"]*"[^>]*/>)'
for m in re.finditer(kontr_pattern, cdi_content):
    print(f"  {m.group(1)}")
