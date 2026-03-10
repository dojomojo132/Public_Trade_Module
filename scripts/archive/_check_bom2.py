# -*- coding: utf-8 -*-
"""Проверка BOM в ключевых файлах конфигурации."""
import pathlib

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка")

files_to_check = [
    ROOT / "Configuration.xml",
    ROOT / "ConfigDumpInfo.xml",
    ROOT / "DataProcessors" / "ТестыРМК.xml",
    ROOT / "DataProcessors" / "ТестыРМК" / "Forms" / "Форма.xml",
    ROOT / "DataProcessors" / "ТестыРМК" / "Forms" / "Форма" / "Ext" / "Form.xml",
    ROOT / "DataProcessors" / "ТестыРМК" / "Forms" / "Форма" / "Ext" / "Form" / "Module.bsl",
]

print("=== BOM / Encoding проверка ===")
for f in files_to_check:
    if not f.exists():
        print(f"  НЕТ: {f.name}")
        continue
    b = f.read_bytes()
    bom = "BOM" if b[:3] == b"\xef\xbb\xbf" else "no-BOM"
    # Проверить XML декларацию
    snippet = b[:50].replace(b"\xef\xbb\xbf", b"").decode("utf-8", errors="replace")
    name = f.name
    print(f"  {bom}  {name}  | start: {snippet[:40]!r}")
