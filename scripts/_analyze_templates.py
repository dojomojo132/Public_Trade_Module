# -*- coding: utf-8 -*-
"""
Анализ использования CommonTemplates (Общих макетов):
1. Получить полный список макетов из ИБ-дампа (Проверка/)
2. Получить список макетов в dev (Конфигурация/)
3. Найти ссылки на каждый макет в BSL-коде
4. Определить, какие макеты можно безопасно удалить
"""
import os
import re
import json
from pathlib import Path
from collections import defaultdict

PROJECT = Path(r"D:\Git\Public_Trade_Module")
IB_DUMP = PROJECT / "Проверка"
DEV = PROJECT / "Конфигурация"

def get_templates(base_path):
    """Get all CommonTemplates from a config folder"""
    ct_dir = base_path / "CommonTemplates"
    if not ct_dir.exists():
        return set()
    templates = set()
    for item in ct_dir.iterdir():
        if item.is_file() and item.suffix == '.xml':
            templates.add(item.stem)
    return templates

def find_bsl_references(template_name, search_dir):
    """Search for references to a template in BSL files"""
    refs = []
    for bsl_path in search_dir.rglob("*.bsl"):
        try:
            content = bsl_path.read_text(encoding='utf-8-sig')
        except:
            continue
        if template_name in content:
            # Find line numbers
            for i, line in enumerate(content.split('\n'), 1):
                if template_name in line:
                    rel = bsl_path.relative_to(search_dir)
                    refs.append(f"{rel}:L{i}")
    return refs

def find_xml_references(template_name, search_dir):
    """Search for references to a template in XML files (excluding CommonTemplates itself)"""
    refs = []
    ct_dir = search_dir / "CommonTemplates"
    for xml_path in search_dir.rglob("*.xml"):
        # Skip the template's own files
        try:
            if ct_dir in xml_path.parents or xml_path.parent == ct_dir:
                continue
        except:
            pass
        try:
            content = xml_path.read_text(encoding='utf-8-sig')
        except:
            continue
        if template_name in content:
            for i, line in enumerate(content.split('\n'), 1):
                if template_name in line:
                    rel = xml_path.relative_to(search_dir)
                    refs.append(f"{rel}:L{i}")
    return refs

# Get templates from both sources
ib_templates = get_templates(IB_DUMP)
dev_templates = get_templates(DEV)

print(f"=== CommonTemplates в ИБ-дампе: {len(ib_templates)} ===")
print(f"=== CommonTemplates в dev: {len(dev_templates)} ===")

# Only in IB (not in dev)
only_ib = sorted(ib_templates - dev_templates)
only_dev = sorted(dev_templates - ib_templates)
both = sorted(ib_templates & dev_templates)

print(f"\n=== Только в ИБ (не в dev): {len(only_ib)} ===")
print(f"=== Только в dev: {len(only_dev)} ===")
print(f"=== В обоих: {len(both)} ===")

# Categorize templates
drivers = []
non_drivers = []
for t in sorted(ib_templates):
    if t.startswith('Драйвер') or t.startswith('Driver'):
        drivers.append(t)
    else:
        non_drivers.append(t)

print(f"\n=== Шаблоны-драйверы: {len(drivers)} ===")
print(f"=== Прочие шаблоны: {len(non_drivers)} ===")

# Calculate sizes
print("\n=== РАЗМЕРЫ ШАБЛОНОВ (из ИБ-дампа) ===")
total_drivers_size = 0
total_other_size = 0
driver_sizes = []
for t in sorted(ib_templates):
    t_dir = IB_DUMP / "CommonTemplates" / t
    t_xml = IB_DUMP / "CommonTemplates" / f"{t}.xml"
    size = 0
    if t_xml.exists():
        size += t_xml.stat().st_size
    if t_dir.exists():
        for f in t_dir.rglob("*"):
            if f.is_file():
                size += f.stat().st_size
    
    is_driver = t.startswith('Драйвер') or t.startswith('Driver')
    if is_driver:
        total_drivers_size += size
        driver_sizes.append((t, size))
    else:
        total_other_size += size

print(f"  Драйверы: {total_drivers_size / 1024 / 1024:.1f} МБ ({len(drivers)} шт)")
print(f"  Прочие:   {total_other_size / 1024 / 1024:.1f} МБ ({len(non_drivers)} шт)")

# Find references for ALL templates (both dev and IB)
print("\n=== АНАЛИЗ ССЫЛОК НА ВСЕ МАКЕТЫ ===")
print("(поиск в BSL и XML файлах dev конфигурации)\n")

# Search in dev for references to ALL templates
used_templates = {}
unused_templates = []

for t in sorted(ib_templates | dev_templates):
    bsl_refs = find_bsl_references(t, DEV)
    xml_refs = find_xml_references(t, DEV)
    all_refs = bsl_refs + xml_refs
    
    in_dev = "DEV" if t in dev_templates else "---"
    in_ib = "IB" if t in ib_templates else "--"
    
    if all_refs:
        used_templates[t] = all_refs
        print(f"  [{in_dev}|{in_ib}] ИСПОЛЬЗУЕТСЯ: {t} ({len(all_refs)} ссылок)")
        for ref in all_refs[:5]:
            print(f"    → {ref}")
        if len(all_refs) > 5:
            print(f"    ... и ещё {len(all_refs)-5}")
    else:
        is_driver = t.startswith('Драйвер') or t.startswith('Driver')
        # Don't print each unused driver individually to save space
        if not is_driver:
            print(f"  [{in_dev}|{in_ib}] НЕ ИСПОЛЬЗУЕТСЯ: {t}")
        unused_templates.append(t)

# Summary
unused_drivers = [t for t in unused_templates if t.startswith('Драйвер') or t.startswith('Driver')]
unused_other = [t for t in unused_templates if not (t.startswith('Драйвер') or t.startswith('Driver'))]

print(f"\n{'='*60}")
print(f"ИТОГО:")
print(f"  Всего макетов: {len(ib_templates | dev_templates)}")
print(f"  Используются в коде: {len(used_templates)}")
print(f"  НЕ используются: {len(unused_templates)}")
print(f"    - Неиспользуемые драйверы: {len(unused_drivers)}")
print(f"    - Неиспользуемые прочие: {len(unused_other)}")
print(f"  Размер неиспользуемых драйверов: {sum(s for t,s in driver_sizes if t in unused_drivers) / 1024 / 1024:.1f} МБ")

print(f"\n=== БЕЗОПАСНО К УДАЛЕНИЮ (не используются в коде) ===")
for t in sorted(unused_templates):
    is_driver = t.startswith('Драйвер') or t.startswith('Driver')
    tag = "[ДРАЙВЕР]" if is_driver else "[ПРОЧИЙ]"
    in_where = "ИБ" if t in only_ib else "dev" if t in only_dev else "оба"
    print(f"  {tag} {t} [{in_where}]")

print(f"\n=== ИСПОЛЬЗУЮТСЯ (НЕЛЬЗЯ УДАЛЯТЬ) ===")
for t in sorted(used_templates.keys()):
    is_driver = t.startswith('Драйвер') or t.startswith('Driver')
    tag = "[ДРАЙВЕР]" if is_driver else "[ПРОЧИЙ]"
    print(f"  {tag} {t} ({len(used_templates[t])} ссылок)")
