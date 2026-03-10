# -*- coding: utf-8 -*-
"""
Full isolation test:
1. Restore ИБ from dt
2. Load ORIGINAL dump (no changes) - should work
3. If works, try adding JUST the form files (no CDI, no Номенклатура.xml changes)
4. If fails, try adding JUST CDI entries (no files, no Номенклатура.xml)
5. Find which component causes the failure
"""
import os
import pathlib
import subprocess
import shutil
import sys
import re

exe = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
ib_path = r"D:\Confiq\Public Trade Module"
dt_file = r"D:\Git\Public_Trade_Module\1Cv8.dt"
log_dir = r"D:\Git\Public_Trade_Module\Документация\Валидация\logs"
dump_dir = r"D:\Git\Public_Trade_Module\Конфигурация\_DumpVerify"

def run_1c(args, log_name, desc):
    log_file = os.path.join(log_dir, log_name)
    cmd = [exe, "DESIGNER", "/F", ib_path] + args + [
        "/DisableStartupDialogs", "/DisableStartupMessages", "/Out", log_file
    ]
    print(f"\n  [{desc}]")
    result = subprocess.run(cmd, timeout=300)
    log_text = ""
    if pathlib.Path(log_file).exists():
        log_text = pathlib.Path(log_file).read_text(encoding='utf-8-sig').strip()
    status = "OK" if result.returncode == 0 else "FAIL"
    print(f"  {status}: {log_text[:200] if log_text else '[empty]'}")
    return result.returncode == 0

# Helper to reset dump to clean state
def reset_dump():
    """Remove all ФормаГруппы traces from dump"""
    nom_forms = os.path.join(dump_dir, "Catalogs", "Номенклатура", "Forms")
    fg_xml = os.path.join(nom_forms, "ФормаГруппы.xml")
    fg_dir = os.path.join(nom_forms, "ФормаГруппы")
    if os.path.exists(fg_xml):
        os.remove(fg_xml)
    if os.path.isdir(fg_dir):
        shutil.rmtree(fg_dir)
    
    # Remove from Номенклатура.xml
    nom_xml = os.path.join(dump_dir, "Catalogs", "Номенклатура.xml")
    content = pathlib.Path(nom_xml).read_text(encoding='utf-8-sig')
    content = re.sub(r'\s*<DefaultFolderForm>[^<]+</DefaultFolderForm>', '', content)
    content = re.sub(r'\s*<Form>ФормаГруппы</Form>', '', content)
    pathlib.Path(nom_xml).write_text(content, encoding='utf-8-sig')
    
    # Remove from CDI
    cdi = os.path.join(dump_dir, "ConfigDumpInfo.xml")
    cdi_c = pathlib.Path(cdi).read_text(encoding='utf-8-sig')
    cdi_c = re.sub(r'\s*<Metadata name="Catalog\.Номенклатура\.Form\.ФормаГруппы"[^/]*/>', '', cdi_c)
    cdi_c = re.sub(r'\s*<Metadata name="Catalog\.Номенклатура\.Form\.ФормаГруппы\.Form"[^/]*/>', '', cdi_c)
    # Restore original configVersion for Номенклатура
    cdi_c = cdi_c.replace(
        'aa3c09fdda956d4599e92d82f097502e00000000',
        'aa3c09fdda956d4599e92d82f097502f00000000'
    )
    pathlib.Path(cdi).write_text(cdi_c, encoding='utf-8-sig')

# ================================
# TEST 1: Clean load check
# ================================
print("=" * 60)
print("TEST 1: Load original clean dump (no ФормаГруппы changes)")
print("=" * 60)

# Restore ИБ
run_1c(["/RestoreIB", dt_file], "t1-restore.log", "Restore ИБ")

# Clean dump
reset_dump()

# Load
ok = run_1c(["/LoadConfigFromFiles", dump_dir], "t1-load.log", "Load clean dump")
if not ok:
    print("\n!!! Clean dump load FAILED - base issue exists!")
    
    # Maybe the dump was corrupted by our previous edits. Re-dump.
    print("\nRe-dumping from clean ИБ...")
    proverka = r"D:\Git\Public_Trade_Module\Конфигурация\Проверка"
    
    # First check if Проверка is clean
    proverka_fg = os.path.join(proverka, "Catalogs", "Номенклатура", "Forms", "ФормаГруппы.xml")
    proverka_fg_dir = os.path.join(proverka, "Catalogs", "Номенклатура", "Forms", "ФормаГруппы")
    if os.path.exists(proverka_fg):
        os.remove(proverka_fg)
        print(f"  Removed ФормаГруппы.xml from Проверка")
    if os.path.isdir(proverka_fg_dir):
        shutil.rmtree(proverka_fg_dir)
        print(f"  Removed ФормаГруппы folder from Проверка")
    
    # Fix Проверка Номенклатура.xml and CDI
    prov_nom = os.path.join(proverka, "Catalogs", "Номенклатура.xml")
    prov_cdi = os.path.join(proverka, "ConfigDumpInfo.xml")
    for fpath in [prov_nom, prov_cdi]:
        c = pathlib.Path(fpath).read_text(encoding='utf-8-sig')
        c = re.sub(r'\s*<DefaultFolderForm>[^<]+</DefaultFolderForm>', '', c)
        c = re.sub(r'\s*<Form>ФормаГруппы</Form>', '', c)
        c = re.sub(r'\s*<Metadata name="Catalog\.Номенклатура\.Form\.ФормаГруппы"[^/]*/>', '', c)
        c = re.sub(r'\s*<Metadata name="Catalog\.Номенклатура\.Form\.ФормаГруппы\.Form"[^/]*/>', '', c)
        pathlib.Path(fpath).write_text(c, encoding='utf-8-sig')
    print(f"  Fixed Проверка Номенклатура.xml and CDI")
    
    # Load from clean Проверка
    ok2 = run_1c(["/LoadConfigFromFiles", proverka], "t1-load-proverka.log", "Load from clean Проверка")
    if ok2:
        # Now dump fresh
        if os.path.exists(dump_dir):
            shutil.rmtree(dump_dir)
        os.makedirs(dump_dir)
        run_1c(["/DumpConfigToFiles", dump_dir], "t1-dump-fresh.log", "Fresh dump")
        print("  Fresh dump created")
else:
    print("\n  Clean dump loads OK!")

# ================================  
# TEST 2: Add JUST form files + ChildObjects entry (no CDI entries)
# ================================
print("\n" + "=" * 60)
print("TEST 2: Add form files + ChildObjects, NO CDI entries")
print("=" * 60)

# Restore ИБ
run_1c(["/RestoreIB", dt_file], "t2-restore.log", "Restore ИБ")

# Start from clean dump
reset_dump()

# Add form files
form_backup = r"D:\Git\Public_Trade_Module\_form_temp_backup"
nom_forms = os.path.join(dump_dir, "Catalogs", "Номенклатура", "Forms")
shutil.copy2(os.path.join(form_backup, "ФормаГруппы.xml"), os.path.join(nom_forms, "ФормаГруппы.xml"))
shutil.copytree(os.path.join(form_backup, "ФормаГруппы"), os.path.join(nom_forms, "ФормаГруппы"))

# Add ChildObjects entry
nom_xml = os.path.join(dump_dir, "Catalogs", "Номенклатура.xml")
content = pathlib.Path(nom_xml).read_text(encoding='utf-8-sig')
content = content.replace("<Form>ФормаСписка</Form>", "<Form>ФормаСписка</Form>\n\t\t\t<Form>ФормаГруппы</Form>")
pathlib.Path(nom_xml).write_text(content, encoding='utf-8-sig')

ok3 = run_1c(["/LoadConfigFromFiles", dump_dir], "t2-load.log", "Load with files only (no CDI)")
print(f"\n  Result: {'OK' if ok3 else 'FAIL'}")

# ================================
# TEST 3: Add JUST CDI entries (no files, no ChildObjects)
# ================================
print("\n" + "=" * 60)
print("TEST 3: Add JUST CDI entries, NO files / ChildObjects")
print("=" * 60)

run_1c(["/RestoreIB", dt_file], "t3-restore.log", "Restore ИБ")
reset_dump()

# Add CDI entries only
cdi_path = os.path.join(dump_dir, "ConfigDumpInfo.xml")
cdi_c = pathlib.Path(cdi_path).read_text(encoding='utf-8-sig')
insert = '''
		<Metadata name="Catalog.Номенклатура.Form.ФормаГруппы" id="b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e" configVersion="a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d600000000"/>
		<Metadata name="Catalog.Номенклатура.Form.ФормаГруппы.Form" id="b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e.0" configVersion="b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e700000000"/>'''
pattern = r'(<Metadata name="Catalog\.Номенклатура\.Form\.ФормаЭлемента\.Form"[^/]*/>)'
match = re.search(pattern, cdi_c)
if match:
    pos = match.end()
    cdi_c = cdi_c[:pos] + insert + cdi_c[pos:]
pathlib.Path(cdi_path).write_text(cdi_c, encoding='utf-8-sig')

ok4 = run_1c(["/LoadConfigFromFiles", dump_dir], "t3-load.log", "Load with CDI only (no files)")
print(f"\n  Result: {'OK' if ok4 else 'FAIL'}")

print("\n\n=== ISOLATION TEST COMPLETE ===")
