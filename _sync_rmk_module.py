# -*- coding: utf-8 -*-
"""Синхронизация Module.bsl РМК: Проверка → Конфигурация"""
import pathlib

src = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\DataProcessors\РабочееМестоКассира\Forms\Форма\Ext\Form\Module.bsl")
dst = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\DataProcessors\РабочееМестоКассира\Forms\Форма\Ext\Form\Module.bsl")

content = src.read_bytes()
dst.write_bytes(content)

print(f"Скопировано: {len(content)} байт")
print(f"  Источник:  {src}")
print(f"  Назначение: {dst}")
print("Готово!")
