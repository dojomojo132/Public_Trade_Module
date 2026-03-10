# -*- coding: utf-8 -*-
"""Смотрим доступные бэкапы для отката ИБ."""
import pathlib, time

BACKUPS = pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Валидация\backups")

if BACKUPS.exists():
    dts = sorted(BACKUPS.glob("*.dt"), key=lambda f: f.stat().st_mtime)
    print(f"Бэкапы ({len(dts)}):")
    for dt in dts:
        mtime = time.ctime(dt.stat().st_mtime)
        size_mb = dt.stat().st_size // 1048576
        print(f"  {dt.name} ({size_mb} MB) - {mtime}")
    
    if dts:
        print(f"\nРекомендую откат к: {dts[-1].name}")
else:
    print("Папка backups не найдена!")
