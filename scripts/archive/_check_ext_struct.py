# -*- coding: utf-8 -*-
"""Check extension folder structure."""
import pathlib

root = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация_PTM_Analytics")
print("Extension folders:")
for d in sorted(root.iterdir()):
    if d.is_dir():
        print(f"  {d.name}/")
    else:
        print(f"  {d.name}")
        
# Check if Documents directory exists with borrowed objects
docs = root / "Documents"
if docs.exists():
    print(f"\nDocuments/ contents:")
    for item in docs.rglob("*"):
        print(f"  {item.relative_to(root)}")

# Check Catalogs
cats = root / "Catalogs"
if cats.exists():
    print(f"\nCatalogs/ contents:")
    for item in cats.rglob("*"):
        print(f"  {item.relative_to(root)}")
else:
    print(f"\nNo Catalogs/ folder yet")
