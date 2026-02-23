# -*- coding: utf-8 -*-
"""Синхронизация BSL-модуля ПриходТовара между Конфигурация/ и Конфигурация/Проверка/"""
import shutil
import pathlib

src = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Documents\ПриходТовара\Forms\ФормаДокумента\Ext\Form\Module.bsl")
dst = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Documents\ПриходТовара\Forms\ФормаДокумента\Ext\Form\Module.bsl")

shutil.copy2(str(src), str(dst))
print(f"OK: Скопировано {src.name} -> {dst.parent}")
