# -*- coding: utf-8 -*-
"""Clean up PTM_Fiscal extension - remove Documents and EventSubscriptions folders."""
import shutil
import os

base = r"D:\Git\Public_Trade_Module\Конфигурация_PTM_Fiscal"

for folder in ["Documents", "EventSubscriptions"]:
    path = os.path.join(base, folder)
    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"Deleted: {folder}/")
    else:
        print(f"Not found: {folder}/")

print("Done")
