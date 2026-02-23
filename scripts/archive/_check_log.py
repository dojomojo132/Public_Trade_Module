# -*- coding: utf-8 -*-
import pathlib

log_path = pathlib.Path(r"D:\Git\Public_Trade_Module\temp_load.log")

if log_path.exists():
    print("=== ЛОГ ЗАГРУЗКИ КОНФИГУРАЦИИ ===\n")
    with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
        if content.strip():
            print(content)
        else:
            print("(лог пустой)")
else:
    print("Файл логаne найден")
