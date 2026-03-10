# -*- coding: utf-8 -*-
"""Удаляет ConfigDumpInfo.xml из Проверка чтобы 1С пересканировал все файлы."""
import pathlib

cdi = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\ConfigDumpInfo.xml")
if cdi.exists():
    cdi.unlink()
    print(f"УДАЛЁН: {cdi}")
else:
    print(f"НЕ НАЙДЕН: {cdi}")
print("Готово!")
