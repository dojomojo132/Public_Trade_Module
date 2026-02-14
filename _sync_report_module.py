# -*- coding: utf-8 -*-
import shutil
import pathlib

src = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Reports\Взаиморасчеты\Forms\ФормаОтчета\Ext\Form\Module.bsl")
dst = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Reports\Взаиморасчеты\Forms\ФормаОтчета\Ext\Form\Module.bsl")

print(f"Копирование: {src.name}")
print(f"  Из: {src}")
print(f"  В:  {dst}")

if not src.exists():
    print(f"  ОШИБКА: Исходный файл не найден!")
else:
    shutil.copy2(src, dst)
    print(f"  OK! Скопирован ({dst.stat().st_size} байт)")
