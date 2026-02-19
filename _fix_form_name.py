# -*- coding: utf-8 -*-
"""Fix form name: add .Форма. to ОткрытьФорму path"""
import pathlib

files = [
    pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Documents\ПриходТовара\Forms\ФормаДокумента\Ext\Form\Module.bsl"),
    pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Documents\ПриходТовара\Forms\ФормаДокумента\Ext\Form\Module.bsl"),
]

old = "Справочник.Номенклатура.ФормаЭлемента"
new = "Справочник.Номенклатура.Форма.ФормаЭлемента"

for f in files:
    content = f.read_text(encoding="utf-8-sig")
    count = content.count(old)
    content = content.replace(old, new)
    f.write_text(content, encoding="utf-8-sig")
    folder = "Проверка" if "Проверка" in str(f) else "Конфигурация"
    print(f"  {folder}: {count} replacements")

print("Done!")
