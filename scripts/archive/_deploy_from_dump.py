# -*- coding: utf-8 -*-
"""
Add ФормаГруппы to the DUMP (known-good CDI), then load from dump.
"""
import os
import pathlib
import shutil
import subprocess
import sys
import re

exe = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
ib_path = r"D:\Confiq\Public Trade Module"
dump_dir = r"D:\Git\Public_Trade_Module\Конфигурация\_DumpVerify"
log_dir = r"D:\Git\Public_Trade_Module\Документация\Валидация\logs"
src_dir = r"D:\Git\Public_Trade_Module\Конфигурация"

# Form source files
form_backup = r"D:\Git\Public_Trade_Module\_form_temp_backup"

def run_1c(args, log_name, desc):
    log_file = os.path.join(log_dir, log_name)
    cmd = [exe, "DESIGNER", "/F", ib_path] + args + [
        "/DisableStartupDialogs", "/DisableStartupMessages", "/Out", log_file
    ]
    print(f"\n{'='*60}")
    print(f"  {desc}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, timeout=300)
    log_text = ""
    if pathlib.Path(log_file).exists():
        log_text = pathlib.Path(log_file).read_text(encoding='utf-8-sig').strip()
    print(f"  Exit: {result.returncode}")
    if log_text:
        print(f"  Log: {log_text[:500]}")
    else:
        print(f"  Log: [empty - OK]")
    return result.returncode == 0, log_text

# ===========================
# STEP 1: Add form files to dump
# ===========================
print("STEP 1: Adding ФормаГруппы files to dump...")

dump_nom_forms = os.path.join(dump_dir, "Catalogs", "Номенклатура", "Forms")

# Copy ФормаГруппы.xml descriptor
src_fg_xml = os.path.join(form_backup, "ФормаГруппы.xml")
dst_fg_xml = os.path.join(dump_nom_forms, "ФормаГруппы.xml")
shutil.copy2(src_fg_xml, dst_fg_xml)
print(f"  Copied: ФормаГруппы.xml")

# Copy ФормаГруппы folder
src_fg_dir = os.path.join(form_backup, "ФормаГруппы")
dst_fg_dir = os.path.join(dump_nom_forms, "ФормаГруппы")
if os.path.exists(dst_fg_dir):
    shutil.rmtree(dst_fg_dir)
shutil.copytree(src_fg_dir, dst_fg_dir)
print(f"  Copied: ФормаГруппы/ folder")

# ===========================
# STEP 2: Update Номенклатура.xml in dump (add DefaultFolderForm + Form entry)
# ===========================
print("\nSTEP 2: Updating Номенклатура.xml in dump...")
dump_nom_xml = os.path.join(dump_dir, "Catalogs", "Номенклатура.xml")
nom_content = pathlib.Path(dump_nom_xml).read_text(encoding='utf-8-sig')

# Add DefaultFolderForm after DefaultObjectForm
if "DefaultFolderForm" not in nom_content:
    nom_content = nom_content.replace(
        "</DefaultObjectForm>",
        "</DefaultObjectForm>\n\t\t\t<DefaultFolderForm>Catalog.Номенклатура.Form.ФормаГруппы</DefaultFolderForm>"
    )
    print(f"  Added DefaultFolderForm")

# Add ФормаГруппы to ChildObjects
if "<Form>ФормаГруппы</Form>" not in nom_content:
    # Add after the last Form entry
    nom_content = nom_content.replace(
        "<Form>ФормаСписка</Form>",
        "<Form>ФормаСписка</Form>\n\t\t\t<Form>ФормаГруппы</Form>"
    )
    print(f"  Added Form entry in ChildObjects")

pathlib.Path(dump_nom_xml).write_text(nom_content, encoding='utf-8-sig')

# ===========================  
# STEP 3: Update ConfigDumpInfo.xml in dump (add ФормаГруппы entries)
# ===========================
print("\nSTEP 3: Updating ConfigDumpInfo.xml in dump...")
dump_cdi = os.path.join(dump_dir, "ConfigDumpInfo.xml")
cdi_content = pathlib.Path(dump_cdi).read_text(encoding='utf-8-sig')

# Get UUID of the form from ФормаГруппы.xml
fg_xml_content = pathlib.Path(src_fg_xml).read_text(encoding='utf-8-sig')
uuid_match = re.search(r'uuid="([^"]+)"', fg_xml_content)
form_uuid = uuid_match.group(1) if uuid_match else "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e"
print(f"  Form UUID: {form_uuid}")

# Add entries after ФормаСписка.Form
new_entries = f'''
		<Metadata name="Catalog.Номенклатура.Form.ФормаГруппы" id="{form_uuid}" configVersion="00000000000000000000000000000000FFFFFFFF"/>
		<Metadata name="Catalog.Номенклатура.Form.ФормаГруппы.Form" id="{form_uuid}.0" configVersion="00000000000000000000000000000000FFFFFFFF"/>'''

# Find insertion point - after ФормаСписка.Form entry
if "Catalog.Номенклатура.Form.ФормаГруппы" not in cdi_content:
    # Insert after the last form's .Form entry
    pattern = r'(<Metadata name="Catalog\.Номенклатура\.Form\.ФормаЭлемента\.Form"[^/]*/>\s*)'
    match = re.search(pattern, cdi_content)
    if match:
        insert_pos = match.end()
        cdi_content = cdi_content[:insert_pos] + new_entries + "\n" + cdi_content[insert_pos:]
        print(f"  Added CDI entries")
    else:
        print(f"  WARNING: Could not find insertion point!")

pathlib.Path(dump_cdi).write_text(cdi_content, encoding='utf-8-sig')

# ===========================
# STEP 4: Verify dump files
# ===========================
print("\nSTEP 4: Verifying dump files...")
for root, dirs, files in os.walk(os.path.join(dump_dir, "Catalogs", "Номенклатура", "Forms")):
    for f in files:
        full = os.path.join(root, f)
        rel = os.path.relpath(full, dump_dir)
        print(f"  {rel} ({os.path.getsize(full)} bytes)")

# ===========================
# STEP 5: Load from dump
# ===========================
ok, log = run_1c(["/LoadConfigFromFiles", dump_dir], "load-with-form2.log", "Load config WITH ФормаГруппы (from dump)")
if not ok:
    print(f"\nFAILED! Log: {log}")
    print("\nTrying without configVersion (remove CDI entries and retry)...")
    sys.exit(1)

# ===========================
# STEP 6: UpdateDBCfg
# ===========================
ok, log = run_1c(["/UpdateDBCfg"], "update-with-form2.log", "UpdateDBCfg with ФормаГруппы")
if not ok:
    print(f"\nFAILED UpdateDBCfg! Log: {log}")
    sys.exit(1)

print("\n\n=== SUCCESS! ФормаГруппы deployed! ===\n")
