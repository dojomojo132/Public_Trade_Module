# -*- coding: utf-8 -*-
"""
Full clean deploy approach:
1. Restore ИБ from stable 1Cv8.dt
2. Remove ФормаГруппы files from Проверка temporarily
3. Load base config (should work)
4. DumpConfigToFiles to verify integrity
5. Add ФормаГруппы back
6. Load with form
7. Check
"""
import subprocess
import pathlib
import shutil
import os
import sys

exe = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
ib_path = r"D:\Confiq\Public Trade Module"
proverka = r"D:\Git\Public_Trade_Module\Конфигурация\Проверка"
log_dir = r"D:\Git\Public_Trade_Module\Документация\Валидация\logs"
dt_file = r"D:\Git\Public_Trade_Module\1Cv8.dt"

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

# Temp storage for our form files
backup_dir = r"D:\Git\Public_Trade_Module\_form_temp_backup"

nom_forms = os.path.join(proverka, "Catalogs", "Номенклатура", "Forms")
nom_xml = os.path.join(proverka, "Catalogs", "Номенклатура.xml")
cdi_xml = os.path.join(proverka, "ConfigDumpInfo.xml")

# ===========================
# STEP 0: Save our form files aside
# ===========================
print("STEP 0: Saving ФормаГруппы files aside...")
if os.path.exists(backup_dir):
    shutil.rmtree(backup_dir)
os.makedirs(backup_dir)

# Save ФормаГруппы descriptor
fg_desc = os.path.join(nom_forms, "ФормаГруппы.xml")
fg_dir = os.path.join(nom_forms, "ФормаГруппы")
if os.path.exists(fg_desc):
    shutil.copy2(fg_desc, os.path.join(backup_dir, "ФормаГруппы.xml"))
    print(f"  Saved: ФормаГруппы.xml")
if os.path.isdir(fg_dir):
    shutil.copytree(fg_dir, os.path.join(backup_dir, "ФормаГруппы"))
    print(f"  Saved: ФормаГруппы/ folder")

# Save modified Номенклатура.xml and ConfigDumpInfo.xml
shutil.copy2(nom_xml, os.path.join(backup_dir, "Номенклатура.xml"))
shutil.copy2(cdi_xml, os.path.join(backup_dir, "ConfigDumpInfo.xml"))
print(f"  Saved: Номенклатура.xml, ConfigDumpInfo.xml")

# ===========================
# STEP 1: Remove form files from Проверка
# ===========================
print("\nSTEP 1: Removing ФормаГруппы from Проверка...")
if os.path.exists(fg_desc):
    os.remove(fg_desc)
    print(f"  Removed: ФормаГруппы.xml")
if os.path.isdir(fg_dir):
    shutil.rmtree(fg_dir)
    print(f"  Removed: ФормаГруппы/ folder")

# Restore original Номенклатура.xml (without DefaultFolderForm and ФормаГруппы form entry)
# Read from base Конфигурация original
base_nom_xml = os.path.join(r"D:\Git\Public_Trade_Module\Конфигурация", "Catalogs", "Номенклатура.xml")
# Actually we need the version WITHOUT our changes. Let me read and remove our additions.
content = pathlib.Path(nom_xml).read_text(encoding='utf-8-sig')
# Remove DefaultFolderForm line
import re
content = re.sub(r'\s*<DefaultFolderForm>[^<]+</DefaultFolderForm>\n?', '', content)
# Remove ФормаГруппы form entry
content = re.sub(r'\s*<Form>ФормаГруппы</Form>\n?', '', content)
pathlib.Path(nom_xml).write_text(content, encoding='utf-8-sig')
print(f"  Fixed: Номенклатура.xml (removed ФормаГруппы references)")

# Restore original ConfigDumpInfo.xml (without ФормаГруппы entries)
cdi_content = pathlib.Path(cdi_xml).read_text(encoding='utf-8-sig')
cdi_content = re.sub(r'\s*<Metadata name="Catalog\.Номенклатура\.Form\.ФормаГруппы"[^/]*/>\n?', '', cdi_content)
cdi_content = re.sub(r'\s*<Metadata name="Catalog\.Номенклатура\.Form\.ФормаГруппы\.Form"[^/]*/>\n?', '', cdi_content)
pathlib.Path(cdi_xml).write_text(cdi_content, encoding='utf-8-sig')
print(f"  Fixed: ConfigDumpInfo.xml (removed ФормаГруппы entries)")

# ===========================
# STEP 2: Restore ИБ from stable dt
# ===========================
ok, _ = run_1c(["/RestoreIB", dt_file], "restore-clean.log", "Restore ИБ from 1Cv8.dt")
if not ok:
    print("FAILED to restore!")
    sys.exit(1)

# ===========================
# STEP 3: Load base config (without form)
# ===========================
ok, _ = run_1c(["/LoadConfigFromFiles", proverka], "load-base-clean.log", "Load config WITHOUT ФормаГруппы")
if not ok:
    print("FAILED to load base config!")
    sys.exit(1)

# ===========================
# STEP 4: UpdateDBCfg
# ===========================
ok, _ = run_1c(["/UpdateDBCfg"], "update-base-clean.log", "UpdateDBCfg (base)")
if not ok:
    print("FAILED UpdateDBCfg!")
    sys.exit(1)

# ===========================
# STEP 5: DumpConfigToFiles to verify integrity
# ===========================
dump_dir = r"D:\Git\Public_Trade_Module\Конфигурация\_DumpVerify"
if os.path.exists(dump_dir):
    shutil.rmtree(dump_dir)
os.makedirs(dump_dir)
ok, _ = run_1c(["/DumpConfigToFiles", dump_dir], "dump-verify.log", "DumpConfigToFiles (verify base integrity)")
if not ok:
    print("FAILED DumpConfigToFiles - base config has integrity issues!")
    # Try to continue anyway
else:
    print("  Base config integrity: OK!")
    # Check CDI from dump
    dump_cdi = os.path.join(dump_dir, "ConfigDumpInfo.xml")
    if os.path.exists(dump_cdi):
        dump_cdi_content = pathlib.Path(dump_cdi).read_text(encoding='utf-8-sig')
        print(f"  Dump CDI size: {len(dump_cdi_content)} bytes")

print("\n\n=== BASE CONFIG TEST COMPLETE ===\n")
