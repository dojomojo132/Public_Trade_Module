# -*- coding: utf-8 -*-
"""Categorize driver templates by equipment type"""
from pathlib import Path
import re

DEV = Path(r"D:\Git\Public_Trade_Module\Конфигурация")
IB = Path(r"D:\Git\Public_Trade_Module\Проверка")

# Get all driver templates 
all_templates = set()
for ct_dir in [DEV / "CommonTemplates", IB / "CommonTemplates"]:
    if ct_dir.exists():
        for f in ct_dir.iterdir():
            if f.is_file() and f.suffix == '.xml':
                name = f.stem
                if name.startswith('Драйвер') or name.startswith('Driver'):
                    all_templates.add(name)

# Categorize by subsystem
subsystem_base = DEV / "Subsystems" / "ПоддержкаОборудования" / "Subsystems" / "ПодключаемоеОборудование" / "Subsystems"
categories = {}
if subsystem_base.exists():
    for xml in subsystem_base.glob("*.xml"):
        cat_name = xml.stem
        with open(xml, 'r', encoding='utf-8-sig') as f:
            content = f.read()
        templates_in_cat = []
        for t in all_templates:
            if t in content:
                templates_in_cat.append(t)
        if templates_in_cat:
            categories[cat_name] = sorted(templates_in_cat)

# Also check for non-categorized drivers  
categorized = set()
for templates in categories.values():
    categorized.update(templates)

uncategorized = sorted(all_templates - categorized)

# Print categories
for cat, templates in sorted(categories.items()):
    # Calculate total size
    total_size = 0
    for t in templates:
        t_dir = IB / "CommonTemplates" / t
        t_xml = IB / "CommonTemplates" / f"{t}.xml"
        if t_xml.exists():
            total_size += t_xml.stat().st_size
        if t_dir.exists():
            for f in t_dir.rglob("*"):
                if f.is_file():
                    total_size += f.stat().st_size
    
    in_dev_count = sum(1 for t in templates if (DEV / "CommonTemplates" / f"{t}.xml").exists())
    print(f"\n{'='*60}")
    print(f"📦 {cat} ({len(templates)} макетов, {total_size/1024/1024:.1f} МБ)")
    print(f"   В dev: {in_dev_count}, Только в ИБ: {len(templates)-in_dev_count}")
    for t in templates:
        in_dev = "✅" if (DEV / "CommonTemplates" / f"{t}.xml").exists() else "❌"
        # Get size
        size = 0
        t_dir = IB / "CommonTemplates" / t
        t_xml = IB / "CommonTemplates" / f"{t}.xml"
        if t_xml.exists():
            size += t_xml.stat().st_size
        if t_dir.exists():
            for f in t_dir.rglob("*"):
                if f.is_file():
                    size += f.stat().st_size
        short = t.replace('Драйвер', '').replace('_ru', '')
        print(f"   {in_dev} {short} ({size/1024:.0f} КБ)")

if uncategorized:
    print(f"\n{'='*60}")
    print(f"📦 Без категории ({len(uncategorized)} макетов)")
    for t in uncategorized:
        in_dev = "✅" if (DEV / "CommonTemplates" / f"{t}.xml").exists() else "❌"
        print(f"   {in_dev} {t}")
