# -*- coding: utf-8 -*-
import os, pathlib

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация_PTM_Driver_Vchasno\DataProcessors\Вчсн_КассаПанель")

files = [
    base / "Forms" / "Форма" / "Ext" / "Form.xml",
    base / "Forms" / "Форма" / "Ext" / "Form" / "Module.bsl",
    base / "Forms" / "Форма.xml",
]

for f in files:
    if f.exists():
        data = f.read_bytes()
        bom = "BOM" if data[:3] == b"\xef\xbb\xbf" else "NO-BOM"
        crlf = "CRLF" if b"\r\n" in data else "LF"
        print(f"{bom} {crlf} {len(data):>6}B  {f.name}")
    else:
        print(f"MISSING  {f.name}")
