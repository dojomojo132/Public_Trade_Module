# -*- coding: utf-8 -*-
"""Fix subsystem references - remove drivers from removed categories"""
import re
from pathlib import Path

DEV = Path(r"D:\Git\Public_Trade_Module\Конфигурация")

# Drivers to remove (from removed categories)
REMOVE_SUBSYSTEMS = ["ВесовоеОборудование", "ДисплеиПокупателя", "ПлатежныеСистемы", "ТерминалыСбораДанных", "УстройствоРаспознавания"]
subsystem_base = DEV / "Subsystems" / "ПоддержкаОборудования" / "Subsystems" / "ПодключаемоеОборудование" / "Subsystems"

# All driver templates
all_drivers = set()
for ct_dir in [DEV / "CommonTemplates", Path(r"D:\Git\Public_Trade_Module\Проверка\CommonTemplates")]:
    if ct_dir.exists():
        for f in ct_dir.iterdir():
            if f.is_file() and f.suffix == '.xml' and (f.stem.startswith('Драйвер') or f.stem.startswith('Driver')):
                all_drivers.add(f.stem)

drivers_to_remove = set()
for sub in REMOVE_SUBSYSTEMS:
    xml_path = subsystem_base / f"{sub}.xml"
    if xml_path.exists():
        content = xml_path.read_text(encoding='utf-8-sig')
        for d in all_drivers:
            if d in content:
                drivers_to_remove.add(d)

# Also include keep drivers already in dev to NOT remove 
KEEP_SUBSYSTEMS = ["ЧекопечатающиеУстройства", "ПринтерыЭтикеток", "УстройстваВвода"]
drivers_to_keep = set()
for sub in KEEP_SUBSYSTEMS:
    xml_path = subsystem_base / f"{sub}.xml"
    if xml_path.exists():
        content = xml_path.read_text(encoding='utf-8-sig')
        for d in all_drivers:
            if d in content:
                drivers_to_keep.add(d)
if 'Драйвер1ССканер' in all_drivers:
    drivers_to_keep.add('Драйвер1ССканер')
drivers_to_remove -= drivers_to_keep

print(f"Драйверы к удалению из подсистем: {len(drivers_to_remove)}")

# Process ALL subsystem XMLs
total_removed = 0
for sub_xml in DEV.rglob("Subsystems/**/*.xml"):
    content = sub_xml.read_text(encoding='utf-8-sig')
    lines = content.split('\n')
    new_lines = []
    removed_here = 0
    
    for line in lines:
        should_remove = False
        for driver in drivers_to_remove:
            if f'CommonTemplate.{driver}' in line:
                should_remove = True
                break
        if should_remove:
            removed_here += 1
        else:
            new_lines.append(line)
    
    if removed_here > 0:
        with open(sub_xml, 'w', encoding='utf-8-sig', newline='\r\n') as f:
            f.write('\n'.join(new_lines))
        rel = sub_xml.relative_to(DEV)
        print(f"  🗑 {rel}: удалено {removed_here} ссылок")
        total_removed += removed_here

print(f"\nИтого удалено из подсистем: {total_removed} ссылок")
