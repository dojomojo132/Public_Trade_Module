"""QC check for ДвижениеТоваров report Template.xml"""
import hashlib
import pathlib

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")
rel = r"Reports\ДвижениеТоваров\Templates\ОсновнаяСхемаКомпоновкиДанных\Ext\Template.xml"

f1 = base / rel
f2 = base / "Проверка" / rel

for label, f in [("Main", f1), ("Проверка", f2)]:
    if not f.exists():
        print(f"{label}: FILE NOT FOUND - {f}")
        continue
    data = f.read_bytes()
    h = hashlib.md5(data).hexdigest()
    bom = data[:3]
    bom_ok = bom == bytes([0xEF, 0xBB, 0xBF])
    crlf = b"\r\n" in data
    print(f"{label}: hash={h}  size={len(data)}  BOM={'OK' if bom_ok else 'MISSING'}  CRLF={'OK' if crlf else 'LF only'}")

if f1.exists() and f2.exists():
    d1 = f1.read_bytes()
    d2 = f2.read_bytes()
    print(f"\nIdentical: {d1 == d2}")
