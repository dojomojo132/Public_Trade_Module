# -*- coding: utf-8 -*-
import pathlib
f = pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Спецификации\ТЕХНИЧЕСКАЯ СПЕЦИФИКАЦИЯ КОНФИГУРАЦИИ PTM (Public Trade Module).xml")
lines = f.read_text(encoding="utf-8").splitlines()
for i, l in enumerate(lines, 1):
    if "Импорт" in l or "DataProcessor" in l or "Обработк" in l:
        print(f"L{i}: {l[:150]}")
