# -*- coding: utf-8 -*-
"""
Тест: откатить изменения ФормаГруппы в Проверка и попробовать Load.
Потом восстановить.
"""
import pathlib
import shutil

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка")

# Save current versions
nom_xml = base / "Catalogs" / "Номенклатура.xml"
cdi_xml = base / "ConfigDumpInfo.xml"
form_dir = base / "Catalogs" / "Номенклатура" / "Forms" / "ФормаГруппы"
form_desc = base / "Catalogs" / "Номенклатура" / "Forms" / "ФормаГруппы.xml"

# Save current  
nom_xml_bak = nom_xml.with_suffix('.xml.bak')
cdi_xml_bak = cdi_xml.with_suffix('.xml.bak')
shutil.copy2(nom_xml, nom_xml_bak)
shutil.copy2(cdi_xml, cdi_xml_bak)
print("Saved backups")

# Read and revert Номенклатура.xml
content = nom_xml.read_text(encoding='utf-8-sig')
content = content.replace(
    '<DefaultFolderForm>Catalog.Номенклатура.Form.ФормаГруппы</DefaultFolderForm>',
    '<DefaultFolderForm/>'
)
content = content.replace(
    '\t\t\t<Form>ФормаГруппы</Form>\n',
    ''
)
nom_xml.write_text(content, encoding='utf-8-sig')
print("Reverted Номенклатура.xml")

# Read and revert ConfigDumpInfo.xml
content = cdi_xml.read_text(encoding='utf-8-sig')
lines = content.split('\n')
new_lines = [l for l in lines if 'ФормаГруппы' not in l]
cdi_xml.write_text('\n'.join(new_lines), encoding='utf-8-sig')
print("Reverted ConfigDumpInfo.xml")

# Remove form files
if form_dir.exists():
    shutil.rmtree(form_dir)
    print(f"Removed {form_dir}")
if form_desc.exists():
    form_desc.unlink()
    print(f"Removed {form_desc}")

print("\n=== Ready to test Load without ФормаГруппы ===")
