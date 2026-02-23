# -*- coding: utf-8 -*-
"""Проверка XML структуры ConfigDumpInfo.xml."""
import pathlib
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка")

cdi = ROOT / "ConfigDumpInfo.xml"
data = cdi.read_bytes()
bom = data[:3] if data[:3] == b"\xef\xbb\xbf" else b""
text = data[len(bom):].decode("utf-8")

# Проверить XML
try:
    ET.fromstring(text)
    print("ConfigDumpInfo.xml: XML валидный")
except ET.ParseError as e:
    print(f"ConfigDumpInfo.xml: XML ОШИБКА: {e}")

# Проверить дубликаты id
import re
ids = re.findall(r' id="([^"]+)"', text)
seen = {}
for idx in ids:
    if idx in seen:
        print(f"  ДУБЛИКАТ id: {idx}")
    seen[idx] = True
print(f"Всего id: {len(ids)}, уникальных: {len(seen)}")

# Найти строки с ТестыРМК
for i, line in enumerate(text.splitlines(), 1):
    if "ТестыРМК" in line:
        print(f"  [{i}]: {line.strip()}")

# Также проверить Configuration.xml
conf = ROOT / "Configuration.xml"
data2 = conf.read_bytes()
bom2 = data2[:3] if data2[:3] == b"\xef\xbb\xbf" else b""
text2 = data2[len(bom2):].decode("utf-8")
try:
    ET.fromstring(text2)
    print("\nConfiguration.xml: XML валидный")
except ET.ParseError as e:
    print(f"\nConfiguration.xml: XML ОШИБКА: {e}")
for i, line in enumerate(text2.splitlines(), 1):
    if "ТестыРМК" in line:
        print(f"  [{i}]: {line.strip()}")

# Проверить ТестыРМК.xml
dp = ROOT / "DataProcessors" / "ТестыРМК.xml"
data3 = dp.read_bytes()
bom3 = data3[:3] if data3[:3] == b"\xef\xbb\xbf" else b""
text3 = data3[len(bom3):].decode("utf-8")
try:
    ET.fromstring(text3)
    print("\nТестыРМК.xml: XML валидный")
except ET.ParseError as e:
    print(f"\nТестыРМК.xml: XML ОШИБКА: {e}")

# Проверить Форма.xml
f1 = ROOT / "DataProcessors" / "ТестыРМК" / "Forms" / "Форма.xml"
data4 = f1.read_bytes()
bom4 = data4[:3] if data4[:3] == b"\xef\xbb\xbf" else b""
text4 = data4[len(bom4):].decode("utf-8")
try:
    ET.fromstring(text4)
    print("Форма.xml: XML валидный")
except ET.ParseError as e:
    print(f"Форма.xml: XML ОШИБКА: {e}")

# Проверить Form.xml
f2 = ROOT / "DataProcessors" / "ТестыРМК" / "Forms" / "Форма" / "Ext" / "Form.xml"
data5 = f2.read_bytes()
bom5 = data5[:3] if data5[:3] == b"\xef\xbb\xbf" else b""
text5 = data5[len(bom5):].decode("utf-8")
try:
    ET.fromstring(text5)
    print("Form.xml: XML валидный")
except ET.ParseError as e:
    print(f"Form.xml: XML ОШИБКА: {e}")

print("\n=== Готово ===")
