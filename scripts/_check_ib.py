# -*- coding: utf-8 -*-
"""Check extensions in InfoBase directory structure."""
import os

ib_path = r"D:\Confiq\Public Trade Module"

print(f"IB path: {ib_path}")
print(f"Exists: {os.path.exists(ib_path)}")
print()

# List top-level contents
for item in sorted(os.listdir(ib_path)):
    full = os.path.join(ib_path, item)
    size = os.path.getsize(full) if os.path.isfile(full) else "DIR"
    print(f"  {item:40s} {size}")

# Check for extension directories
print("\n--- Extension dirs ---")
for item in os.listdir(ib_path):
    if item.lower().startswith("ext"):
        full = os.path.join(ib_path, item)
        print(f"\n  {item}/")
        if os.path.isdir(full):
            for sub in os.listdir(full):
                sub_full = os.path.join(full, sub)
                size = os.path.getsize(sub_full) if os.path.isfile(sub_full) else "DIR"
                print(f"    {sub:36s} {size}")
