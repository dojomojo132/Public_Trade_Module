# -*- coding: utf-8 -*-
import pathlib

paths = [
    pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\DataProcessors\ИмпортНоменклатуры\Ext\ObjectModule.bsl"),
    pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\DataProcessors\ИмпортНоменклатуры\Ext\ObjectModule.bsl"),
]

old = "\t\tТабДок.Прочитать(ИмяВременногоФайла, ТипФайлаТабличногоДокумента.XLSX);"
new = "\t\tТабДок.Прочитать(ИмяВременногоФайла);"

for p in paths:
    content = p.read_text(encoding='utf-8-sig')
    if old in content:
        content = content.replace(old, new)
        p.write_text(content, encoding='utf-8-sig')
        print(f"  OK: {p}")
    else:
        print(f"  SKIP: {p} (not found)")

print("\nDone!")
