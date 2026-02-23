# -*- coding: utf-8 -*-
"""Исследование структуры БПО_ДЕМО"""
import pathlib
import os

bpo_root = pathlib.Path(r"D:\Git\БПО_ДЕМО")

print("=== Корень БПО_ДЕМО ===")
for item in sorted(bpo_root.iterdir()):
    prefix = "📁" if item.is_dir() else "📄"
    print(f"  {prefix} {item.name}")

# Ищем Configuration.xml
for cf_xml in bpo_root.rglob("Configuration.xml"):
    print(f"\n=== Configuration.xml: {cf_xml} ===")
    # Читаем ChildObjects
    with open(cf_xml, encoding='utf-8') as f:
        content = f.read()
    
    # Простой парсинг - ищем типы объектов
    import re
    child_start = content.find("<ChildObjects>")
    child_end = content.find("</ChildObjects>")
    if child_start > 0:
        child_block = content[child_start:child_end]
        # Извлекаем все теги
        tags = re.findall(r'<(\w+)>([^<]+)</\1>', child_block)
        by_type = {}
        for tag, name in tags:
            by_type.setdefault(tag, []).append(name)
        
        for t, names in sorted(by_type.items()):
            print(f"\n  {t} ({len(names)}):")
            for n in names:
                print(f"    - {n}")

# Список всех папок верхнего уровня в конфигурации
config_dirs = [d for d in bpo_root.rglob("*") if d.is_dir() and d.parent == bpo_root]
