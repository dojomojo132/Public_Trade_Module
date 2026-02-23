# -*- coding: utf-8 -*-
import shutil
import pathlib

src = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\DataProcessors\РабочееМестоКассира\Forms\Форма\Ext\Form\Module.bsl")
dst = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\DataProcessors\РабочееМестоКассира\Forms\Форма\Ext\Form\Module.bsl")

dst.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(src, dst)
print(f"OK: {src.name} -> Проверка")
