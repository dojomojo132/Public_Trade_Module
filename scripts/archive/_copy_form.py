# -*- coding: utf-8 -*-
import shutil
import pathlib

src = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Reports\Взаиморасчеты\Forms\ФормаОтчета\Ext")
dst = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Reports\Взаиморасчеты\Forms\ФормаОтчета\Ext")

dst.mkdir(parents=True, exist_ok=True)
shutil.copytree(str(src), str(dst), dirs_exist_ok=True)
print("OK: copied Ext to Проверка")
