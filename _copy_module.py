# -*- coding: utf-8 -*-
import shutil
import pathlib

src = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\HTTPServices\ТоварыАПИ\Ext\Module.bsl")
dst = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\HTTPServices\ТоварыАПИ\Ext\Module.bsl")

# Ensure destination directory exists
dst.parent.mkdir(parents=True, exist_ok=True)

shutil.copy2(str(src), str(dst))
print(f"Copied: {src.name}")
print(f"  From: {src}")
print(f"  To:   {dst}")
print(f"  Size: {dst.stat().st_size} bytes")
