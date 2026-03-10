"""Check BOM presence in all report Template.xml files"""
import pathlib

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Reports")
if not base.exists():
    base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Reports")

for template in sorted(base.rglob("Template.xml")):
    data = template.read_bytes()
    bom = data[:3] == bytes([0xEF, 0xBB, 0xBF])
    rel = template.relative_to(base)
    report = str(rel).split("\\")[0]
    print(f"{report:30s} size={len(data):6d}  BOM={'YES' if bom else 'NO '}  first_byte={data[0]:02x}")
