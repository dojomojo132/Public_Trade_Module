# -*- coding: utf-8 -*-
"""Remove СправочникНоменклатуры report entirely from Проверка to test base config"""
import pathlib
import re
import shutil

BASE = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка")

# 1. Remove from Configuration.xml
config_path = BASE / "Configuration.xml"
config = config_path.read_text(encoding='utf-8')
config = config.replace('\t\t\t<Report>СправочникНоменклатуры</Report>\n', '')
config_path.write_text(config, encoding='utf-8')
print("1. Removed from Configuration.xml")

# 2. Remove from ConfigDumpInfo.xml
cdi_path = BASE / "ConfigDumpInfo.xml"
cdi = cdi_path.read_text(encoding='utf-8')
cdi = re.sub(r'\s*<Metadata name="Report\.СправочникНоменклатуры"[^/]*/>', '', cdi)
cdi_path.write_text(cdi, encoding='utf-8')
print("2. Removed from ConfigDumpInfo.xml")

# 3. Remove from Subsystems
for sub_name in ['Склад.xml', 'Все.xml']:
    sub_path = BASE / "Subsystems" / sub_name
    sub = sub_path.read_text(encoding='utf-8')
    sub = re.sub(r'\s*<xr:Item[^>]*>Report\.СправочникНоменклатуры</xr:Item>', '', sub)
    sub_path.write_text(sub, encoding='utf-8')
    print(f"3. Removed from {sub_name}")

# 4. Remove report file
report_xml = BASE / "Reports" / "СправочникНоменклатуры.xml"
if report_xml.exists():
    report_xml.unlink()
    print("4. Removed СправочникНоменклатуры.xml")

report_dir = BASE / "Reports" / "СправочникНоменклатуры"
if report_dir.exists():
    shutil.rmtree(report_dir)
    print("5. Removed СправочникНоменклатуры/ folder")

print("\nReport completely removed from Проверка. Ready to test base config.")
