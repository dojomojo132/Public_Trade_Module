# -*- coding: utf-8 -*-
"""Sync Configuration.xml, ConfigDumpInfo.xml, and subsystem files to Проверка"""
import shutil
import pathlib

BASE = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")
COPY = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка")

files_to_sync = [
    "Configuration.xml",
    "ConfigDumpInfo.xml",
    "Subsystems/Склад.xml",
    "Subsystems/Все.xml",
]

for f in files_to_sync:
    src = BASE / f
    dst = COPY / f
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"  OK: {f}")

print("\nSync complete!")
