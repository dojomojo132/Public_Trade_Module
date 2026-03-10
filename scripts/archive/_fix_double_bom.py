# -*- coding: utf-8 -*-
"""Fix double BOM in ДвижениеТоваров Template.xml"""
import pathlib

BOM = b'\xef\xbb\xbf'
base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")
rel = pathlib.Path(r"Reports\ДвижениеТоваров\Templates\ОсновнаяСхемаКомпоновкиДанных\Ext\Template.xml")

for folder_name in ["", "Проверка"]:
    folder = base / folder_name if folder_name else base
    f = folder / rel
    if not f.exists():
        print(f"SKIP: {f}")
        continue
    data = f.read_bytes()
    # Remove all BOMs at start
    while data.startswith(BOM):
        data = data[3:]
    # Add single BOM
    data = BOM + data
    f.write_bytes(data)
    print(f"  OK {folder_name or 'Main'}: first={data[:10].hex(' ')}, size={len(data)}")
