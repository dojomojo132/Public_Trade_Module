# -*- coding: utf-8 -*-
"""Fix missing CDI entries for CommonTemplates"""
import re
from pathlib import Path

DEV = Path(r"D:\Git\Public_Trade_Module\Конфигурация")
IB_DUMP = Path(r"D:\Git\Public_Trade_Module\Проверка")

# Get all CommonTemplates that exist as files in dev
dev_ct_dir = DEV / "CommonTemplates"
dev_templates = set()
for f in dev_ct_dir.iterdir():
    if f.is_file() and f.suffix == '.xml':
        dev_templates.add(f.stem)

# Get all CommonTemplates listed in Configuration.xml
cfg_path = DEV / "Configuration.xml"
cfg_content = cfg_path.read_text(encoding='utf-8-sig')
cfg_templates = set(re.findall(r'<CommonTemplate>(.*?)</CommonTemplate>', cfg_content))

# Check which have CDI entries
cdi_path = DEV / "ConfigDumpInfo.xml"
cdi_content = cdi_path.read_text(encoding='utf-8-sig')
cdi_templates = set()
for m in re.finditer(r'name="CommonTemplate\.([^"\.]+)"', cdi_content):
    cdi_templates.add(m.group(1))

print(f"Files in dev/CommonTemplates: {len(dev_templates)}")
print(f"In Configuration.xml: {len(cfg_templates)}")
print(f"In ConfigDumpInfo.xml: {len(cdi_templates)}")

# Find templates in Configuration.xml but NOT in CDI
missing_cdi = cfg_templates - cdi_templates
if missing_cdi:
    print(f"\n⚠ Отсутствуют в CDI ({len(missing_cdi)}):")
    for t in sorted(missing_cdi):
        print(f"  - {t}")

# Also check: templates in CDI but not in Configuration.xml
extra_cdi = cdi_templates - cfg_templates
if extra_cdi:
    print(f"\n⚠ В CDI, но не в Configuration.xml ({len(extra_cdi)}):")
    for t in sorted(extra_cdi):
        print(f"  - {t}")

# Fix: Get CDI entries from IB dump for missing ones
ib_cdi_path = IB_DUMP / "ConfigDumpInfo.xml"
ib_cdi_content = ib_cdi_path.read_text(encoding='utf-8-sig')
ib_cdi_lines = ib_cdi_content.split('\n')

entries_to_add = []
for line in ib_cdi_lines:
    for driver in missing_cdi:
        if f'name="CommonTemplate.{driver}"' in line or f'name="CommonTemplate.{driver}.' in line:
            entries_to_add.append(line.rstrip())
            break

print(f"\n📋 Найдено CDI-записей из ИБ-дампа для добавления: {len(entries_to_add)}")

if entries_to_add:
    # Insert before closing </ConfigDumpInfo>
    cdi_lines = cdi_content.split('\n')
    new_cdi_lines = []
    for line in cdi_lines:
        if '</ConfigDumpInfo>' in line:
            for entry in entries_to_add:
                new_cdi_lines.append(entry)
                print(f"  ➕ {entry[:80]}...")
            new_cdi_lines.append(line)
        else:
            new_cdi_lines.append(line)
    
    with open(cdi_path, 'w', encoding='utf-8-sig', newline='\r\n') as f:
        f.write('\n'.join(new_cdi_lines))
    print(f"\n✅ Добавлено {len(entries_to_add)} CDI-записей")

# Also check: files in dev but not in Configuration.xml
missing_cfg = dev_templates - cfg_templates
if missing_cfg:
    # Only driver ones
    missing_driver_cfg = {t for t in missing_cfg if t.startswith('Драйвер') or t.startswith('Driver')}
    if missing_driver_cfg:
        print(f"\n⚠ Файлы есть, но НЕТ в Configuration.xml ({len(missing_driver_cfg)}):")
        for t in sorted(missing_driver_cfg):
            print(f"  - {t}")

# Check for non-driver templates too
all_non_driver = {t for t in dev_templates if not t.startswith('Драйвер') and not t.startswith('Driver')}
missing_nd_cdi = all_non_driver - cdi_templates
if missing_nd_cdi:
    print(f"\n⚠ Не-драйвер макеты без CDI ({len(missing_nd_cdi)}):")
    for t in sorted(missing_nd_cdi):
        print(f"  - {t}")
