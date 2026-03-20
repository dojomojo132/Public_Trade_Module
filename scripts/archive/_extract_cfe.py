# -*- coding: utf-8 -*-
"""Extract .cfe file for analysis."""
import os, zipfile, sys, struct

PRRO_DIR = r"D:\Git\Public_Trade_Module\PRRO"
OUT_DIR = os.path.join(PRRO_DIR, "_extracted")

# Find the .cfe file
cfe_files = [f for f in os.listdir(PRRO_DIR) if f.endswith('.cfe')]
if not cfe_files:
    print("No .cfe files found")
    sys.exit(1)

cfe_path = os.path.join(PRRO_DIR, cfe_files[0])
print(f"Found: {cfe_files[0]}")
print(f"Size: {os.path.getsize(cfe_path)} bytes")

# Read header to understand format
with open(cfe_path, 'rb') as f:
    header = f.read(64)
    print(f"Header (hex): {header[:32].hex()}")
    print(f"Header (ascii attempt): {header[:64]}")

# Try ZIP extraction
try:
    with zipfile.ZipFile(cfe_path, 'r') as z:
        os.makedirs(OUT_DIR, exist_ok=True)
        z.extractall(OUT_DIR)
        print(f"\nExtracted {len(z.namelist())} files to _extracted/")
        for name in z.namelist():
            print(f"  {name}")
except zipfile.BadZipFile:
    print("\nNot a standard ZIP. CFE uses 1C internal format.")
    print("Trying to find XML/BSL content by scanning binary...")
    
    with open(cfe_path, 'rb') as f:
        data = f.read()
    
    # Search for XML signatures
    xml_positions = []
    pos = 0
    while True:
        pos = data.find(b'<?xml', pos)
        if pos == -1:
            break
        xml_positions.append(pos)
        pos += 1
    
    print(f"Found {len(xml_positions)} XML fragments")
    
    # Search for BSL content markers
    bsl_markers = [b'\xd0\x9f\xd1\x80\xd0\xbe\xd1\x86\xd0\xb5\xd0\xb4\xd1\x83\xd1\x80\xd0\xb0',  # Процедура
                   b'\xd0\xa4\xd1\x83\xd0\xbd\xd0\xba\xd1\x86\xd0\xb8\xd1\x8f',  # Функция
                   b'HTTPConnection', b'HTTPRequest',
                   b'/dm/execute']
    
    for marker in bsl_markers:
        positions = []
        pos = 0
        while True:
            pos = data.find(marker, pos)
            if pos == -1:
                break
            positions.append(pos)
            pos += 1
        if positions:
            label = marker.decode('utf-8', errors='replace')
            print(f"  '{label}' found at positions: {positions[:5]}")
    
    # Try to extract readable chunks
    os.makedirs(OUT_DIR, exist_ok=True)
    
    # Extract XML fragments
    for i, xpos in enumerate(xml_positions[:20]):
        # Find end of XML (look for null bytes or next section)
        end = data.find(b'\x00\x00\x00\x00', xpos + 10)
        if end == -1 or end - xpos > 500000:
            end = min(xpos + 500000, len(data))
        fragment = data[xpos:end]
        fname = os.path.join(OUT_DIR, f"xml_fragment_{i}.xml")
        with open(fname, 'wb') as f:
            f.write(fragment)
        print(f"  Saved xml_fragment_{i}.xml ({len(fragment)} bytes)")
    
    # Dump full binary for manual analysis
    raw_path = os.path.join(OUT_DIR, "raw_dump.bin")
    with open(raw_path, 'wb') as f:
        f.write(data)
    print(f"\n  Full dump saved to raw_dump.bin ({len(data)} bytes)")
