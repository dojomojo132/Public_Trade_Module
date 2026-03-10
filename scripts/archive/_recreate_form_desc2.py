# -*- coding: utf-8 -*-
"""Пересоздаёт дескриптор ФормаГруппы.xml по образцу ФормаСписка.xml."""
import pathlib

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Catalogs\Номенклатура\Forms")
base2 = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Catalogs\Номенклатура\Forms")

# Читаем эталон (ФормаСписка.xml), decode
src_bytes = (base / "ФормаСписка.xml").read_bytes()
src_text = src_bytes.decode('utf-8-sig')

# Заменяем UUID
result = src_text.replace('a4b5c6d7-e8f9-4012-a3b4-c5d6e7f8a9b0', 'b96d6d98-dfdc-4fa7-9250-48fd8d13eae7')
# Заменяем имя
result = result.replace('<Name>ФормаСписка</Name>', '<Name>ФормаГруппы</Name>')
# Заменяем синоним
result = result.replace('Форма списка', 'Форма группы')

# Записываем с BOM как оригинал
result_bytes = b'\xef\xbb\xbf' + result.encode('utf-8')

for b in [base, base2]:
    dst = b / "ФормаГруппы.xml"
    dst.write_bytes(result_bytes)
    print(f"СОЗДАН: {dst.name} ({len(result_bytes)} bytes)")

print("\nСодержимое:")
print(result)
