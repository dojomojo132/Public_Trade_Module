# -*- coding: utf-8 -*-
import subprocess
import os

os.chdir(r"D:\Git\Public_Trade_Module")
os.environ["GIT_CONFIG_PARAMETERS"] = "'core.quotePath=false'"

# Get the diff between pre-BPO and BPO commits
result = subprocess.run(
    ["git", "diff", "--name-only", "960be69", "f8d6d1a"],
    capture_output=True, encoding="utf-8", errors="replace"
)
all_files = [f for f in result.stdout.strip().split('\n') if f]
bpo_files = [f for f in all_files if f.startswith('Конфигурация/')]

print(f"Total BPO config files: {len(bpo_files)}")

# Count by top-level metadata type
types_count = {}
for f in bpo_files:
    parts = f.replace('Конфигурация/', '').split('/')
    if len(parts) >= 1:
        t = parts[0]
        if t not in types_count:
            types_count[t] = 0
        types_count[t] += 1

print("\nBy metadata type:")
for t, c in sorted(types_count.items(), key=lambda x: -x[1]):
    print(f"  {t}: {c}")

# Count unique objects per type
print("\nUnique objects per metadata type:")
objects_by_type = {}
for f in bpo_files:
    parts = f.replace('Конфигурация/', '').split('/')
    if len(parts) >= 2:
        obj_type = parts[0]
        obj_name = parts[1].replace('.xml', '')
        key = f"{obj_type}/{obj_name}"
        if key not in objects_by_type:
            objects_by_type[key] = obj_type
            
type_obj_counts = {}
for key, obj_type in objects_by_type.items():
    if obj_type not in type_obj_counts:
        type_obj_counts[obj_type] = []
    type_obj_counts[obj_type].append(key.split('/')[1])

for t in sorted(type_obj_counts.keys()):
    objs = type_obj_counts[t]
    print(f"\n  {t} ({len(objs)} objects):")
    for o in sorted(objs):
        print(f"    - {o}")

# Check which files were MODIFIED (not added) in BPO merge
print("\n\n=== MODIFIED (not new) files ===")
result_mod = subprocess.run(
    ["git", "diff", "--diff-filter=M", "--name-only", "960be69", "f8d6d1a"],
    capture_output=True, encoding="utf-8", errors="replace"
)
modified = [f for f in result_mod.stdout.strip().split('\n') if f and f.startswith('Конфигурация/')]
for f in sorted(modified):
    print(f"  {f}")
