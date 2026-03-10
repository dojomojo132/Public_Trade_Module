# -*- coding: utf-8 -*-
"""Пересоздаёт дескриптор ФормаГруппы.xml по образцу ФормаСписка.xml."""
import pathlib

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Catalogs\Номенклатура\Forms")
base2 = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Catalogs\Номенклатура\Forms")

# Читаем эталон (ФормаСписка.xml) побайтово
src = (base / "ФормаСписка.xml").read_bytes()

# Заменяем данные
result = src.replace(
    b'a4b5c6d7-e8f9-4012-a3b4-c5d6e7f8a9b0',
    b'b96d6d98-dfdc-4fa7-9250-48fd8d13eae7'
)
result = result.replace(
    '<Name>\xd0\xa4\xd0\xbe\xd1\x80\xd0\xbc\xd0\xb0\xd0\xa1\xd0\xbf\xd0\xb8\xd1\x81\xd0\xba\xd0\xb0</Name>'.encode('utf-8'),
    '<Name>\xd0\xa4\xd0\xbe\xd1\x80\xd0\xbc\xd0\xb0\xd0\x93\xd1\x80\xd1\x83\xd0\xbf\xd0\xbf\xd1\x8b</Name>'.encode('utf-8')
)
result = result.replace(
    '\xd0\xa4\xd0\xbe\xd1\x80\xd0\xbc\xd0\xb0 \xd1\x81\xd0\xbf\xd0\xb8\xd1\x81\xd0\xba\xd0\xb0'.encode('utf-8'),
    '\xd0\xa4\xd0\xbe\xd1\x80\xd0\xbc\xd0\xb0 \xd0\xb3\xd1\x80\xd1\x83\xd0\xbf\xd0\xbf\xd1\x8b'.encode('utf-8')
)

for b in [base, base2]:
    dst = b / "\u0424\u043e\u0440\u043c\u0430\u0413\u0440\u0443\u043f\u043f\u044b.xml"
    dst.write_bytes(result)
    print(f"СОЗДАН: {dst} ({len(result)} bytes)")
    print(f"  Ends with: {result[-10:].hex()}")

print("\nПроверка содержимого:")
print(result.decode('utf-8-sig'))
