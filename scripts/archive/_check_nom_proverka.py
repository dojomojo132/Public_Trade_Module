# -*- coding: utf-8 -*-
"""List all files in Proверка/Catalogs/Номенклатура"""
import os

base = r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Catalogs\Номенклатура"
if not os.path.exists(base):
    print("NOT FOUND")
else:
    print(f"Номенклатура folder exists")
    for root, dirs, files in os.walk(base):
        rel = os.path.relpath(root, base)
        if rel == '.':
            for f in files:
                print(f"  {f}")
        else:
            for f in files:
                print(f"  {rel}\\{f}")
