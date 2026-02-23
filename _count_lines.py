# -*- coding: utf-8 -*-
import pathlib

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка")
files = [
    base / "DataProcessors" / "РабочееМестоКассира" / "Forms" / "Форма" / "Ext" / "Form" / "Module.bsl",
    base / "Documents" / "КассоваяСмена" / "Forms" / "ФормаДокумента" / "Ext" / "Form" / "Module.bsl",
    base / "Documents" / "ИнвентаризацияТоваров" / "Forms" / "ФормаДокумента" / "Ext" / "Form" / "Module.bsl",
    base / "Documents" / "ЧекККМ" / "Forms" / "ФормаДокумента" / "Ext" / "Form" / "Module.bsl",
    base / "Documents" / "Переоценка" / "Forms" / "ФормаДокумента" / "Ext" / "Form" / "Module.bsl",
    base / "Documents" / "СписаниеТовара" / "Forms" / "ФормаДокумента" / "Ext" / "Form" / "Module.bsl",
    base / "Documents" / "ПриходТовара" / "Forms" / "ФормаДокумента" / "Ext" / "Form" / "Module.bsl",
]
for f in files:
    if f.exists():
        lines = len(f.read_text(encoding="utf-8-sig").splitlines())
        print(f"{f.relative_to(base)}: {lines} lines")
    else:
        print(f"{f.relative_to(base)}: NOT FOUND")
