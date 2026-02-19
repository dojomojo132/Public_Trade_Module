# -*- coding: utf-8 -*-
import subprocess
import os

os.chdir(r"D:\Git\Public_Trade_Module")
os.environ["GIT_CONFIG_PARAMETERS"] = "'core.quotePath=false'"

# 1. Show what files were in the BPO merge commit
result = subprocess.run(
    ["git", "diff", "--name-only", "960be69", "f8d6d1a"],
    capture_output=True, encoding="utf-8", errors="replace"
)
all_files = [f for f in result.stdout.strip().split('\n') if f]
print(f"=== TOTAL BPO FILES: {len(all_files)} ===")

# 2. Categorize by folder type
categories = {}
for f in all_files:
    parts = f.split('/')
    if len(parts) >= 2:
        cat = parts[1]  # Second level folder
    else:
        cat = "(root)"
    if cat not in categories:
        categories[cat] = []
    categories[cat].append(f)

for cat, files in sorted(categories.items(), key=lambda x: -len(x[1])):
    print(f"\n{cat}: {len(files)} files")
    # Show first 5 files
    for f in files[:5]:
        print(f"  {f}")
    if len(files) > 5:
        print(f"  ... and {len(files)-5} more")

# 3. List CommonModules
print("\n\n=== COMMON MODULES IN BPO ===")
modules = [f for f in all_files if '/CommonModules/' in f and f.endswith('.xml') and f.count('/') == 2]
for m in sorted(modules):
    print(f"  {m}")

# 4. List DataProcessors
print("\n=== DATA PROCESSORS IN BPO ===")
procs = set()
for f in all_files:
    if '/DataProcessors/' in f:
        parts = f.split('/')
        idx = parts.index('DataProcessors')
        if idx + 1 < len(parts):
            procs.add(parts[idx + 1])
for p in sorted(procs):
    print(f"  {p}")

# 5. List Catalogs
print("\n=== CATALOGS IN BPO ===")
cats = set()
for f in all_files:
    if '/Catalogs/' in f:
        parts = f.split('/')
        idx = parts.index('Catalogs')
        if idx + 1 < len(parts):
            cats.add(parts[idx + 1])
for c in sorted(cats):
    print(f"  {c}")

# 6. List Enums
print("\n=== ENUMS IN BPO ===")
enums = set()
for f in all_files:
    if '/Enums/' in f:
        parts = f.split('/')
        idx = parts.index('Enums')
        if idx + 1 < len(parts):
            enums.add(parts[idx + 1])
for e in sorted(enums):
    print(f"  {e}")

# 7. Show BPO-specific scanner/printer related files
print("\n\n=== SCANNER/PRINTER RELATED ===")
scanner_printer_keywords = ['сканер', 'scanner', 'принтер', 'printer', 'чек', 'этикет', 'label', 'receipt', 'pos', 'kkm', 'ккм', 'ккт']
for f in all_files:
    f_lower = f.lower()
    if any(kw in f_lower for kw in scanner_printer_keywords):
        print(f"  {f}")
