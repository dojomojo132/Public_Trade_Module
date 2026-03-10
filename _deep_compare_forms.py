# -*- coding: utf-8 -*-
"""Глубокое сравнение файлов формы - line endings, BOM, encoding."""
import pathlib

def analyze_file(path):
    raw = path.read_bytes()
    has_bom = raw[:3] == b'\xef\xbb\xbf'
    has_crlf = b'\r\n' in raw
    has_lf_only = b'\n' in raw and not has_crlf
    has_cr_only = b'\r' in raw and not has_crlf and not has_lf_only
    content = raw.decode('utf-8-sig')
    return {
        'size': len(raw),
        'bom': has_bom, 
        'crlf': has_crlf,
        'lf_only': has_lf_only,
        'cr_only': has_cr_only,
        'lines': content.count('\n'),
        'first_20': repr(raw[:50])
    }

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Catalogs\Номенклатура\Forms")

files_to_check = [
    base / "ФормаЭлемента.xml",
    base / "ФормаГруппы.xml",
    base / "ФормаСписка.xml",
    base / "ФормаЭлемента" / "Ext" / "Form.xml",
    base / "ФормаГруппы" / "Ext" / "Form.xml",
    base / "ФормаСписка" / "Ext" / "Form.xml",
]

for f in files_to_check:
    if f.exists():
        info = analyze_file(f)
        name = str(f).split("Forms\\")[1]
        print(f"\n{name}:")
        print(f"  size={info['size']}, bom={info['bom']}, crlf={info['crlf']}, lf_only={info['lf_only']}, lines={info['lines']}")
    else:
        print(f"\nNOT FOUND: {f}")

print("\n=== Попробуем пересоздать ФормаГруппы.xml с тем же содержимым что ФормаСписка.xml ===")
# Copy structure exactly from ФормаСписка.xml
src = base / "ФормаСписка.xml"
raw_src = src.read_bytes()
print(f"ФормаСписка.xml raw last 20 bytes: {raw_src[-20:].hex()}")

dst = base / "ФормаГруппы.xml"
raw_dst = dst.read_bytes()
print(f"ФормаГруппы.xml raw last 20 bytes: {raw_dst[-20:].hex()}")

# Check if ФормаГруппы has trailing newline
if raw_dst.endswith(b'\r\n'):
    print("ФормаГруппы.xml ends with CRLF")
elif raw_dst.endswith(b'\n'):
    print("ФормаГруппы.xml ends with LF only")
else:
    print(f"ФормаГруппы.xml ends with: {raw_dst[-5:].hex()}")

if raw_src.endswith(b'\r\n'):
    print("ФормаСписка.xml ends with CRLF")
elif raw_src.endswith(b'\n'):
    print("ФормаСписка.xml ends with LF only")
else:
    print(f"ФормаСписка.xml ends with: {raw_src[-5:].hex()}")

print("\nГотово!")
