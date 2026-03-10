# -*- coding: utf-8 -*-
"""
More granular isolation tests to find exact cause.
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
form_backup = r"D:\Git\Public_Trade_Module\_form_temp_backup"

def run_1c(args, log_name, desc):
    log_file = os.path.join(log_dir, log_name)
    cmd = [exe, "DESIGNER", "/F", ib_path] + args + [
        "/DisableStartupDialogs", "/DisableStartupMessages", "/Out", log_file
    ]
    print(f"  [{desc}]")
    result = subprocess.run(cmd, timeout=300)
    log_text = ""
    if pathlib.Path(log_file).exists():
        log_text = pathlib.Path(log_file).read_text(encoding='utf-8-sig').strip()
    status = "OK" if result.returncode == 0 else "FAIL"
    if log_text and result.returncode != 0:
        print(f"  {status}: {log_text[:200]}")
    else:
        print(f"  {status}")
    return result.returncode == 0

def reset_dump():
    nom_forms = os.path.join(dump_dir, "Catalogs", "Номенклатура", "Forms")
    fg_xml = os.path.join(nom_forms, "ФормаГруппы.xml")
    fg_dir = os.path.join(nom_forms, "ФормаГруппы")
    if os.path.exists(fg_xml):
        os.remove(fg_xml)
    if os.path.isdir(fg_dir):
        shutil.rmtree(fg_dir)
    
    nom_xml = os.path.join(dump_dir, "Catalogs", "Номенклатура.xml")
    content = pathlib.Path(nom_xml).read_text(encoding='utf-8-sig')
    content = re.sub(r'\s*<DefaultFolderForm>[^<]+</DefaultFolderForm>', '', content)
    content = re.sub(r'\s*<Form>ФормаГруппы</Form>', '', content)
    pathlib.Path(nom_xml).write_text(content, encoding='utf-8-sig')
    
    cdi = os.path.join(dump_dir, "ConfigDumpInfo.xml")
    cdi_c = pathlib.Path(cdi).read_text(encoding='utf-8-sig')
    cdi_c = re.sub(r'\s*<Metadata name="Catalog\.Номенклатура\.Form\.ФормаГруппы"[^/]*/>', '', cdi_c)
    cdi_c = re.sub(r'\s*<Metadata name="Catalog\.Номенклатура\.Form\.ФормаГруппы\.Form"[^/]*/>', '', cdi_c)
    cdi_c = cdi_c.replace('aa3c09fdda956d4599e92d82f097502e00000000',
                           'aa3c09fdda956d4599e92d82f097502f00000000')
    pathlib.Path(cdi).write_text(cdi_c, encoding='utf-8-sig')

def add_cdi_entries():
    cdi_path = os.path.join(dump_dir, "ConfigDumpInfo.xml")
    cdi_c = pathlib.Path(cdi_path).read_text(encoding='utf-8-sig')
    if "Catalog.Номенклатура.Form.ФормаГруппы" not in cdi_c:
        insert = '''
		<Metadata name="Catalog.Номенклатура.Form.ФормаГруппы" id="b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e" configVersion="a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d600000000"/>
		<Metadata name="Catalog.Номенклатура.Form.ФормаГруппы.Form" id="b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e.0" configVersion="b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e700000000"/>'''
        pattern = r'(<Metadata name="Catalog\.Номенклатура\.Form\.ФормаЭлемента\.Form"[^/]*/>)'
        match = re.search(pattern, cdi_c)
        if match:
            pos = match.end()
            cdi_c = cdi_c[:pos] + insert + cdi_c[pos:]
    pathlib.Path(cdi_path).write_text(cdi_c, encoding='utf-8-sig')

def add_child_objects_entry():
    nom_xml = os.path.join(dump_dir, "Catalogs", "Номенклатура.xml")
    content = pathlib.Path(nom_xml).read_text(encoding='utf-8-sig')
    if "<Form>ФормаГруппы</Form>" not in content:
        content = content.replace("<Form>ФормаСписка</Form>", 
                                  "<Form>ФормаСписка</Form>\n\t\t\t<Form>ФормаГруппы</Form>")
    pathlib.Path(nom_xml).write_text(content, encoding='utf-8-sig')

def add_form_files():
    nom_forms = os.path.join(dump_dir, "Catalogs", "Номенклатура", "Forms")
    shutil.copy2(os.path.join(form_backup, "ФормаГруппы.xml"), os.path.join(nom_forms, "ФормаГруппы.xml"))
    dst = os.path.join(nom_forms, "ФормаГруппы")
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(os.path.join(form_backup, "ФормаГруппы"), dst)

def add_minimal_form_files():
    """Create minimal form files based on working ФормаЭлемента structure"""
    nom_forms = os.path.join(dump_dir, "Catalogs", "Номенклатура", "Forms")
    
    # Copy the same descriptor (this is identical to working forms)
    shutil.copy2(os.path.join(form_backup, "ФормаГруппы.xml"), os.path.join(nom_forms, "ФормаГруппы.xml"))
    
    # Create minimal Form.xml based on the simplest working form
    form_dir = os.path.join(nom_forms, "ФормаГруппы", "Ext")
    module_dir = os.path.join(form_dir, "Form")
    os.makedirs(module_dir, exist_ok=True)
    
    # Minimal Form.xml - just the required structure
    minimal_form = '''<?xml version="1.0" encoding="UTF-8"?>
<Form xmlns="http://v8.1c.ru/8.3/xcf/logform" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:dcscor="http://v8.1c.ru/8.1/data-composition-system/core" xmlns:dcssch="http://v8.1c.ru/8.1/data-composition-system/schema" xmlns:dcsset="http://v8.1c.ru/8.1/data-composition-system/settings" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<AutoCommandBar name="ФормаКоманднаяПанель" id="-1"/>
	<Attributes>
		<Attribute name="Объект" id="1">
			<Type>
				<v8:Type>cfg:CatalogObject.Номенклатура</v8:Type>
			</Type>
			<MainAttribute>true</MainAttribute>
			<SavedData>true</SavedData>
		</Attribute>
	</Attributes>
</Form>
'''
    # Write with BOM
    pathlib.Path(os.path.join(form_dir, "Form.xml")).write_text(minimal_form, encoding='utf-8-sig')
    
    # Empty module
    pathlib.Path(os.path.join(module_dir, "Module.bsl")).write_text('\n', encoding='utf-8-sig')

# ================================
# TEST 4: ALL together (files + CDI + ChildObjects)
# ================================
print("=" * 60)
print("TEST 4: ALL components together")
print("=" * 60)
run_1c(["/RestoreIB", dt_file], "t4-restore.log", "Restore ИБ")
reset_dump()
add_form_files()
add_cdi_entries()
add_child_objects_entry()
ok = run_1c(["/LoadConfigFromFiles", dump_dir], "t4-load.log", "Load: files + CDI + ChildObjects")
print(f"  Result: {'OK' if ok else 'FAIL'}\n")

# ================================
# TEST 5: ChildObjects + CDI (no files)
# ================================
print("=" * 60)
print("TEST 5: ChildObjects + CDI, NO files")
print("=" * 60)
run_1c(["/RestoreIB", dt_file], "t5-restore.log", "Restore ИБ")
reset_dump()
add_cdi_entries()
add_child_objects_entry()
ok = run_1c(["/LoadConfigFromFiles", dump_dir], "t5-load.log", "Load: CDI + ChildObjects (no files)")
print(f"  Result: {'OK' if ok else 'FAIL'}\n")

# ================================
# TEST 6: Form files ONLY (no CDI, no ChildObjects)
# ================================
print("=" * 60)
print("TEST 6: Form files ONLY (no CDI, no ChildObjects)")
print("=" * 60)
run_1c(["/RestoreIB", dt_file], "t6-restore.log", "Restore ИБ")
reset_dump()
add_form_files()
ok = run_1c(["/LoadConfigFromFiles", dump_dir], "t6-load.log", "Load: files only")
print(f"  Result: {'OK' if ok else 'FAIL'}\n")

# ================================
# TEST 7: MINIMAL form files + CDI + ChildObjects
# ================================
print("=" * 60)
print("TEST 7: MINIMAL form + CDI + ChildObjects")
print("=" * 60)
run_1c(["/RestoreIB", dt_file], "t7-restore.log", "Restore ИБ")
reset_dump()
add_minimal_form_files()
add_cdi_entries()
add_child_objects_entry()
ok = run_1c(["/LoadConfigFromFiles", dump_dir], "t7-load.log", "Load: minimal form + CDI + ChildObjects")
print(f"  Result: {'OK' if ok else 'FAIL'}\n")

print("\n=== ALL TESTS COMPLETE ===")
