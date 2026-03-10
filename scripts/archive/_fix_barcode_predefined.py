# -*- coding: utf-8 -*-
"""Убирает StringQualifiers из Type в предопределённых значениях штрихкодов."""
import re
import pathlib

files = [
    pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\ChartsOfCharacteristicTypes\_ДемоТипыШтрихкодов\Ext\Predefined.xml"),
    pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\ChartsOfCharacteristicTypes\_ДемоТипыШтрихкодов\Ext\Predefined.xml"),
]

# Удаляем StringQualifiers внутри Type
PATTERN = re.compile(
    r'(<Type>\s*<v8:Type>xs:string</v8:Type>)\s*<v8:StringQualifiers>.*?</v8:StringQualifiers>\s*(</Type>)',
    re.DOTALL
)

for f in files:
    original = f.read_text(encoding='utf-8')
    fixed = PATTERN.sub(r'\1\n\t\t</Type>', original)
    if fixed != original:
        f.write_text(fixed, encoding='utf-8')
        print(f"ИСПРАВЛЕН: {f.name}")
        # Считаем заменённые
        count = len(PATTERN.findall(original))
        print(f"  Удалено StringQualifiers блоков: {count}")
    else:
        print(f"БЕЗ ИЗМЕНЕНИЙ: {f.name}")

print("Готово!")
