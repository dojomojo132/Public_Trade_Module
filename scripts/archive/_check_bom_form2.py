# -*- coding: utf-8 -*-
import pathlib

path = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Catalogs\Контрагенты\Forms\ФормаВыбора\Ext\Form.xml")
data = path.read_bytes()
print(f"First 10 bytes: {data[:10].hex(' ')}")
print(f"Has BOM: {data[:3] == b'\\xef\\xbb\\xbf'}")
print(f"File size: {len(data)}")

# Check for double BOM
if data[:6] == b'\xef\xbb\xbf\xef\xbb\xbf':
    print("DOUBLE BOM detected!")

# Also check the working ФормаГруппы for comparison
path2 = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Catalogs\Контрагенты\Forms\ФормаГруппы\Ext\Form.xml")
data2 = path2.read_bytes()
print(f"\nФормаГруппы first 10 bytes: {data2[:10].hex(' ')}")
print(f"ФормаГруппы Has BOM: {data2[:3] == b'\\xef\\xbb\\xbf'}")
