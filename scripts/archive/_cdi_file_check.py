# -*- coding: utf-8 -*-
"""Check EVERY CDI entry with configVersion maps to an actual file."""
import pathlib
import xml.etree.ElementTree as ET

BASE = pathlib.Path(r'D:\Git\Public_Trade_Module\Конфигурация\Проверка')
NS_CDI = '{http://v8.1c.ru/8.3/xcf/dumpinfo}'

cdi = ET.parse(str(BASE / 'ConfigDumpInfo.xml'))

TYPE_TO_FOLDER = {
    'AccumulationRegister': 'AccumulationRegisters',
    'InformationRegister': 'InformationRegisters',
    'Catalog': 'Catalogs',
    'Document': 'Documents',
    'Enum': 'Enums',
    'Report': 'Reports',
    'DataProcessor': 'DataProcessors',
    'CommonModule': 'CommonModules',
    'Constant': 'Constants',
    'Subsystem': 'Subsystems',
    'Role': 'Roles',
    'Language': 'Languages',
    'CommonTemplate': 'CommonTemplates',
    'CommonPicture': 'CommonPictures',
    'Style': 'Styles',
    'StyleItem': 'StyleItems',
}

print("=" * 70)
print("CDI FILE MAPPING CHECK")
print("=" * 70)

issues = 0
checked = 0

for elem in cdi.getroot().iter(NS_CDI + 'Metadata'):
    name = elem.get('name', '')
    cv = elem.get('configVersion', '')
    
    if not cv:
        continue  # No configVersion = no file to check
    
    checked += 1
    parts = name.split('.')
    
    # Skip Configuration root entries
    if parts[0] == 'Configuration':
        # Configuration.X → Configuration.xml
        # Configuration.X.ManagedApplicationModule → Ext/ManagedApplicationModule.bsl
        # Configuration.X.ClientApplicationInterface → special
        if len(parts) == 2:
            f = BASE / 'Configuration.xml'
            if not f.exists():
                print(f"  MISSING: {name} -> Configuration.xml")
                issues += 1
        elif parts[-1] == 'ManagedApplicationModule':
            f = BASE / 'Ext' / 'ManagedApplicationModule.bsl'
            if not f.exists():
                print(f"  MISSING: {name} -> Ext/ManagedApplicationModule.bsl")
                issues += 1
        elif parts[-1] == 'ClientApplicationInterface':
            # This maps to Ext/ClientApplicationInterface.xml or similar
            # It's a special entry, skip
            pass
        continue
    
    # Regular objects: Type.ObjectName...
    obj_type = parts[0]
    obj_name = parts[1]
    
    folder_name = TYPE_TO_FOLDER.get(obj_type)
    if not folder_name:
        print(f"  UNKNOWN TYPE: {name} (type={obj_type})")
        continue
    
    folder = BASE / folder_name
    
    if len(parts) == 2:
        # Top-level object: Type.Name → Folder/Name.xml
        f = folder / f'{obj_name}.xml'
        if not f.exists():
            print(f"  MISSING: {name} -> {f.relative_to(BASE)}")
            issues += 1
    
    elif parts[2] == 'Form' and len(parts) == 4:
        # Form descriptor: Type.Obj.Form.FormName → Folder/Obj/Forms/FormName.xml
        form_name = parts[3]
        f = folder / obj_name / 'Forms' / f'{form_name}.xml'
        if not f.exists():
            print(f"  MISSING: {name} -> {f.relative_to(BASE)}")
            issues += 1
    
    elif parts[2] == 'Form' and len(parts) == 5 and parts[4] == 'Form':
        # Form content: Type.Obj.Form.FormName.Form → Folder/Obj/Forms/FormName/Ext/Form.xml
        form_name = parts[3]
        f = folder / obj_name / 'Forms' / form_name / 'Ext' / 'Form.xml'
        if not f.exists():
            print(f"  MISSING: {name} -> {f.relative_to(BASE)}")
            issues += 1
    
    elif parts[-1] == 'ObjectModule':
        # Module: Type.Obj.ObjectModule → Folder/Obj/Ext/ObjectModule.bsl or .xml wrapper
        bsl = folder / obj_name / 'Ext' / 'ObjectModule.bsl'
        xml_w = folder / obj_name / 'Ext' / 'ObjectModule.xml'
        if not bsl.exists() and not xml_w.exists():
            print(f"  MISSING: {name} -> {bsl.relative_to(BASE)} or {xml_w.relative_to(BASE)}")
            issues += 1
    
    elif parts[-1] == 'ManagerModule':
        bsl = folder / obj_name / 'Ext' / 'ManagerModule.bsl'
        xml_w = folder / obj_name / 'Ext' / 'ManagerModule.xml'
        if not bsl.exists() and not xml_w.exists():
            print(f"  MISSING: {name} -> {bsl.relative_to(BASE)}")
            issues += 1
    
    elif parts[2] == 'Template' and len(parts) >= 4:
        # Template: Type.Obj.Template.TmplName → Folder/Obj/Templates/TmplName.xml or dir
        tmpl_name = parts[3]
        f_xml = folder / obj_name / 'Templates' / f'{tmpl_name}.xml'
        f_dir = folder / obj_name / 'Templates' / tmpl_name
        if not f_xml.exists() and not f_dir.exists():
            print(f"  MISSING: {name} -> Templates/{tmpl_name}.xml or dir")
            issues += 1
    
    elif parts[2] == 'Command':
        # Command: Type.Obj.Command.CmdName → various
        pass  # Commands don't always have separate files
    
    else:
        # Other entry types - skip for now
        pass

print(f"\nChecked {checked} CDI entries with configVersion")
print(f"Issues found: {issues}")

# ============================================================
# Check REVERSE: files on disk that have no CDI entry
# ============================================================
print()
print("=" * 70)
print("REVERSE: Files on disk without CDI entries")
print("=" * 70)

# Collect all CDI names for quick lookup
all_cdi_names = set()
for elem in cdi.getroot().iter(NS_CDI + 'Metadata'):
    all_cdi_names.add(elem.get('name', ''))

rev_issues = 0

for folder_type, cdi_prefix in [
    ('Documents', 'Document'), ('Catalogs', 'Catalog'),
    ('DataProcessors', 'DataProcessor'), ('Reports', 'Report')
]:
    folder = BASE / folder_type
    if not folder.exists():
        continue
    
    for xml_file in folder.glob('*.xml'):
        obj_name = xml_file.stem
        cdi_name = f'{cdi_prefix}.{obj_name}'
        
        obj_dir = folder / obj_name
        if not obj_dir.exists():
            continue
        
        # Check for ObjectModule
        bsl = obj_dir / 'Ext' / 'ObjectModule.bsl'
        xml_w = obj_dir / 'Ext' / 'ObjectModule.xml'
        modules_cdi = f'{cdi_name}.ObjectModule'
        
        if (bsl.exists() or xml_w.exists()) and modules_cdi not in all_cdi_names:
            print(f"  FILE W/O CDI: {folder_type}/{obj_name}/Ext/ObjectModule.* (no {modules_cdi} in CDI)")
            rev_issues += 1
        
        # Check for forms
        forms_dir = obj_dir / 'Forms'
        if forms_dir.exists():
            for form_desc in forms_dir.glob('*.xml'):
                form_name = form_desc.stem
                form_cdi = f'{cdi_name}.Form.{form_name}'
                if form_cdi not in all_cdi_names:
                    print(f"  FILE W/O CDI: {folder_type}/{obj_name}/Forms/{form_desc.name} (no {form_cdi} in CDI)")
                    rev_issues += 1

print(f"Reverse issues: {rev_issues}")
