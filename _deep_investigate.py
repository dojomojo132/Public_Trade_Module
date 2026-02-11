# -*- coding: utf-8 -*-
"""Deep investigation of 1C config structure for integrity issues."""
import pathlib
import xml.etree.ElementTree as ET

BASE = pathlib.Path(r'D:\Git\Public_Trade_Module\Конфигурация\Проверка')
NS_CDI = '{http://v8.1c.ru/8.3/xcf/dumpinfo}'
NS_MD = '{http://v8.1c.ru/8.3/MDClasses}'

print("=" * 70)
print("INVESTIGATION 1: Extra files in form directories")
print("=" * 70)

# Check all form directories for unexpected files
form_dirs_checked = 0
anomalies = []
for form_dir in BASE.rglob('Forms'):
    if not form_dir.is_dir():
        continue
    for item in form_dir.iterdir():
        if item.is_dir():
            # This should be the form's directory (e.g., ФормаДокумента/)
            # Inside it, there should be ONLY Ext/ subdirectory
            expected_contents = {'Ext'}
            actual_contents = {f.name for f in item.iterdir()}
            unexpected = actual_contents - expected_contents
            if unexpected:
                anomalies.append(f"  ANOMALY in {item.relative_to(BASE)}/")
                for u in unexpected:
                    full = item / u
                    if full.is_file():
                        anomalies.append(f"    EXTRA FILE: {u}")
                    else:
                        anomalies.append(f"    EXTRA DIR: {u}/")
            
            # Check Ext contents
            ext_dir = item / 'Ext'
            if ext_dir.exists():
                ext_contents = {f.name for f in ext_dir.iterdir()}
                expected_ext = {'Form.xml', 'Form'}
                unexpected_ext = ext_contents - expected_ext
                if unexpected_ext:
                    anomalies.append(f"  ANOMALY in {ext_dir.relative_to(BASE)}/")
                    for u in unexpected_ext:
                        anomalies.append(f"    EXTRA: {u}")
            form_dirs_checked += 1

print(f"Checked {form_dirs_checked} form directories")
if anomalies:
    print(f"Found {len(anomalies)} anomaly lines:")
    for a in anomalies:
        print(a)
else:
    print("No anomalies found")

print()
print("=" * 70)
print("INVESTIGATION 2: Module format consistency")
print("=" * 70)

# Check all Ext/ directories for module format
for obj_type in ['Documents', 'DataProcessors', 'Catalogs', 'Reports']:
    type_dir = BASE / obj_type
    if not type_dir.exists():
        continue
    for obj_dir in type_dir.iterdir():
        if not obj_dir.is_dir():
            continue
        ext_dir = obj_dir / 'Ext'
        if not ext_dir.exists():
            continue
        ext_files = {f.name for f in ext_dir.iterdir()}
        has_bsl = 'ObjectModule.bsl' in ext_files
        has_xml = 'ObjectModule.xml' in ext_files
        has_dir = (ext_dir / 'ObjectModule').is_dir()
        
        if has_xml and has_dir and not has_bsl:
            fmt = "XML-WRAPPER (ObjectModule.xml + ObjectModule/Module.bsl)"
        elif has_bsl and not has_xml:
            fmt = "FLAT-BSL (ObjectModule.bsl)"
        elif not has_bsl and not has_xml:
            fmt = "NO MODULE"
        else:
            fmt = f"MIXED: bsl={has_bsl} xml={has_xml} dir={has_dir}"
        
        if 'XML-WRAPPER' in fmt or 'MIXED' in fmt:
            print(f"  {obj_type}/{obj_dir.name}: {fmt}")

print()
print("=" * 70)
print("INVESTIGATION 3: CDI entries without matching files")
print("=" * 70)

cdi = ET.parse(str(BASE / 'ConfigDumpInfo.xml'))
cdi_root = cdi.getroot()

form_cdi_entries = []
for elem in cdi_root.iter(NS_CDI + 'Metadata'):
    name = elem.get('name', '')
    if '.Form.' in name and name.endswith('.Form'):
        # This is the inner Form entry (X.Y.Form.Z.Form)
        form_cdi_entries.append(name)

print(f"CDI entries with .Form.X.Form pattern: {len(form_cdi_entries)}")
for entry in sorted(form_cdi_entries):
    # Parse: Type.ObjName.Form.FormName.Form
    parts = entry.split('.')
    # Find the object type and name
    # e.g., Document.СписаниеТовара.Form.ФормаДокумента.Form
    obj_type_map = {
        'Document': 'Documents',
        'Catalog': 'Catalogs', 
        'DataProcessor': 'DataProcessors',
        'Report': 'Reports',
    }
    obj_type_1c = parts[0]
    obj_name = parts[1]
    form_name = parts[3]
    
    disk_type = obj_type_map.get(obj_type_1c, obj_type_1c + 's')
    
    # Check files exist
    form_dir = BASE / disk_type / obj_name / 'Forms' / form_name
    desc_file = BASE / disk_type / obj_name / 'Forms' / f'{form_name}.xml'
    ext_form = form_dir / 'Ext' / 'Form.xml'
    module_file = form_dir / 'Ext' / 'Form' / 'Module.bsl'
    
    issues = []
    if not form_dir.exists():
        issues.append("MISSING form dir")
    if not desc_file.exists():
        issues.append("MISSING descriptor .xml")
    if not ext_form.exists():
        issues.append("MISSING Ext/Form.xml")
    if not module_file.exists():
        issues.append("no Module.bsl (may be OK)")
    
    status = " | ".join(issues) if issues else "OK"
    if "MISSING" in status:
        print(f"  *** {entry}: {status}")
    else:
        print(f"      {entry}: {status}")

print()
print("=" * 70)
print("INVESTIGATION 4: UUID cross-check (CDI vs XML)")
print("=" * 70)

# Check form UUIDs match between CDI and descriptor XML
for elem in cdi_root.iter(NS_CDI + 'Metadata'):
    name = elem.get('name', '')
    mid = elem.get('id', '')
    
    if '.Form.' not in name or name.endswith('.Form') or '.Form.Form' in name:
        continue  # Skip inner Form entries
    
    parts = name.split('.')
    obj_type_1c = parts[0]
    obj_name = parts[1]
    form_name = parts[3]
    
    obj_type_map = {
        'Document': 'Documents',
        'Catalog': 'Catalogs',
        'DataProcessor': 'DataProcessors',
        'Report': 'Reports',
    }
    disk_type = obj_type_map.get(obj_type_1c, obj_type_1c + 's')
    
    desc_path = BASE / disk_type / obj_name / 'Forms' / f'{form_name}.xml'
    if desc_path.exists():
        try:
            tree = ET.parse(str(desc_path))
            root = tree.getroot()
            form_elem = root.find(f'{NS_MD}Form')
            if form_elem is not None:
                xml_uuid = form_elem.get('uuid', '')
                if xml_uuid != mid:
                    print(f"  UUID MISMATCH: {name}")
                    print(f"    CDI:  {mid}")
                    print(f"    XML:  {xml_uuid}")
                else:
                    pass  # OK
        except Exception as e:
            print(f"  ERROR parsing {desc_path}: {e}")

print("  UUID cross-check complete")

print()
print("=" * 70)
print("INVESTIGATION 5: Check for README.md and other non-1C files")
print("=" * 70)

non_1c_files = []
for f in BASE.rglob('*'):
    if f.is_file():
        if f.suffix.lower() in ['.md', '.txt', '.py', '.js', '.bat']:
            non_1c_files.append(str(f.relative_to(BASE)))
        elif f.name.startswith('.'):
            non_1c_files.append(str(f.relative_to(BASE)))

if non_1c_files:
    print(f"Found {len(non_1c_files)} non-1C files:")
    for f in non_1c_files:
        print(f"  {f}")
else:
    print("No non-1C files found")

print()
print("=" * 70)
print("INVESTIGATION 6: Form descriptor check (owner attribute)")
print("=" * 70)

# Check all form descriptors for correct owner uuid
for elem in cdi_root.iter(NS_CDI + 'Metadata'):
    name = elem.get('name', '')
    mid = elem.get('id', '')
    
    # Only look at form entries (not .Form inner, not .Form.Form)
    if '.Form.' not in name or name.endswith('.Form') or name.count('.Form.') > 1:
        continue
    
    parts = name.split('.')
    obj_type_1c = parts[0]
    obj_name = parts[1]
    form_name = parts[3]
    
    obj_type_map = {
        'Document': 'Documents',
        'Catalog': 'Catalogs',
        'DataProcessor': 'DataProcessors',
        'Report': 'Reports',
    }
    disk_type = obj_type_map.get(obj_type_1c, obj_type_1c + 's')
    
    desc_path = BASE / disk_type / obj_name / 'Forms' / f'{form_name}.xml'
    if desc_path.exists():
        try:
            tree = ET.parse(str(desc_path))
            root = tree.getroot()
            form_elem = root.find(f'{NS_MD}Form')
            if form_elem is not None:
                owner = form_elem.get('owner', '')
                if owner:
                    # Find parent object UUID in CDI
                    parent_name = f'{obj_type_1c}.{obj_name}'
                    parent_uuid = None
                    for p_elem in cdi_root.iter(NS_CDI + 'Metadata'):
                        if p_elem.get('name', '') == parent_name:
                            parent_uuid = p_elem.get('id', '')
                            break
                    if parent_uuid and owner != parent_uuid:
                        print(f"  OWNER MISMATCH: {name}")
                        print(f"    Form descriptor owner: {owner}")
                        print(f"    Parent CDI UUID: {parent_uuid}")
                    elif not parent_uuid:
                        print(f"  WARNING: Parent not found in CDI for {name}")
                # Check if owner is missing
                if not owner:
                    # Check if it has the correct form
                    pass  # owner is optional in some cases
        except Exception as e:
            print(f"  ERROR: {desc_path}: {e}")

print("  Owner check complete")
