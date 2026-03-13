import os, sys

base = r"d:\Git\Public_Trade_Module"
rel = r"Reports\ОстаткиТоваров\Templates\ОсновнаяСхемаКомпоновкиДанных\Ext\Template.xml"

f1 = os.path.join(base, "Конфигурация", rel)
f2 = os.path.join(base, "Конфигурация", "Проверка", rel)

e1 = os.path.exists(f1)
e2 = os.path.exists(f2)
print("f1 exists:", e1)
print("f2 exists:", e2)
if not e1 or not e2:
    sys.exit(1)

d1 = open(f1, "rb").read()
d2 = open(f2, "rb").read()
print("Size:", len(d1), "/", len(d2))
print("MATCH" if d1 == d2 else "MISMATCH")
