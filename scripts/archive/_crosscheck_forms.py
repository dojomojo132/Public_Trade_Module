# -*- coding: utf-8 -*-
"""Cross-check: Forms in ChildObjects XML vs Forms in CDI."""
import pathlib
import xml.etree.ElementTree as ET
import re

BASE = pathlib.Path(r'D:\Git\Public_Trade_Module\Конфигурация\Проверка')
NS_CDI = '{http://v8.1c.ru/8.3/xcf/dumpinfo}'
NS_MD = '{http://v8.1c.ru/8.3/MDClasses}'

# Parse CDI
cdi = ET.parse(str(BASE / 'ConfigDumpInfo.xml'))
cdi_names = set()
for elem in cdi.getroot().iter(NS_CDI + 'Metadata'):
    cdi_names.add(elem.get('name', ''))

# Parse Configuration.xml to get all objects
config = ET.parse(str(BASE / 'Configuration.xml'))
config_root = config.getroot()

# Map metadata type tags to CDI prefixes and disk folders
type_map = {
    'Document': ('Document', 'Documents'),
    'Catalog': ('Catalog', 'Catalogs'),
    'DataProcessor': ('DataProcessor', 'DataProcessors'),
    'Report': ('Report', 'Reports'),
}

print("=" * 70)
print("CROSS-CHECK: Forms in Object XML vs CDI")
print("=" * 70)

issues_found = 0

for xml_tag, (cdi_prefix, disk_folder) in type_map.items():
    folder = BASE / disk_folder
    if not folder.exists():
        continue
    
    for xml_file in folder.glob('*.xml'):
        if not xml_file.is_file():
            continue
        obj_name = xml_file.stem  # e.g., 'СписаниеТовара'
        
        try:
            tree = ET.parse(str(xml_file))
            root = tree.getroot()
        except Exception as e:
            print(f"  ERROR parsing {xml_file.name}: {e}")
            continue
        
        # Find all <Form> elements in ChildObjects
        forms_in_xml = []
        for form_elem in root.iter(NS_MD + 'Form'):
            form_name = form_elem.text
            if form_name:
                forms_in_xml.append(form_name)
        
        if not forms_in_xml:
            continue
        
        for form_name in forms_in_xml:
            cdi_form_name = f'{cdi_prefix}.{obj_name}.Form.{form_name}'
            cdi_form_inner = f'{cdi_form_name}.Form'
            
            has_cdi_form = cdi_form_name in cdi_names
            has_cdi_inner = cdi_form_inner in cdi_names
            
            # Check files on disk
            desc_file = folder / obj_name / 'Forms' / f'{form_name}.xml'
            form_dir = folder / obj_name / 'Forms' / form_name
            ext_form = form_dir / 'Ext' / 'Form.xml'
            
            has_desc = desc_file.exists()
            has_dir = form_dir.exists()
            has_ext_form = ext_form.exists()
            
            problems = []
            if not has_cdi_form:
                problems.append("NO CDI entry for form")
            if not has_cdi_inner:
                problems.append("NO CDI .Form entry")
            if not has_desc:
                problems.append("NO descriptor .xml")
            if not has_dir:
                problems.append("NO form directory")
            if not has_ext_form:
                problems.append("NO Ext/Form.xml")
            
            if problems:
                print(f"\n  *** {cdi_prefix}.{obj_name} → Form '{form_name}':")
                for p in problems:
                    print(f"      - {p}")
                issues_found += 1
            else:
                print(f"  OK: {cdi_prefix}.{obj_name}.Form.{form_name}")

print(f"\n{'=' * 70}")
print(f"REVERSE CHECK: CDI form entries without XML reference")
print(f"{'=' * 70}")

# Find all CDI form entries
cdi_forms = {}
for elem in cdi.getroot().iter(NS_CDI + 'Metadata'):
    name = elem.get('name', '')
    if '.Form.' in name and not name.endswith('.Form'):
        # This is a form CDI entry like DataProcessor.X.Form.Y
        # Skip inner Form entries like X.Form.Y.Form
        parts = name.split('.')
        # Check it's exactly Type.Object.Form.FormName 
        if len(parts) == 4 and parts[2] == 'Form':
            cdi_forms[name] = elem.get('id', '')

for cdi_form_entry, cdi_id in sorted(cdi_forms.items()):
    parts = cdi_form_entry.split('.')
    obj_type_1c = parts[0]
    obj_name = parts[1]
    form_name = parts[3]
    
    disk_folder = type_map.get(obj_type_1c, (None, None))[1]
    if not disk_folder:
        continue
    
    # Check if this form is listed in the parent object's ChildObjects
    obj_xml = BASE / disk_folder / f'{obj_name}.xml'
    if not obj_xml.exists():
        print(f"  *** {cdi_form_entry}: PARENT XML NOT FOUND ({obj_xml.name})")
        issues_found += 1
        continue
    
    tree = ET.parse(str(obj_xml))
    root = tree.getroot()
    
    form_found_in_xml = False
    for form_elem in root.iter(NS_MD + 'Form'):
        if form_elem.text == form_name:
            form_found_in_xml = True
            break
    
    if not form_found_in_xml:
        print(f"  *** {cdi_form_entry}: CDI entry exists but NOT in parent XML ChildObjects!")
        issues_found += 1
    else:
        pass  # Already checked above

print(f"\n{'=' * 70}")
print(f"Total issues found: {issues_found}")
print(f"{'=' * 70}")
