# -*- coding: utf-8 -*-
import pathlib
import shutil

src = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Catalogs\Кассы.xml")
dst = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Catalogs\Кассы.xml")
shutil.copy2(src, dst)
print("OK: Кассы.xml скопирован")
