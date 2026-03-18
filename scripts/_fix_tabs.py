"""Fix literal \\t in query text — replace with real tab character"""
import pathlib

p = pathlib.Path(r"d:\Git\Public_Trade_Module\Конфигурация_PTM_Fiscal\CommonModules\Фскл_ФискализацияСервер\Ext\Module.bsl")
data = p.read_text(encoding="utf-8-sig")

old = "|\\tЧекККМ.СуммаДокумента"
new = "|\tЧекККМ.СуммаДокумента"

count = data.count(old)
if count == 0:
    print("NOT FOUND — already fixed or different encoding")
elif count > 1:
    print(f"MULTIPLE ({count}) occurrences — manual fix needed")
else:
    data = data.replace(old, new)
    p.write_text(data, encoding="utf-8-sig")
    print(f"FIXED: replaced 1 occurrence of literal \\t with real tab")

# Verify
data2 = p.read_text(encoding="utf-8-sig")
lines = data2.split("\n")
for i, line in enumerate(lines, 1):
    if "\\t" in line:
        print(f"  REMAINING literal \\t at line {i}: {repr(line.rstrip()[:80])}")
if not any("\\t" in line for line in lines):
    print("  Verification: NO literal \\t remaining — file clean")
