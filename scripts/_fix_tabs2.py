"""Fix ALL remaining literal \\t in query text"""
import pathlib

p = pathlib.Path(r"d:\Git\Public_Trade_Module\Конфигурация_PTM_Fiscal\CommonModules\Фскл_ФискализацияСервер\Ext\Module.bsl")
data = p.read_text(encoding="utf-8-sig")

old = "|\\tКассы.Оборудование"
new = "|\tКассы.Оборудование"

count = data.count(old)
print(f"Found {count} occurrences of literal \\t before Кассы.Оборудование")
if count > 0:
    data = data.replace(old, new)
    p.write_text(data, encoding="utf-8-sig")
    print(f"FIXED: {count} replacement(s)")

# Final verification
data2 = p.read_text(encoding="utf-8-sig")
lines = data2.split("\n")
found = False
for i, line in enumerate(lines, 1):
    if "\\t" in line:
        print(f"  REMAINING: line {i}: {repr(line.rstrip()[:80])}")
        found = True
if not found:
    print("  ALL CLEAN: no literal \\t remaining")
