# -*- coding: utf-8 -*-
import pathlib

p = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\ConfigDumpInfo.xml")
c = p.read_text(encoding="utf-8-sig")
lines = c.splitlines()
print(f"Total lines: {len(lines)}")
print("\nLast 10 lines:")
for i in range(max(0, len(lines)-10), len(lines)):
    print(f"  {i+1}: {lines[i]}")

# Check structure
print(f"\nConfigVersions closes at line: {[i+1 for i,l in enumerate(lines) if '</ConfigVersions>' in l]}")
print(f"ConfigDumpInfo closes at line: {[i+1 for i,l in enumerate(lines) if '</ConfigDumpInfo>' in l]}")

# Check the new entries are inside ConfigVersions
import re
cv_close = c.index("</ConfigVersions>")
demo_const = c.index("Constant._Д") if "Constant._Д" in c else -1
print(f"\nConfigVersions closes at char: {cv_close}")
print(f"First Constant._Д at char: {demo_const}")
print(f"Entries INSIDE ConfigVersions: {demo_const < cv_close}")
