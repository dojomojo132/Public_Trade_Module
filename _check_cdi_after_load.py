# -*- coding: utf-8 -*-
"""Проверяет ConfigDumpInfo.xml — создан ли после Load."""
import pathlib

cdi = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\ConfigDumpInfo.xml")
if cdi.exists():
    content = cdi.read_text(encoding='utf-8-sig')
    # Ищем Catalog.Номенклатура и ФормаГруппы
    for i, line in enumerate(content.split('\n'), 1):
        if 'Catalog.Номенклатура' in line:
            print(f"  L{i}: {line.strip()}")
    print(f"\n  Содержит 'ФормаГруппы': {'ФормаГруппы' in content}")
    print(f"  Общий размер: {len(content)} chars, {cdi.stat().st_size} bytes")
else:
    print("ConfigDumpInfo.xml НЕ НАЙДЕН!")
