# -*- coding: utf-8 -*-
import shutil
import pathlib

src = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\DataProcessors\ИнформацияНоменклатуры\Forms\Форма\Ext\Form\Module.bsl")
dst = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\DataProcessors\ИнформацияНоменклатуры\Forms\Форма\Ext\Form\Module.bsl")

shutil.copy2(str(src), str(dst))
print(f"Synced: {src.name} -> Проверка")
