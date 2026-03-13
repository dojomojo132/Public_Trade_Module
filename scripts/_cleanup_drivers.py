# -*- coding: utf-8 -*-
"""
Скрипт для гибридной очистки CommonTemplates:
1. Копировать нужные драйверы из ИБ-дампа в dev
2. Удалить ненужные ссылки из Подсистем, CDI, Configuration.xml
3. Удалить файлы ненужных драйверов из dev

Категории ОСТАВИТЬ: ЧекопечатающиеУстройства, ПринтерыЭтикеток, УстройстваВвода
Категории УДАЛИТЬ: ВесовоеОборудование, ДисплеиПокупателя, ПлатежныеСистемы, ТерминалыСбораДанных, УстройствоРаспознавания
"""
import os
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

PROJECT = Path(r"D:\Git\Public_Trade_Module")
IB_DUMP = PROJECT / "Проверка"
DEV = PROJECT / "Конфигурация"

# ========== STEP 0: Определяем списки драйверов по категориям ==========

def get_subsystem_templates(subsystem_xml_path, all_driver_names):
    """Extract driver template names referenced in a subsystem XML"""
    if not subsystem_xml_path.exists():
        return []
    content = subsystem_xml_path.read_text(encoding='utf-8-sig')
    return [t for t in all_driver_names if t in content]

# Get all driver template names from IB dump + dev
all_drivers = set()
for ct_dir in [DEV / "CommonTemplates", IB_DUMP / "CommonTemplates"]:
    if ct_dir.exists():
        for f in ct_dir.iterdir():
            if f.is_file() and f.suffix == '.xml':
                name = f.stem
                if name.startswith('Драйвер') or name.startswith('Driver'):
                    all_drivers.add(name)

# Categorize using subsystem files
subsystem_base = DEV / "Subsystems" / "ПоддержкаОборудования" / "Subsystems" / "ПодключаемоеОборудование" / "Subsystems"

KEEP_SUBSYSTEMS = ["ЧекопечатающиеУстройства", "ПринтерыЭтикеток", "УстройстваВвода"]
REMOVE_SUBSYSTEMS = ["ВесовоеОборудование", "ДисплеиПокупателя", "ПлатежныеСистемы", "ТерминалыСбораДанных", "УстройствоРаспознавания"]

drivers_to_keep = set()
drivers_to_remove = set()

for sub in KEEP_SUBSYSTEMS:
    xml_path = subsystem_base / f"{sub}.xml"
    templates = get_subsystem_templates(xml_path, all_drivers)
    drivers_to_keep.update(templates)
    
for sub in REMOVE_SUBSYSTEMS:
    xml_path = subsystem_base / f"{sub}.xml"
    templates = get_subsystem_templates(xml_path, all_drivers)
    drivers_to_remove.update(templates)

# Драйвер1ССканер - без категории, входит в УстройстваВвода по смыслу → KEEP
if 'Драйвер1ССканер' in all_drivers:
    drivers_to_keep.add('Драйвер1ССканер')

# If a driver is in both categories (shouldn't happen), keep it
drivers_to_remove -= drivers_to_keep

# Some might be in both KEEP and REMOVE subsystems
uncategorized = all_drivers - drivers_to_keep - drivers_to_remove
if uncategorized:
    print(f"⚠ Некатегоризированные драйверы: {uncategorized}")
    # Default: keep uncategorized
    drivers_to_keep.update(uncategorized)

print(f"Драйверы к СОХРАНЕНИЮ: {len(drivers_to_keep)}")
print(f"Драйверы к УДАЛЕНИЮ:   {len(drivers_to_remove)}")

# ========== STEP 1: Копируем недостающие драйверы из ИБ-дампа ==========
print(f"\n{'='*60}")
print("ЭТАП 1: Копирование недостающих драйверов из ИБ-дампа")
print(f"{'='*60}")

copied_count = 0
for driver in sorted(drivers_to_keep):
    src_xml = IB_DUMP / "CommonTemplates" / f"{driver}.xml"
    src_dir = IB_DUMP / "CommonTemplates" / driver
    dst_xml = DEV / "CommonTemplates" / f"{driver}.xml"
    dst_dir = DEV / "CommonTemplates" / driver
    
    if not dst_xml.exists() and src_xml.exists():
        shutil.copy2(src_xml, dst_xml)
        print(f"  📋 Скопирован {driver}.xml")
        copied_count += 1
        
    if not dst_dir.exists() and src_dir.exists():
        shutil.copytree(src_dir, dst_dir)
        # Count size
        size = sum(f.stat().st_size for f in dst_dir.rglob("*") if f.is_file())
        print(f"  📋 Скопирован {driver}/ ({size/1024:.0f} КБ)")

print(f"\n  Итого скопировано: {copied_count} макетов")

# ========== STEP 2: Удаляем файлы ненужных драйверов из dev ==========
print(f"\n{'='*60}")
print("ЭТАП 2: Удаление файлов ненужных драйверов из dev")
print(f"{'='*60}")

deleted_count = 0
deleted_size = 0
for driver in sorted(drivers_to_remove):
    dev_xml = DEV / "CommonTemplates" / f"{driver}.xml"
    dev_dir = DEV / "CommonTemplates" / driver
    
    if dev_xml.exists():
        size = dev_xml.stat().st_size
        dev_xml.unlink()
        deleted_size += size
        deleted_count += 1
        print(f"  🗑 Удалён {driver}.xml")
        
    if dev_dir.exists():
        size = sum(f.stat().st_size for f in dev_dir.rglob("*") if f.is_file())
        shutil.rmtree(dev_dir)
        deleted_size += size
        print(f"  🗑 Удалён {driver}/ ({size/1024:.0f} КБ)")

print(f"\n  Итого удалено: {deleted_count} макетов, {deleted_size/1024/1024:.1f} МБ")

# ========== STEP 3: Обновляем Configuration.xml ==========
print(f"\n{'='*60}")
print("ЭТАП 3: Обновление Configuration.xml")
print(f"{'='*60}")

cfg_path = DEV / "Configuration.xml"
cfg_content = cfg_path.read_text(encoding='utf-8-sig')
cfg_lines = cfg_content.split('\n')
new_cfg_lines = []
removed_cfg = 0

# Also need to add missing KEEP drivers to Configuration.xml
# First, find which KEEP drivers are already in Configuration.xml
existing_in_cfg = set()
cfg_ct_pattern = re.compile(r'<CommonTemplate>(.*?)</CommonTemplate>')
for line in cfg_lines:
    m = cfg_ct_pattern.search(line)
    if m:
        existing_in_cfg.add(m.group(1))

# Find where CommonTemplates section is
ct_insert_line = -1
last_ct_line = -1
for i, line in enumerate(cfg_lines):
    if '<CommonTemplate>' in line:
        if ct_insert_line == -1:
            ct_insert_line = i
        last_ct_line = i

# Filter out REMOVE drivers and track what's kept
for line in cfg_lines:
    m = cfg_ct_pattern.search(line)
    if m and m.group(1) in drivers_to_remove:
        removed_cfg += 1
        print(f"  🗑 Удалён <CommonTemplate>{m.group(1)}</CommonTemplate>")
        continue
    new_cfg_lines.append(line)

# Add missing KEEP drivers to Configuration.xml
missing_in_cfg = drivers_to_keep - existing_in_cfg
if missing_in_cfg:
    # Find the last CommonTemplate line in new_cfg_lines
    insert_idx = -1
    for i, line in enumerate(new_cfg_lines):
        if '<CommonTemplate>' in line:
            insert_idx = i
    
    if insert_idx >= 0:
        # Get indent from existing line
        indent = ''
        for ch in new_cfg_lines[insert_idx]:
            if ch in ' \t':
                indent += ch
            else:
                break
        
        # Insert after last CommonTemplate
        for driver in sorted(missing_in_cfg):
            insert_idx += 1
            new_cfg_lines.insert(insert_idx, f"{indent}<CommonTemplate>{driver}</CommonTemplate>")
            print(f"  ➕ Добавлен <CommonTemplate>{driver}</CommonTemplate>")

# Write back (preserve BOM)
with open(cfg_path, 'w', encoding='utf-8-sig', newline='\r\n') as f:
    f.write('\n'.join(new_cfg_lines))
print(f"\n  Удалено из Configuration.xml: {removed_cfg}")
print(f"  Добавлено в Configuration.xml: {len(missing_in_cfg)}")

# ========== STEP 4: Обновляем ConfigDumpInfo.xml ==========
print(f"\n{'='*60}")
print("ЭТАП 4: Обновление ConfigDumpInfo.xml")
print(f"{'='*60}")

cdi_path = DEV / "ConfigDumpInfo.xml"
cdi_content = cdi_path.read_text(encoding='utf-8-sig')
cdi_lines = cdi_content.split('\n')
new_cdi_lines = []
removed_cdi = 0

# Remove CDI entries for REMOVE drivers
for line in cdi_lines:
    should_remove = False
    for driver in drivers_to_remove:
        if f'name="CommonTemplate.{driver}"' in line or f'name="CommonTemplate.{driver}.' in line:
            should_remove = True
            removed_cdi += 1
            break
    if not should_remove:
        new_cdi_lines.append(line)

# Add CDI entries for missing KEEP drivers (copy from IB dump CDI)
ib_cdi_path = IB_DUMP / "ConfigDumpInfo.xml"
if ib_cdi_path.exists():
    ib_cdi_content = ib_cdi_path.read_text(encoding='utf-8-sig')
    ib_cdi_lines = ib_cdi_content.split('\n')
    
    # Find which KEEP drivers don't have CDI entries
    existing_cdi = set()
    for line in new_cdi_lines:
        m = re.search(r'name="CommonTemplate\.(\w+)"', line)
        if m:
            existing_cdi.add(m.group(1))
    
    missing_cdi_drivers = set()
    for d in drivers_to_keep:
        if d not in existing_cdi:
            missing_cdi_drivers.add(d)
    
    if missing_cdi_drivers:
        # Find CDI entries in IB dump
        entries_to_add = []
        for line in ib_cdi_lines:
            for driver in missing_cdi_drivers:
                if f'name="CommonTemplate.{driver}"' in line or f'name="CommonTemplate.{driver}.' in line:
                    entries_to_add.append(line)
                    break
        
        # Insert before closing </ConfigDumpInfo>
        if entries_to_add:
            close_idx = -1
            for i, line in enumerate(new_cdi_lines):
                if '</ConfigDumpInfo>' in line:
                    close_idx = i
                    break
            
            if close_idx >= 0:
                for entry in entries_to_add:
                    new_cdi_lines.insert(close_idx, entry)
                    close_idx += 1
                print(f"  ➕ Добавлено {len(entries_to_add)} CDI-записей для недостающих драйверов")

with open(cdi_path, 'w', encoding='utf-8-sig', newline='\r\n') as f:
    f.write('\n'.join(new_cdi_lines))
print(f"  Удалено из CDI: {removed_cdi} записей")

# ========== STEP 5: Обновляем Подсистемы ==========
print(f"\n{'='*60}")
print("ЭТАП 5: Удаление ссылок из подсистем")
print(f"{'='*60}")

# Find all subsystem XMLs that reference removed drivers
subsystem_files_to_check = list(DEV.rglob("Subsystems/**/*.xml"))
ct_ref_pattern = re.compile(r'<Item>CommonTemplate\.(\w+)</Item>')

total_subsystem_refs_removed = 0
for sub_xml in subsystem_files_to_check:
    content = sub_xml.read_text(encoding='utf-8-sig')
    lines = content.split('\n')
    new_lines = []
    removed_here = 0
    
    for line in lines:
        m = ct_ref_pattern.search(line)
        if m and m.group(1) in drivers_to_remove:
            removed_here += 1
            continue
        new_lines.append(line)
    
    if removed_here > 0:
        with open(sub_xml, 'w', encoding='utf-8-sig', newline='\r\n') as f:
            f.write('\n'.join(new_lines))
        rel = sub_xml.relative_to(DEV)
        print(f"  🗑 {rel}: удалено {removed_here} ссылок")
        total_subsystem_refs_removed += removed_here

print(f"\n  Итого удалено из подсистем: {total_subsystem_refs_removed} ссылок")

# ========== ИТОГО ==========
print(f"\n{'='*60}")
print("ИТОГО")
print(f"{'='*60}")
print(f"  Скопировано драйверов в dev:    {copied_count}")
print(f"  Удалено файлов драйверов:       {deleted_count}")
print(f"  Удалено из Configuration.xml:    {removed_cfg}")
print(f"  Добавлено в Configuration.xml:   {len(missing_in_cfg)}")
print(f"  Удалено из ConfigDumpInfo.xml:   {removed_cdi}")
print(f"  Удалено из подсистем:            {total_subsystem_refs_removed}")
print(f"\n✅ Готово! Запустите validate → deploy")
