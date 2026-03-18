# -*- coding: utf-8 -*-
"""Fix first line of Module.bsl - remove stray parenthesis."""
import pathlib

p = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация_PTM_Fiscal\CommonModules\Фскл_ФискализацияСервер\Ext\Module.bsl")
content = p.read_bytes()
print("First 70 bytes:", repr(content[:70]))

# Fix: replace "#Область ПрограммныйИнтерфейс)" with "#Область ПрограммныйИнтерфейс"
old = "#Область ПрограммныйИнтерфейс)".encode("utf-8")
new = "#Область ПрограммныйИнтерфейс".encode("utf-8")
if old in content:
    content = content.replace(old, new, 1)
    p.write_bytes(content)
    print("FIXED: removed stray ')'")
else:
    print("Pattern not found - already fixed or different encoding")
