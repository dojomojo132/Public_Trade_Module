# -*- coding: utf-8 -*-
"""Очищает Predefined.xml от _ДемоТипыШтрихкодов (оставляет пустой контейнер)."""
import pathlib

EMPTY_CONTENT = '''<?xml version="1.0" encoding="UTF-8"?>
<PredefinedData xmlns="http://v8.1c.ru/8.3/xcf/predef" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="PlanOfCharacteristicKindPredefinedItems" version="2.20">
</PredefinedData>
'''

files = [
    pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\ChartsOfCharacteristicTypes\_ДемоТипыШтрихкодов\Ext\Predefined.xml"),
    pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\ChartsOfCharacteristicTypes\_ДемоТипыШтрихкодов\Ext\Predefined.xml"),
]

for f in files:
    if f.exists():
        # UTF-8 BOM (как в оригинальных файлах 1С)
        f.write_bytes(b'\xef\xbb\xbf' + EMPTY_CONTENT.encode('utf-8'))
        print(f"ОЧИЩЕН: {f}")
    else:
        print(f"НЕ НАЙДЕН: {f}")

print("Готово!")
