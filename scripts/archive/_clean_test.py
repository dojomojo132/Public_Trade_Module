# -*- coding: utf-8 -*-
"""
Step 1: Remove report from Конфигурация source, resync to Проверка, test deploy.
If clean config loads → problem is specifically in report files/CDI.
"""
import pathlib
import re
import shutil

KONFIG = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")
PROVERKA = KONFIG / "Проверка"

# === Remove report from Конфигурация SOURCE ===

# 1. Configuration.xml
config_path = KONFIG / "Configuration.xml"
config = config_path.read_text(encoding='utf-8')
config = config.replace('\t\t\t<Report>СправочникНоменклатуры</Report>\n', '')
config_path.write_text(config, encoding='utf-8')
print("1. Removed from Configuration.xml")

# 2. ConfigDumpInfo.xml — remove all report entries
cdi_path = KONFIG / "ConfigDumpInfo.xml"
cdi = cdi_path.read_text(encoding='utf-8')
# Remove parent with nested ObjectModule
cdi = re.sub(
    r'\s*<Metadata name="Report\.СправочникНоменклатуры"[^>]*>\s*'
    r'<Metadata name="Report\.СправочникНоменклатуры\.ObjectModule"[^/]*/>\s*'
    r'</Metadata>',
    '', cdi
)
# Remove self-closing entries (Form.*)
cdi = re.sub(r'\s*<Metadata name="Report\.СправочникНоменклатуры[^"]*"[^/]*/>', '', cdi)
cdi_path.write_text(cdi, encoding='utf-8')
print("2. Removed from ConfigDumpInfo.xml")

# 3. Subsystems
for sub_name in ['Склад.xml', 'Все.xml']:
    sub_path = KONFIG / "Subsystems" / sub_name
    sub = sub_path.read_text(encoding='utf-8')
    sub = re.sub(r'\s*<xr:Item[^>]*>Report\.СправочникНоменклатуры</xr:Item>', '', sub)
    sub_path.write_text(sub, encoding='utf-8')
    print(f"3. Removed from {sub_name}")

# 4. Remove report files
report_xml = KONFIG / "Reports" / "СправочникНоменклатуры.xml"
if report_xml.exists():
    report_xml.unlink()
    print("4. Removed report XML")

report_dir = KONFIG / "Reports" / "СправочникНоменклатуры"
if report_dir.exists():
    shutil.rmtree(report_dir)
    print("5. Removed report directory")

# === Resync to Проверка ===
print("\n=== Resyncing to Проверка ===")
if PROVERKA.exists():
    shutil.rmtree(PROVERKA)
for item in KONFIG.iterdir():
    if item.name in ("Проверка", "README.md"):
        continue
    dest = PROVERKA / item.name
    if item.is_dir():
        shutil.copytree(item, dest)
    else:
        PROVERKA.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, dest)
print("Resynced.")

# Verify
config2 = (PROVERKA / "Configuration.xml").read_text(encoding='utf-8')
print(f"\nReports in Configuration.xml: {config2.count('<Report>')}")
print(f"СправочникНоменклатуры present: {'СправочникНоменклатуры' in config2}")

cdi2 = (PROVERKA / "ConfigDumpInfo.xml").read_text(encoding='utf-8')
print(f"СправочникНоменклатуры in CDI: {'СправочникНоменклатуры' in cdi2}")

print("\nReady to test clean deploy!")
