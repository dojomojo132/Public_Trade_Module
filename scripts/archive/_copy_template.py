"""Copy fixed Template.xml from Main to Проверка"""
import pathlib, shutil

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")
rel = pathlib.Path(r"Reports\ДвижениеТоваров\Templates\ОсновнаяСхемаКомпоновкиДанных\Ext\Template.xml")

src = base / rel
dst = base / "Проверка" / rel

print(f"src exists: {src.exists()}, size: {src.stat().st_size}")
print(f"dst exists: {dst.exists()}")

if not dst.parent.exists():
    dst.parent.mkdir(parents=True, exist_ok=True)
    print(f"Created dir: {dst.parent}")

shutil.copy2(src, dst)
print(f"Copied. dst size: {dst.stat().st_size}")

# Verify
import hashlib
h1 = hashlib.md5(src.read_bytes()).hexdigest()
h2 = hashlib.md5(dst.read_bytes()).hexdigest()
print(f"Identical: {h1 == h2}")
d = dst.read_bytes()
print(f"dst first 10 hex: {d[:10].hex(' ')}")
