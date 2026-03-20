# -*- coding: utf-8 -*-
import pathlib

form = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация_PTM_Driver_Vchasno\DataProcessors\Вчсн_КассаПанель\Forms\Форма\Ext\Form.xml")
mod = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация_PTM_Driver_Vchasno\DataProcessors\Вчсн_КассаПанель\Forms\Форма\Ext\Form\Module.bsl")

for f in [form, mod]:
    data = f.read_bytes()
    bom = "YES" if data[0]==0xEF and data[1]==0xBB and data[2]==0xBF else "NO"
    print(f"{f.name}: {len(data)}B, BOM={bom}, first3=[{data[0]},{data[1]},{data[2]}]")
