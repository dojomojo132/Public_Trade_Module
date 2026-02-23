# -*- coding: utf-8 -*-
"""FINAL: Check which DataProcessors have ObjectModules on disk vs CDI vs Main XML."""
import pathlib
import xml.etree.ElementTree as ET

BASE = pathlib.Path(r'D:\Git\Public_Trade_Module\Конфигурация\Проверка')
NS_MD = '{http://v8.1c.ru/8.3/MDClasses}'
CDI_TEXT = (BASE / 'ConfigDumpInfo.xml').read_text(encoding='utf-8')

print("=" * 70)
print("DataProcessor module comprehensive check")
print("=" * 70)

dp_folder = BASE / 'DataProcessors'
for dp_xml in sorted(dp_folder.glob('*.xml')):
    name = dp_xml.stem
    dp_dir = dp_folder / name
    
    # Check main XML for UseStandardCommands, etc.
    tree = ET.parse(str(dp_xml))
    root = tree.getroot()
    
    # Check if IncludeHelpInContents or other properties indicate it has a module
    has_managed_form_module = False
    
    # Check disk
    ext_dir = dp_dir / 'Ext' if dp_dir.exists() else None
    has_bsl = ext_dir and (ext_dir / 'ObjectModule.bsl').exists()
    has_xml_wrapper = ext_dir and (ext_dir / 'ObjectModule.xml').exists()
    has_module_dir = ext_dir and (ext_dir / 'ObjectModule').is_dir()
    
    # Check CDI
    cdi_key = f'DataProcessor.{name}.ObjectModule'
    has_cdi = cdi_key in CDI_TEXT
    
    any_module = has_bsl or has_xml_wrapper
    
    status = []
    if has_bsl:
        status.append('BSL')
    if has_xml_wrapper:
        status.append('XML-wrapper')
    if has_module_dir:
        status.append('+Dir')
    if not any_module:
        status.append('NO-MODULE')
    
    cdi_str = 'CDI:YES' if has_cdi else 'CDI:NO'
    
    marker = '***' if (any_module and not has_cdi) or (not any_module and has_cdi) else '   '
    print(f"  {marker} {name}: {' '.join(status)} | {cdi_str}")

print()
print("=" * 70)
print("Document module check (for comparison)")
print("=" * 70)

doc_folder = BASE / 'Documents'
for doc_xml in sorted(doc_folder.glob('*.xml')):
    name = doc_xml.stem
    doc_dir = doc_folder / name
    
    ext_dir = doc_dir / 'Ext' if doc_dir.exists() else None
    has_bsl = ext_dir and (ext_dir / 'ObjectModule.bsl').exists()
    has_xml_wrapper = ext_dir and (ext_dir / 'ObjectModule.xml').exists()
    
    cdi_key = f'Document.{name}.ObjectModule'
    has_cdi = cdi_key in CDI_TEXT
    
    any_module = has_bsl or has_xml_wrapper
    
    status = 'BSL' if has_bsl else ('XML' if has_xml_wrapper else 'NO-MODULE')
    cdi_str = 'CDI:YES' if has_cdi else 'CDI:NO'
    
    marker = '***' if (any_module and not has_cdi) or (not any_module and has_cdi) else '   '
    print(f"  {marker} {name}: {status} | {cdi_str}")

# Also check catalog with module
print()
print("Catalog.Номенклатура:")
cat_ext = BASE / 'Catalogs' / 'Номенклатура' / 'Ext'
if cat_ext.exists():
    has_bsl = (cat_ext / 'ObjectModule.bsl').exists()
    has_mgr = (cat_ext / 'ManagerModule.bsl').exists()
    cdi_obj = 'Catalog.Номенклатура.ObjectModule' in CDI_TEXT
    cdi_mgr = 'Catalog.Номенклатура.ManagerModule' in CDI_TEXT
    print(f"  ObjectModule: BSL={has_bsl} CDI={cdi_obj}")
    print(f"  ManagerModule: BSL={has_mgr} CDI={cdi_mgr}")
