# -*- coding: utf-8 -*-
"""Временно переименовать папку Documents в расширении."""
import os
import sys

src = r"D:\Git\Public_Trade_Module\Конфигурация_PTM_Fiscal\Documents"
dst = r"D:\Git\Public_Trade_Module\Конфигурация_PTM_Fiscal\Documents_TEMP"

if sys.argv[1:] and sys.argv[1] == "--restore":
    src, dst = dst, src

if os.path.exists(src):
    os.rename(src, dst)
    print(f"OK: {os.path.basename(src)} -> {os.path.basename(dst)}")
else:
    print(f"Не найдено: {src}")
