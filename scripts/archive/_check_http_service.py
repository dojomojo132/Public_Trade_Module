"""Проверка файлов HTTP-сервиса мобильной кассы"""
import os, glob

base = r"D:\Git\Public_Trade_Module\Конфигурация_PTM_Analytics\HTTPServices"
print("=== HTTPServices dir ===")
for item in os.listdir(base):
    print(f"  {item}")

# Найти XML и BSL файлы HTTP-сервиса мобильной кассы
for root, dirs, files in os.walk(base):
    for f in files:
        fp = os.path.join(root, f)
        rel = os.path.relpath(fp, base)
        data = open(fp, 'rb').read()
        bom = "BOM" if data[:3] == b'\xef\xbb\xbf' else "NO-BOM"
        crlf_count = data.count(b'\r\n')
        lf_only = data.count(b'\n') - crlf_count
        print(f"\n--- {rel} ---")
        print(f"  Size: {len(data)} bytes, {bom}, CRLF: {crlf_count}, LF-only: {lf_only}")
        if f.endswith('.bsl'):
            text = data.decode('utf-8-sig')
            lines = text.splitlines()
            print(f"  Lines: {len(lines)}")
            # Check for null bytes or weird chars
            null_count = data.count(b'\x00')
            if null_count:
                print(f"  WARNING: {null_count} null bytes found!")
            # Print first 3 and last 3 lines
            for i, line in enumerate(lines[:3]):
                print(f"  L{i+1}: {line[:80]}")
            print("  ...")
            for i, line in enumerate(lines[-3:], len(lines)-2):
                print(f"  L{i}: {line[:80]}")
        elif f.endswith('.xml'):
            text = data.decode('utf-8-sig')
            lines = text.splitlines()
            print(f"  Lines: {len(lines)}")
            for i, line in enumerate(lines[:5]):
                print(f"  L{i+1}: {line[:120]}")

# Also check MCP HTTP service for comparison
mcp_base = r"D:\Git\Public_Trade_Module\MCP_Extension\HTTPServices"
if os.path.exists(mcp_base):
    print("\n\n=== MCP HTTPServices dir ===")
    for item in os.listdir(mcp_base):
        print(f"  {item}")
