# -*- coding: utf-8 -*-
"""Читает конкретный лог загрузки 1С."""
import pathlib

# Лог от загрузки
log_file = pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Валидация\logs\1c-designer-20260227-010254.log")
if not log_file.exists():
    # Найти последний лог загрузки
    logs = sorted(pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Валидация\logs").glob("1c-designer-*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    for l in logs:
        print(f"  LOG: {l.name} ({l.stat().st_size} bytes)")
    if logs:
        log_file = logs[0]

for enc in ['utf-8-sig', 'utf-8', 'cp1251', 'utf-16-le', 'utf-16']:
    try:
        content = log_file.read_text(encoding=enc)
        print(f"=== {log_file.name} (enc={enc}, {len(content)} chars) ===")
        for line in content.strip().split('\n'):
            print(f"  {line.rstrip()}")
        break
    except Exception as e:
        print(f"  {enc}: FAIL {e}")
        continue

# Также проверим BOM первого файла ФормаГруппы.xml
print("\n=== Descriptor BOM check ===")
desc = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Catalogs\Номенклатура\Forms\ФормаГруппы.xml")
raw = desc.read_bytes()
print(f"Size: {len(raw)}, BOM bytes: {raw[:3].hex()}, First 100: {raw[:100]}")

print("\n=== Form.xml BOM check ===")
form = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Catalogs\Номенклатура\Forms\ФормаГруппы\Ext\Form.xml")
raw2 = form.read_bytes()
print(f"Size: {len(raw2)}, BOM bytes: {raw2[:3].hex()}, First 100: {raw2[:100]}")

# Compare with working form
print("\n=== ФормаЭлемента BOM check ===")
form_e = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Catalogs\Номенклатура\Forms\ФормаЭлемента.xml")
raw3 = form_e.read_bytes()
print(f"Size: {len(raw3)}, BOM bytes: {raw3[:3].hex()}, First 100: {raw3[:100]}")

form_e2 = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Catalogs\Номенклатура\Forms\ФормаЭлемента\Ext\Form.xml")
raw4 = form_e2.read_bytes()
print(f"Size: {len(raw4)}, BOM bytes: {raw4[:3].hex()}, First 100: {raw4[:100]}")

print("\nГотово!")
