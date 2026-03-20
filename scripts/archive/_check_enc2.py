# -*- coding: utf-8 -*-
import pathlib

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация_PTM_Driver_Vchasno\DataProcessors\Вчсн_КассаПанель\Forms\Форма")

for f in base.rglob("*"):
    if f.is_file():
        data = f.read_bytes()
        bom = "BOM" if data[:3] == b"\xef\xbb\xbf" else "NO-BOM"
        crlf = "CRLF" if b"\r\n" in data else "LF"
        rel = f.relative_to(base)
        print(f"{bom} {crlf} {len(data):>6}B  {rel}")
