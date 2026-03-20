# -*- coding: utf-8 -*-
"""Check for suspicious UUIDs (too-patterned like a1b2c3d4)"""
import os
import re

base = r'd:\Git\Public_Trade_Module'
config_dir = os.path.join(base, "Конфигурация")
cdi_path = os.path.join(config_dir, "ConfigDumpInfo.xml")

# Pattern for all UUIDs
uuid_pattern = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.I)

# Check if UUID looks "fabricated" (sequential hex digits)
def is_suspicious(uuid_str):
    # Remove dashes
    clean = uuid_str.replace('-', '')
    # Check for sequential patterns
    suspicious_patterns = [
        'a1b2c3d4',  # Our known suspect
        'e1234567',  # Another pattern
        'a4b5c6d7',  # Another pattern
        'a3f7e2d1',  # Check this one too
        '3a4b5c6d',  # ФОП uuid from backup
    ]
    for p in suspicious_patterns:
        if p in clean:
            return True
    return False

print("=== Checking CDI for suspicious UUIDs ===")
with open(cdi_path, 'r', encoding='utf-8-sig') as f:
    for i, line in enumerate(f, 1):
        uuids = uuid_pattern.findall(line)
        for u in uuids:
            if is_suspicious(u):
                print(f"  CDI line {i}: UUID={u}")
                print(f"    {line.strip()[:150]}")

print("\n=== Checking НалоговыеГруппы.xml for all UUIDs ===")
ng_path = os.path.join(config_dir, "Catalogs", "НалоговыеГруппы.xml")
with open(ng_path, 'r', encoding='utf-8-sig') as f:
    for i, line in enumerate(f, 1):
        uuids = uuid_pattern.findall(line)
        for u in uuids:
            if is_suspicious(u):
                print(f"  НГ line {i}: UUID={u} SUSPICIOUS")
                print(f"    {line.strip()}")

print("\n=== Checking Номенклатура.xml for suspicious UUIDs ===")
nom_path = os.path.join(config_dir, "Catalogs", "Номенклатура.xml")
with open(nom_path, 'r', encoding='utf-8-sig') as f:
    for i, line in enumerate(f, 1):
        uuids = uuid_pattern.findall(line)
        for u in uuids:
            if is_suspicious(u):
                print(f"  Ном line {i}: UUID={u} SUSPICIOUS")
                print(f"    {line.strip()}")

print("\n=== All suspicious UUIDs across ALL config XML files ===")
count = 0
for root, dirs, files in os.walk(config_dir):
    for fname in files:
        if fname.endswith('.xml'):
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, 'r', encoding='utf-8-sig') as f:
                    content = f.read()
                for i, line in enumerate(content.split('\n'), 1):
                    uuids = uuid_pattern.findall(line)
                    for u in uuids:
                        if is_suspicious(u):
                            rel = os.path.relpath(fpath, base)
                            print(f"  {rel}:{i}: {u}")
                            print(f"    {line.strip()[:150]}")
                            count += 1
            except:
                pass
print(f"\nTotal suspicious UUIDs found: {count}")
