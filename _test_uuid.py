# -*- coding: utf-8 -*-
"""
Test with proper random UUID and also updated Номенклатура configVersion.
Also check if our UUID conflicts with anything.
"""
import os
import pathlib
import subprocess
import shutil
import re
import uuid

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
    print(f"  [{desc}]")
    result = subprocess.run(cmd, timeout=300)
    log_text = ""
    if pathlib.Path(log_file).exists():
        log_text = pathlib.Path(log_file).read_text(encoding='utf-8-sig').strip()
    status = "OK" if result.returncode == 0 else "FAIL"
    if log_text and result.returncode != 0:
        print(f"  {status}: {log_text[:300]}")
    elif log_text:
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
    cdi_c = re.sub(r'\s*<Metadata name="Catalog\.Номенклатура\.Form\.ФормаГруппы[^"]*"[^/]*/>', '', cdi_c)
    cdi_c = cdi_c.replace('aa3c09fdda956d4599e92d82f097502e00000000',
                           'aa3c09fdda956d4599e92d82f097502f00000000')
    pathlib.Path(cdi).write_text(cdi_c, encoding='utf-8-sig')

# Check UUID conflict
print("Checking UUID conflict...")
cdi_path = os.path.join(dump_dir, "ConfigDumpInfo.xml")
cdi_content = pathlib.Path(cdi_path).read_text(encoding='utf-8-sig')
old_uuid = "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e"
count = cdi_content.count(old_uuid)
print(f"  UUID '{old_uuid}' appears {count} times in CDI")

# Search in all XML files
all_xml_hits = 0
for root, dirs, files in os.walk(dump_dir):
    for f in files:
        if f.endswith('.xml'):
            fpath = os.path.join(root, f)
            try:
                fc = pathlib.Path(fpath).read_text(encoding='utf-8-sig')
                if old_uuid in fc:
                    rel = os.path.relpath(fpath, dump_dir)
                    all_xml_hits += 1
                    print(f"  Found in: {rel}")
            except:
                pass
print(f"  Total files with UUID: {all_xml_hits}")

# Generate a proper random UUID  
new_uuid = str(uuid.uuid4())
new_cv1 = uuid.uuid4().hex + "00000000"
new_cv2 = uuid.uuid4().hex + "00000000"
new_nom_cv = uuid.uuid4().hex + "00000000"
print(f"\nNew UUID: {new_uuid}")
print(f"New configVersions: {new_cv1}, {new_cv2}")
print(f"New Номенклатура configVersion: {new_nom_cv}")

# ================================
# TEST 8: Random UUID + updated configVersions
# ================================
print("\n" + "=" * 60)
print("TEST 8: Proper random UUID + updated Номенклатура configVersion")
print("=" * 60)

run_1c(["/RestoreIB", dt_file], "t8-restore.log", "Restore ИБ")
reset_dump()

# Create form files with new UUID
nom_forms = os.path.join(dump_dir, "Catalogs", "Номенклатура", "Forms")

# Descriptor with new UUID
descriptor = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<Form uuid="{new_uuid}">
		<Properties>
			<Name>ФормаГруппы</Name>
			<Synonym>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Форма группы</v8:content>
				</v8:item>
			</Synonym>
			<Comment/>
			<FormType>Managed</FormType>
			<IncludeHelpInContents>false</IncludeHelpInContents>
			<UsePurposes>
				<v8:Value xsi:type="app:ApplicationUsePurpose">PlatformApplication</v8:Value>
				<v8:Value xsi:type="app:ApplicationUsePurpose">MobilePlatformApplication</v8:Value>
			</UsePurposes>
		</Properties>
	</Form>
</MetaDataObject>
'''
pathlib.Path(os.path.join(nom_forms, "ФормаГруппы.xml")).write_text(descriptor, encoding='utf-8-sig')
print("  Created descriptor with new UUID")

# Minimal Form.xml
form_dir = os.path.join(nom_forms, "ФормаГруппы", "Ext")
module_dir = os.path.join(form_dir, "Form")
os.makedirs(module_dir, exist_ok=True)

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
pathlib.Path(os.path.join(form_dir, "Form.xml")).write_text(minimal_form, encoding='utf-8-sig')
pathlib.Path(os.path.join(module_dir, "Module.bsl")).write_text('\n', encoding='utf-8-sig')
print("  Created minimal Form.xml and Module.bsl")

# Update CDI with new UUID and updated Номенклатура configVersion
cdi_c = pathlib.Path(cdi_path).read_text(encoding='utf-8-sig')

# Change Номенклатура configVersion
cdi_c = cdi_c.replace(
    'aa3c09fdda956d4599e92d82f097502f00000000',
    new_nom_cv
)

# Add form CDI entries
insert = f'''
		<Metadata name="Catalog.Номенклатура.Form.ФормаГруппы" id="{new_uuid}" configVersion="{new_cv1}"/>
		<Metadata name="Catalog.Номенклатура.Form.ФормаГруппы.Form" id="{new_uuid}.0" configVersion="{new_cv2}"/>'''
pattern = r'(<Metadata name="Catalog\.Номенклатура\.Form\.ФормаЭлемента\.Form"[^/]*/>)'
match = re.search(pattern, cdi_c)
if match:
    pos = match.end()
    cdi_c = cdi_c[:pos] + insert + cdi_c[pos:]
pathlib.Path(cdi_path).write_text(cdi_c, encoding='utf-8-sig')
print("  Updated CDI with new UUID + configVersions")

# Update ChildObjects
nom_xml = os.path.join(dump_dir, "Catalogs", "Номенклатура.xml")
content = pathlib.Path(nom_xml).read_text(encoding='utf-8-sig')
content = content.replace("<Form>ФормаСписка</Form>", 
                          "<Form>ФормаСписка</Form>\n\t\t\t<Form>ФормаГруппы</Form>")
pathlib.Path(nom_xml).write_text(content, encoding='utf-8-sig')
print("  Updated ChildObjects")

ok = run_1c(["/LoadConfigFromFiles", dump_dir], "t8-load.log", "Load with new UUID")
print(f"\n  Result: {'OK' if ok else 'FAIL'}")

if not ok:
    # TEST 9: Maybe we need to change configVersion in Configuration.xml too
    print("\n" + "=" * 60)
    print("TEST 9: Also check if Configuration.xml needs update")
    print("=" * 60)
    
    config_xml = os.path.join(dump_dir, "Configuration.xml")
    if os.path.exists(config_xml):
        config_content = pathlib.Path(config_xml).read_text(encoding='utf-8-sig')
        if "Номенклатура" in config_content:
            print("  Номенклатура IS in Configuration.xml")
            # Check if Configuration.xml also has configVersion in CDI
            if "Configuration" in cdi_c:
                config_cv_match = re.search(r'name="Configuration"[^>]*configVersion="([^"]+)"', cdi_c)
                if config_cv_match:
                    print(f"  Configuration configVersion: {config_cv_match.group(1)}")
    
    # Also check: are there any issues with BOM/encoding?
    for fname in ["ФормаГруппы.xml", "ФормаГруппы/Ext/Form.xml", "ФормаГруппы/Ext/Form/Module.bsl"]:
        fpath = os.path.join(nom_forms, fname)
        if os.path.exists(fpath):
            with open(fpath, 'rb') as f:
                first3 = f.read(3)
            has_bom = first3 == b'\xef\xbb\xbf'
            print(f"  {fname}: BOM={has_bom}")

if ok:
    ok2 = run_1c(["/UpdateDBCfg"], "t8-update.log", "UpdateDBCfg")
    print(f"  UpdateDBCfg: {'OK' if ok2 else 'FAIL'}")
