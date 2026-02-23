# -*- coding: utf-8 -*-
"""Диагностика XML файлов ТестыРМК."""
import pathlib
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка")

files_xml = [
    ROOT / "DataProcessors" / "ТестыРМК.xml",
    ROOT / "DataProcessors" / "ТестыРМК" / "Forms" / "Форма.xml",
    ROOT / "DataProcessors" / "ТестыРМК" / "Forms" / "Форма" / "Ext" / "Form.xml",
]

print("=== Валидация XML файлов ===")
for f in files_xml:
    if not f.exists():
        print(f"  НЕТ: {f.name}")
        continue
    try:
        data = f.read_bytes()
        # Удалить BOM для парсинга (ElementTree не понимает BOM как часть UTF-8 в Python<3.8)
        if data[:3] == b"\xef\xbb\xbf":
            data = data[3:]
        ET.fromstring(data)
        print(f"  OK XML: {f.relative_to(ROOT)}")
    except ET.ParseError as e:
        print(f"  ERROR XML: {f.relative_to(ROOT)}")
        print(f"    {e}")

print()
print("=== Содержимое Form.xml (первые 30 строк) ===")
form_xml = ROOT / "DataProcessors" / "ТестыРМК" / "Forms" / "Форма" / "Ext" / "Form.xml"
data = form_xml.read_bytes()
if data[:3] == b"\xef\xbb\xbf":
    data = data[3:]
text = data.decode("utf-8")
for i, line in enumerate(text.split("\n")[:30], 1):
    print(f"  {i:3}: {line}")
