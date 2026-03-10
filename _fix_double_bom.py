# -*- coding: utf-8 -*-
import pathlib

BOM = b'\xef\xbb\xbf'

files = [
    r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Catalogs\Контрагенты\Forms\ФормаВыбора.xml",
    r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Catalogs\Контрагенты\Forms\ФормаВыбора\Ext\Form.xml",
    r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Catalogs\Контрагенты\Forms\ФормаВыбора\Ext\Form\Module.bsl",
    r"D:\Git\Public_Trade_Module\Конфигурация\Catalogs\Контрагенты\Forms\ФормаВыбора.xml",
    r"D:\Git\Public_Trade_Module\Конфигурация\Catalogs\Контрагенты\Forms\ФормаВыбора\Ext\Form.xml",
    r"D:\Git\Public_Trade_Module\Конфигурация\Catalogs\Контрагенты\Forms\ФормаВыбора\Ext\Form\Module.bsl",
]

for f in files:
    p = pathlib.Path(f)
    data = p.read_bytes()
    # Remove all BOMs at the start
    while data.startswith(BOM):
        data = data[3:]
    # Add single BOM
    data = BOM + data
    p.write_bytes(data)
    first = data[:10].hex(' ')
    print(f"  OK {p.name}: {first}")

print("\nГотово! Все файлы с одним BOM.")
