# -*- coding: utf-8 -*-
"""Check ObjectModule: files on disk vs CDI entries for ALL objects."""
import pathlib

BASE = pathlib.Path(r'D:\Git\Public_Trade_Module\Конфигурация\Проверка')
CDI_TEXT = (BASE / 'ConfigDumpInfo.xml').read_text(encoding='utf-8')

print("=" * 70)
print("ObjectModule: disk files vs CDI entries")
print("=" * 70)

type_map = {
    'Documents': 'Document',
    'DataProcessors': 'DataProcessor',
    'Catalogs': 'Catalog',
    'Reports': 'Report',
}

for folder_name, cdi_prefix in type_map.items():
    folder = BASE / folder_name
    if not folder.exists():
        continue
    
    for obj_dir in sorted(folder.iterdir()):
        if not obj_dir.is_dir():
            continue
        
        ext_dir = obj_dir / 'Ext'
        if not ext_dir.exists():
            continue
        
        has_bsl = (ext_dir / 'ObjectModule.bsl').exists()
        has_xml = (ext_dir / 'ObjectModule.xml').exists()
        has_dir = (ext_dir / 'ObjectModule').is_dir()
        
        cdi_entry = f'{cdi_prefix}.{obj_dir.name}.ObjectModule'
        has_cdi = cdi_entry in CDI_TEXT
        
        if has_bsl or has_xml:
            fmt = 'BSL' if has_bsl else 'XML+DIR'
            cdi_status = 'CDI:YES' if has_cdi else 'CDI:NO!!!'
            marker = '  ***' if not has_cdi else '     '
            print(f'{marker} {folder_name}/{obj_dir.name}: {fmt} | {cdi_status}')
        elif has_cdi:
            print(f'  *** {folder_name}/{obj_dir.name}: NO FILE | CDI:YES!!!')

# Also check CommonModules
print()
print("CommonModules:")
cm_folder = BASE / 'CommonModules'
if cm_folder.exists():
    for obj_dir in sorted(cm_folder.iterdir()):
        if not obj_dir.is_dir():
            continue
        ext_dir = obj_dir / 'Ext'
        if ext_dir.exists():
            has_bsl = (ext_dir / 'Module.bsl').exists()
            cdi_entry = f'CommonModule.{obj_dir.name}.Module'
            has_cdi = cdi_entry in CDI_TEXT
            if has_bsl or has_cdi:
                marker = '  ***' if (has_bsl != has_cdi) else '     '
                print(f'{marker} {obj_dir.name}: BSL={has_bsl} | CDI={has_cdi}')
