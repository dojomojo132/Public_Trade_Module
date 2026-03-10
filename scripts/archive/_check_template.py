"""Check both Template.xml files"""
import pathlib

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")
rel = pathlib.Path(r"Reports\ДвижениеТоваров\Templates\ОсновнаяСхемаКомпоновкиДанных\Ext\Template.xml")

for label, folder in [("Main", base), ("Проверка", base / "Проверка")]:
    f = folder / rel
    print(f"\n=== {label} ===")
    print(f"Path: {f}")
    print(f"Exists: {f.exists()}")
    if f.exists():
        data = f.read_bytes()
        print(f"Size: {len(data)} bytes")
        print(f"First 3 bytes (hex): {data[:3].hex()}")
        print(f"BOM: {'YES' if data[:3] == bytes([0xEF, 0xBB, 0xBF]) else 'NO'}")
        # Check first line
        text = data.decode('utf-8-sig')
        first_line = text.split('\n')[0][:80]
        print(f"First line: {first_line}")
        print(f"Total lines: {text.count(chr(10)) + 1}")
        # Check if content looks like XML
        stripped = text.strip()
        print(f"Starts with <?xml: {stripped.startswith('<?xml')}")
        print(f"Ends with </DataCompositionSchema>: {stripped.endswith('</DataCompositionSchema>')}")
    else:
        # Check parent dir
        parent = f.parent
        print(f"Parent exists: {parent.exists()}")
        if parent.exists():
            print(f"Parent contents: {list(parent.iterdir())}")
        # Check if there's a similar file nearby
        gp = parent.parent
        if gp.exists():
            print(f"GrandParent contents: {list(gp.iterdir())}")
