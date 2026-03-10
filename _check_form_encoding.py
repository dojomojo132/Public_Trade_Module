# -*- coding: utf-8 -*-
"""Читает последний лог 1С и проверяет кодировку файлов формы."""
import pathlib, glob

# 1. Прочитать лог
logs_dir = pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Валидация\logs")
logs = sorted(logs_dir.glob("1c-designer-*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
if logs:
    log_file = logs[0]
    print(f"=== Лог: {log_file.name} ===")
    for enc in ['utf-8-sig', 'utf-8', 'cp1251', 'utf-16-le']:
        try:
            content = log_file.read_text(encoding=enc)
            print(f"Кодировка: {enc}")
            for line in content.strip().split('\n'):
                line = line.strip()
                if line:
                    print(f"  {line}")
            break
        except:
            continue

# 2. Проверить файлы формы ФормаГруппы
print("\n=== Файлы ФормаГруппы ===")
base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Catalogs\Номенклатура\Forms")
form_dir = None
for d in base.iterdir():
    print(f"  DIR/FILE: '{d.name}' (is_dir={d.is_dir()}) hex_name={d.name.encode('utf-8').hex()}")
    if 'Группы' in d.name or 'руппы' in d.name:
        form_dir = d

if form_dir:
    print(f"\n  Found ФормаГруппы dir: '{form_dir.name}'")
    # Check encoding of Form.xml
    form_xml = form_dir / "Ext" / "Form.xml"
    if form_xml.exists():
        raw = form_xml.read_bytes()
        print(f"  Form.xml size: {len(raw)} bytes")
        print(f"  BOM: {raw[:3].hex()}")
        print(f"  First 200 chars: {raw[:200]}")
    else:
        print(f"  Form.xml NOT FOUND at {form_xml}")
    
    # Check descriptor
    desc_xml = base / (form_dir.name + ".xml")
    if desc_xml.exists():
        raw = desc_xml.read_bytes()
        print(f"\n  Descriptor {desc_xml.name} size: {len(raw)} bytes")
        print(f"  BOM: {raw[:3].hex()}")
        print(f"  First 200 chars: {raw[:200]}")
    else:
        print(f"  Descriptor NOT FOUND at {desc_xml}")

# 3. Check Номенклатура.xml for exact DefaultFolderForm text
nom_xml = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Catalogs\Номенклатура.xml")
content = nom_xml.read_text(encoding='utf-8-sig')
for i, line in enumerate(content.split('\n'), 1):
    if 'DefaultFolderForm' in line or 'ФормаГруппы' in line:
        raw_bytes = line.encode('utf-8')
        print(f"\n  Line {i}: {line.strip()}")
        print(f"  Hex: {raw_bytes.hex()}")

print("\nГотово!")
