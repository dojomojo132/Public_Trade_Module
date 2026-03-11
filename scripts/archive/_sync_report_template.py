"""Sync ДвижениеТоваров Template.xml from Конфигурация/ to Проверка/"""
import pathlib, shutil

base = pathlib.Path(r'd:\Git\Public_Trade_Module')

# Find Конфигурация folder using Unicode
cfg = None
for d in base.iterdir():
    if d.is_dir() and d.name.startswith('\u041a\u043e\u043d\u0444\u0438\u0433\u0443\u0440\u0430\u0446\u0438\u044f'):
        cfg = d
        break

if not cfg:
    print("ERROR: Cannot find folder")
    exit(1)

# Find Проверка subfolder
proverka = None
for d in cfg.iterdir():
    if d.is_dir() and d.name.startswith('\u041f\u0440\u043e\u0432\u0435\u0440\u043a\u0430'):
        proverka = d
        break

if not proverka:
    print("ERROR: Cannot find Proverka folder")
    exit(1)

# Source and dest paths
src_template = cfg / 'Reports'
dst_template = proverka / 'Reports'

# Find ДвижениеТоваров
src_report = None
for d in src_template.iterdir():
    if '\u0414\u0432\u0438\u0436\u0435\u043d\u0438\u0435\u0422\u043e\u0432\u0430\u0440\u043e\u0432' in d.name:
        src_report = d
        break

dst_report = None
for d in dst_template.iterdir():
    if '\u0414\u0432\u0438\u0436\u0435\u043d\u0438\u0435\u0422\u043e\u0432\u0430\u0440\u043e\u0432' in d.name:
        dst_report = d
        break

if not src_report or not dst_report:
    print("ERROR: Cannot find report folders")
    print(f"  src: {src_report}")
    print(f"  dst: {dst_report}")
    exit(1)

# Find Template.xml in subfolders
src_files = list(src_report.rglob('Template.xml'))
dst_dir = None
for d in dst_report.rglob('Ext'):
    if d.is_dir():
        dst_dir = d
        break

print(f"Source: {src_files[0]}")
print(f"Dest dir: {dst_dir}")

src = src_files[0]
dst = dst_dir / 'Template.xml'

# Copy
shutil.copy2(src, dst)

# Verify BOM
data = dst.read_bytes()[:10]
hex_str = ' '.join(f'{b:02x}' for b in data)
print(f"First bytes: {hex_str}")

if data[:6] == b'\xef\xbb\xbf\xef\xbb\xbf':
    print("WARNING: Double BOM detected! Fixing...")
    full_data = dst.read_bytes()
    dst.write_bytes(b'\xef\xbb\xbf' + full_data[6:])
    print("Fixed.")
else:
    print("OK: No double BOM")

# Verify sizes
print(f"Source size: {src.stat().st_size}")
print(f"Dest size:   {dst.stat().st_size}")
print("DONE: Template.xml synced successfully")
