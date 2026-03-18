"""Check for literal \\t vs real tab in BSL file"""
import pathlib

p = pathlib.Path(r"d:\Git\Public_Trade_Module\Конфигурация_PTM_Fiscal\CommonModules\Фскл_ФискализацияСервер\Ext\Module.bsl")
data = p.read_text(encoding="utf-8-sig")
lines = data.split("\n")
for i, line in enumerate(lines, 1):
    if "\\t" in line:
        print(f"Line {i}: LITERAL \\t: {repr(line.rstrip()[:100])}")
