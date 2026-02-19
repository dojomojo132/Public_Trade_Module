# -*- coding: utf-8 -*-
import pathlib

p = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\ConfigDumpInfo.xml")
c = p.read_text(encoding="utf-8-sig")
lines = c.splitlines()
print(f"Total lines: {len(lines)}")
print("\nLast 25 lines:")
for i in range(max(0, len(lines)-25), len(lines)):
    print(f"  {i+1}: {lines[i]}")
