# -*- coding: utf-8 -*-
"""Analyze CommonTemplates size and usage"""
import os, pathlib

base = pathlib.Path(r'd:\Git\Public_Trade_Module') / 'Конфигурация' / 'CommonTemplates'
if not base.exists():
    # try Проверка
    base = pathlib.Path(r'd:\Git\Public_Trade_Module') / 'Конфигурация' / 'Проверка' / 'CommonTemplates'

if not base.exists():
    print("ERROR: CommonTemplates not found")
    exit(1)

print(f"PATH: {base}")
dirs = sorted([d for d in base.iterdir() if d.is_dir()])
total = 0
results = []
for d in dirs:
    size = sum(f.stat().st_size for f in d.rglob('*') if f.is_file())
    total += size
    results.append((size, d.name))

# Sort by size descending
results.sort(key=lambda x: -x[0])

print(f"\nТОП-20 по размеру:")
for size, name in results[:20]:
    print(f"  {size/1024/1024:8.2f} MB  {name}")

print(f"\n--- ВСЕГО папок: {len(dirs)}")
print(f"--- ВСЕГО размер папок: {total/1024/1024:.2f} MB")

# Count descriptors
xmls = [f for f in base.iterdir() if f.suffix == '.xml']
xml_total = sum(f.stat().st_size for f in xmls)
print(f"--- Дескрипторы XML ({len(xmls)} шт): {xml_total/1024/1024:.2f} MB")
print(f"--- ИТОГО: {(total+xml_total)/1024/1024:.2f} MB")

# Categorize
drivers = [n for _, n in results if n.startswith('Драйвер')]
components = [n for _, n in results if n.startswith('Компонента')]
other = [n for _, n in results if not n.startswith('Драйвер') and not n.startswith('Компонента')]

print(f"\nКатегории:")
print(f"  Драйверы: {len(drivers)}")
print(f"  Компоненты: {len(components)}")
print(f"  Другое: {len(other)} -> {other}")

# Now check usage in BSL files
print("\n\n=== ПРОВЕРКА ИСПОЛЬЗОВАНИЯ В BSL ===")
bsl_root = pathlib.Path(r'd:\Git\Public_Trade_Module') / 'Конфигурация'
bsl_files = list(bsl_root.rglob('*.bsl'))
print(f"Найдено BSL файлов: {len(bsl_files)}")

# Read all BSL content
all_bsl = ""
for f in bsl_files:
    try:
        content = f.read_text(encoding='utf-8-sig', errors='ignore')
        all_bsl += content + "\n"
    except:
        pass

# Check each template name
used = []
unused = []
for _, name in results:
    if name in all_bsl:
        used.append(name)
    else:
        unused.append(name)

print(f"\nИспользуемые в BSL ({len(used)}):")
for n in used:
    print(f"  + {n}")

print(f"\nНЕ используемые в BSL ({len(unused)}):")
for n in unused:
    sz = next(s for s, nm in results if nm == n)
    print(f"  - {n}  ({sz/1024/1024:.2f} MB)")

# Total unused size
unused_size = sum(s for s, n in results if n in unused)
unused_xml = sum(f.stat().st_size for f in xmls if f.stem in unused)
print(f"\nРазмер неиспользуемых: {(unused_size+unused_xml)/1024/1024:.2f} MB")
print(f"Размер используемых: {(total+xml_total-unused_size-unused_xml)/1024/1024:.2f} MB")
