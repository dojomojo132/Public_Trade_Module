# -*- coding: utf-8 -*-
import pathlib

for label, p in [
    ("Проверка", pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Catalogs\Контрагенты\Forms")),
    ("Конфигурация", pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Catalogs\Контрагенты\Forms")),
]:
    print(f"{label}: {p}")
    if p.exists():
        for f in sorted(p.rglob("*")):
            print(f"  {f.relative_to(p)}")
    else:
        print("  НЕ СУЩЕСТВУЕТ!")
