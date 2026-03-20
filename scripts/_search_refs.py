# -*- coding: utf-8 -*-
"""Comprehensive search for references to removed/added attributes"""
import os

base = r'd:\Git\Public_Trade_Module'
config_dirs = [
    os.path.join(base, "Конфигурация"),
    os.path.join(base, "Конфигурация_PTM_Analytics"),
]

search_terms = [
    "СтавкаНДС",
    "СтавкиНДС",
    "Номенклатура.ФОП",
    ".ФОП",
]

for config_dir in config_dirs:
    if not os.path.exists(config_dir):
        continue
    print(f"\n=== Searching: {os.path.basename(config_dir)} ===")
    for root, dirs, files in os.walk(config_dir):
        for fname in files:
            if fname.endswith(('.xml', '.bsl')):
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8-sig') as f:
                        content = f.read()
                    for term in search_terms:
                        if term in content:
                            for i, line in enumerate(content.split('\n'), 1):
                                if term in line:
                                    rel = os.path.relpath(fpath, base)
                                    print(f"  {rel}:{i}: {line.strip()[:150]}")
                except:
                    pass

# Also check the Enums to verify СтавкиНДС exists
enum_dir = os.path.join(base, "Конфигурация", "Enums")
if os.path.exists(enum_dir):
    print(f"\n=== Enums directory contents ===")
    for item in os.listdir(enum_dir):
        print(f"  {item}")

# Check Configuration.xml for НалоговыеГруппы reference
config_xml = os.path.join(base, "Конфигурация", "Configuration.xml")
with open(config_xml, 'r', encoding='utf-8-sig') as f:
    for i, line in enumerate(f, 1):
        if 'НалоговыеГруппы' in line or 'СтавкиНДС' in line:
            print(f"\nConfiguration.xml:{i}: {line.strip()}")
