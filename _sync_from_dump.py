# -*- coding: utf-8 -*-
"""
Sync correct files from final dump back to source (Конфигурация/) and Проверка/.
The final dump has the correct CDI and all files with correct UUID.
"""
import os
import pathlib
import shutil

dump_dir = r"D:\Git\Public_Trade_Module\Конфигурация\_DumpFinal"
source_dir = r"D:\Git\Public_Trade_Module\Конфигурация"
proverka_dir = r"D:\Git\Public_Trade_Module\Конфигурация\Проверка"

files_to_sync = [
    # (relative_path_in_dump, description)
    ("ConfigDumpInfo.xml", "CDI"),
    ("Catalogs/Номенклатура.xml", "Catalog descriptor"),
    ("Catalogs/Номенклатура/Forms/ФормаГруппы.xml", "Form descriptor"),
    ("Catalogs/Номенклатура/Forms/ФормаГруппы/Ext/Form.xml", "Form XML"),
    ("Catalogs/Номенклатура/Forms/ФормаГруппы/Ext/Form/Module.bsl", "BSL module"),
]

for rel, desc in files_to_sync:
    src = os.path.join(dump_dir, rel)
    if not os.path.exists(src):
        print(f"  WARNING: {rel} not found in dump!")
        continue
    
    # Copy to source
    dst_source = os.path.join(source_dir, rel)
    os.makedirs(os.path.dirname(dst_source), exist_ok=True)
    shutil.copy2(src, dst_source)
    
    # Copy to Проверка
    dst_proverka = os.path.join(proverka_dir, rel)
    os.makedirs(os.path.dirname(dst_proverka), exist_ok=True)
    shutil.copy2(src, dst_proverka)
    
    print(f"  Synced: {desc} ({rel})")

# Verify
print("\nVerification:")
for rel, desc in files_to_sync:
    src_exists = os.path.exists(os.path.join(source_dir, rel))
    prv_exists = os.path.exists(os.path.join(proverka_dir, rel))
    print(f"  {desc}: source={src_exists}, proverka={prv_exists}")

# Check UUID in the synced files
fg_xml = os.path.join(source_dir, "Catalogs/Номенклатура/Forms/ФормаГруппы.xml")
content = pathlib.Path(fg_xml).read_text(encoding='utf-8-sig')
import re
uuid_match = re.search(r'uuid="([^"]+)"', content)
print(f"\nForm UUID: {uuid_match.group(1) if uuid_match else 'NOT FOUND'}")

# Check CDI has the correct UUID
cdi = os.path.join(source_dir, "ConfigDumpInfo.xml")
cdi_content = pathlib.Path(cdi).read_text(encoding='utf-8-sig')
if "79c07310-710b-4c4d-84c7-3afd65bf5024" in cdi_content:
    print("CDI UUID: 79c07310-710b-4c4d-84c7-3afd65bf5024 (correct)")
elif "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e" in cdi_content:
    print("CDI UUID: b2c3d4e5-... (OLD - WRONG!)")
else:
    print("CDI UUID: unknown")

# Check Номенклатура.xml has DefaultFolderForm
nom_xml = os.path.join(source_dir, "Catalogs/Номенклатура.xml")
nom_content = pathlib.Path(nom_xml).read_text(encoding='utf-8-sig')
if "DefaultFolderForm" in nom_content:
    print("DefaultFolderForm: present")
else:
    print("DefaultFolderForm: MISSING!")

print("\nDone!")
