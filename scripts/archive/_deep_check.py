"""Deep check of Template.xml content"""
import pathlib

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Reports")

# Check our file vs a known working one
our_file = base / r"ДвижениеТоваров\Templates\ОсновнаяСхемаКомпоновкиДанных\Ext\Template.xml"
good_file = base / r"ОстаткиТоваров\Templates\ОсновнаяСхемаКомпоновкиДанных\Ext\Template.xml"

for label, f in [("ДвижениеТоваров", our_file), ("ОстаткиТоваров (ref)", good_file)]:
    data = f.read_bytes()
    print(f"\n=== {label} ===")
    print(f"Size: {len(data)}")
    print(f"First 20 bytes hex: {data[:20].hex(' ')}")
    
    # Check for null bytes
    null_count = data.count(b'\x00')
    print(f"Null bytes: {null_count}")
    
    # Check CRLF vs LF
    crlf = data.count(b'\r\n')
    lf_only = data.count(b'\n') - crlf
    print(f"CRLF: {crlf}, LF-only: {lf_only}")
    
    # Decode and check
    text = data.decode('utf-8-sig')
    stripped = text.strip()
    print(f"After strip, first 50 repr: {repr(stripped[:50])}")
    print(f"Starts with <?xml: {stripped.startswith('<?xml')}")
    
    # Check for invisible chars before <?xml
    xml_pos = text.find('<?xml')
    print(f"Position of <?xml: {xml_pos}")
    if xml_pos > 0:
        before = text[:xml_pos]
        print(f"Chars before <?xml: {repr(before)}")
