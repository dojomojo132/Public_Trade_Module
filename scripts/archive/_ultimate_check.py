# -*- coding: utf-8 -*-
"""Ultimate integrity check: Configuration.xml vs CDI vs disk files."""
import pathlib
import xml.etree.ElementTree as ET
from collections import defaultdict

BASE = pathlib.Path(r'D:\Git\Public_Trade_Module\Конфигурация\Проверка')
NS_CDI = '{http://v8.1c.ru/8.3/xcf/dumpinfo}'
NS_MD = '{http://v8.1c.ru/8.3/MDClasses}'

# ============================================================
# Parse Configuration.xml - get ALL objects from ChildObjects
# ============================================================
config = ET.parse(str(BASE / 'Configuration.xml'))
config_root = config.getroot()

# Map: XML tag -> CDI prefix, disk folder
TAG_MAP = {
    'Document': ('Document', 'Documents'),
    'Catalog': ('Catalog', 'Catalogs'),
    'DataProcessor': ('DataProcessor', 'DataProcessors'),
    'Report': ('Report', 'Reports'),
    'Enum': ('Enum', 'Enums'),
    'CommonModule': ('CommonModule', 'CommonModules'),
    'AccumulationRegister': ('AccumulationRegister', 'AccumulationRegisters'),
    'InformationRegister': ('InformationRegister', 'InformationRegisters'),
    'Constant': ('Constant', 'Constants'),
    'Subsystem': ('Subsystem', 'Subsystems'),
    'Role': ('Role', 'Roles'),
    'Language': ('Language', 'Languages'),
    'CommonTemplate': ('CommonTemplate', 'CommonTemplates'),
    'CommonPicture': ('CommonPicture', 'CommonPictures'),
    'Style': ('Style', 'Styles'),
    'StyleItem': ('StyleItem', 'StyleItems'),
}

conf_objects = {}  # {CDI_name: tag}
for elem in config_root.iter():
    tag = elem.tag.replace(NS_MD, '')
    if tag in TAG_MAP and elem.text:
        cdi_prefix = TAG_MAP[tag][0]
        cdi_name = f'{cdi_prefix}.{elem.text}'
        conf_objects[cdi_name] = tag

# ============================================================
# Parse CDI - get ALL top-level metadata entries
# ============================================================
cdi = ET.parse(str(BASE / 'ConfigDumpInfo.xml'))
cdi_top_level = {}  # {name: id} for top-level entries (direct children of ConfigVersions)

config_versions = cdi.getroot().find(NS_CDI + 'ConfigVersions')
if config_versions is None:
    print("ERROR: ConfigVersions not found!")
    exit(1)

# Direct children of ConfigVersions
for elem in config_versions:
    if elem.tag == NS_CDI + 'Metadata':
        name = elem.get('name', '')
        mid = elem.get('id', '')
        cdi_top_level[name] = mid

# ALL CDI entries
all_cdi = {}
for elem in cdi.getroot().iter(NS_CDI + 'Metadata'):
    name = elem.get('name', '')
    mid = elem.get('id', '')
    all_cdi[name] = mid

# ============================================================
# CHECK: Configuration.xml objects vs CDI
# ============================================================
print("=" * 70)
print("CHECK A: Configuration.xml objects missing from CDI")
print("=" * 70)

issues = 0
for obj_name, tag in sorted(conf_objects.items()):
    if obj_name not in all_cdi:
        print(f"  MISSING: {obj_name} (in Configuration.xml but NOT in CDI)")
        issues += 1

if issues == 0:
    print("  All Configuration.xml objects found in CDI")

print()
print("=" * 70)
print("CHECK B: CDI top-level objects not in Configuration.xml")
print("=" * 70)

# CDI top-level entries that should be in Configuration.xml
issues = 0
for name in sorted(cdi_top_level.keys()):
    # Skip sub-object entries (Form, Module, Template)
    parts = name.split('.')
    if len(parts) == 2:
        # This is a top-level object like Document.X
        if name not in conf_objects:
            print(f"  EXTRA: {name} (in CDI but NOT in Configuration.xml)")
            issues += 1

if issues == 0:
    print("  All CDI top-level entries matched in Configuration.xml")

print()
print("=" * 70) 
print("CHECK C: Disk files vs CDI for objects with folders")
print("=" * 70)

issues = 0
for xml_tag, (cdi_prefix, disk_folder) in TAG_MAP.items():
    folder = BASE / disk_folder
    if not folder.exists():
        continue
    
    # Check .xml files on disk
    for xml_file in folder.glob('*.xml'):
        obj_name = xml_file.stem
        cdi_name = f'{cdi_prefix}.{obj_name}'
        
        if cdi_name not in all_cdi:
            print(f"  DISK-ONLY: {disk_folder}/{xml_file.name} has NO CDI entry")
            issues += 1
        
        if cdi_name not in conf_objects:
            print(f"  DISK-ONLY: {disk_folder}/{xml_file.name} has NO Configuration.xml entry")
            issues += 1
    
    # Check directories on disk that have no .xml
    for subdir in folder.iterdir():
        if subdir.is_dir():
            xml_file = folder / f'{subdir.name}.xml'
            if not xml_file.exists():
                print(f"  DIR-ONLY: {disk_folder}/{subdir.name}/ exists but NO {subdir.name}.xml")
                issues += 1

if issues == 0:
    print("  All disk files consistent with CDI and Configuration.xml")

print()
print("=" * 70)
print("CHECK D: CDI ObjectModule entries vs actual files")
print("=" * 70)

issues = 0
for name, mid in sorted(all_cdi.items()):
    if not name.endswith('.ObjectModule'):
        continue
    
    # Parse name: Type.Object.ObjectModule
    parts = name.split('.')
    obj_type = parts[0]
    obj_name = parts[1]
    
    if obj_type not in TAG_MAP:
        continue
    
    disk_folder = TAG_MAP[obj_type][1]
    
    # Check both formats
    bsl_path = BASE / disk_folder / obj_name / 'Ext' / 'ObjectModule.bsl'
    xml_path = BASE / disk_folder / obj_name / 'Ext' / 'ObjectModule.xml'
    dir_path = BASE / disk_folder / obj_name / 'Ext' / 'ObjectModule'
    
    has_bsl = bsl_path.exists()
    has_xml = xml_path.exists()
    has_dir = dir_path.exists()
    
    if has_bsl:
        pass  # OK - flat format
    elif has_xml and has_dir:
        pass  # OK - hierarchical format
    else:
        print(f"  MISSING MODULE: {name}")
        print(f"    Expected at: {bsl_path} or {xml_path}")
        issues += 1

if issues == 0:
    print("  All ObjectModule CDI entries have matching files")

print()
print("=" * 70)
print("CHECK E: All attribute UUIDs in XML match CDI")
print("=" * 70)

issues = 0
for xml_tag, (cdi_prefix, disk_folder) in TAG_MAP.items():
    if xml_tag not in ('Document', 'Catalog', 'DataProcessor'):
        continue
    folder = BASE / disk_folder
    if not folder.exists():
        continue
    
    for xml_file in folder.glob('*.xml'):
        obj_name = xml_file.stem
        try:
            tree = ET.parse(str(xml_file))
            root = tree.getroot()
        except:
            continue
        
        # Find all Attribute elements with uuid
        for attr_elem in root.iter(NS_MD + 'Attribute'):
            attr_uuid = attr_elem.get('uuid', '')
            if not attr_uuid:
                continue
            
            # Find name
            name_elem = attr_elem.find(f'{NS_MD}Properties/{NS_MD}Name')
            if name_elem is None:
                continue
            attr_name = name_elem.text or ''
            
            # Determine parent (could be in TabularSection)
            # Check if this attribute is inside a TabularSection
            # This is tricky with ET, let's check CDI instead
            # Look for this UUID in CDI
            uuid_in_cdi = False
            for cdi_entry_name, cdi_id in all_cdi.items():
                if cdi_id == attr_uuid:
                    uuid_in_cdi = True
                    break
            
            if not uuid_in_cdi:
                print(f"  UUID NOT IN CDI: {obj_name}.{attr_name} uuid={attr_uuid}")
                issues += 1

        # Check TabularSections too
        for ts_elem in root.iter(NS_MD + 'TabularSection'):
            ts_uuid = ts_elem.get('uuid', '')
            if ts_uuid:
                uuid_in_cdi = any(cid == ts_uuid for cid in all_cdi.values())
                if not uuid_in_cdi:
                    ts_name_elem = ts_elem.find(f'{NS_MD}Properties/{NS_MD}Name')
                    ts_name = ts_name_elem.text if ts_name_elem is not None else '?'
                    print(f"  TS UUID NOT IN CDI: {obj_name}.{ts_name} uuid={ts_uuid}")
                    issues += 1

if issues == 0:
    print("  All attribute/TS UUIDs in XML have matching CDI entries")

print()
print("=" * 70)
print("CHECK F: Form descriptor UUID vs parent object listing")
print("=" * 70)

issues = 0
# For each form descriptor, check that its UUID matches the CDI
for xml_tag, (cdi_prefix, disk_folder) in TAG_MAP.items():
    if xml_tag not in ('Document', 'Catalog', 'DataProcessor', 'Report'):
        continue
    folder = BASE / disk_folder
    if not folder.exists():
        continue
    
    for obj_dir in folder.iterdir():
        if not obj_dir.is_dir():
            continue
        forms_dir = obj_dir / 'Forms'
        if not forms_dir.exists():
            continue
        
        for desc_file in forms_dir.glob('*.xml'):
            form_name = desc_file.stem
            try:
                tree = ET.parse(str(desc_file))
                root = tree.getroot()
                form_elem = root.find(f'{NS_MD}Form')
                if form_elem is None:
                    print(f"  NO <Form> element: {desc_file.relative_to(BASE)}")
                    issues += 1
                    continue
                
                desc_uuid = form_elem.get('uuid', '')
                owner = form_elem.get('owner', '')
                
                # Check CDI
                cdi_name = f'{cdi_prefix}.{obj_dir.name}.Form.{form_name}'
                cdi_id = all_cdi.get(cdi_name, '')
                
                if not cdi_id:
                    print(f"  NO CDI: {cdi_name}")
                    issues += 1
                elif cdi_id != desc_uuid:
                    print(f"  UUID MISMATCH: {cdi_name}")
                    print(f"    CDI:  {cdi_id}")
                    print(f"    Desc: {desc_uuid}")
                    issues += 1
                
                # Check owner matches parent object UUID
                if owner:
                    parent_cdi = f'{cdi_prefix}.{obj_dir.name}'
                    parent_uuid = all_cdi.get(parent_cdi, '')
                    if parent_uuid and owner != parent_uuid:
                        print(f"  OWNER MISMATCH: {cdi_name}")
                        print(f"    Descriptor owner: {owner}")
                        print(f"    Parent UUID:      {parent_uuid}")
                        issues += 1
                        
            except Exception as e:
                print(f"  ERROR: {desc_file.relative_to(BASE)}: {e}")
                issues += 1

if issues == 0:
    print("  All form descriptors consistent")

print()
print(f"{'=' * 70}")
print(f"SUMMARY")
print(f"{'=' * 70}")
