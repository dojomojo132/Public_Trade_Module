# -*- coding: utf-8 -*-
"""Find ALL files that differ between original and working copy."""
import pathlib
import hashlib

ORIG = pathlib.Path(r'D:\Git\Public_Trade_Module\Конфигурация')
WORK = pathlib.Path(r'D:\Git\Public_Trade_Module\Конфигурация\Проверка')

# Exclusion: don't compare Проверка with itself, or _test_backup
EXCLUDE_DIRS = {'Проверка', '_test_backup'}

def get_file_hash(path):
    try:
        return hashlib.md5(path.read_bytes()).hexdigest()
    except:
        return None

def get_all_files(base, exclude_dirs=None):
    result = {}
    for f in base.rglob('*'):
        if f.is_file():
            rel = f.relative_to(base)
            # Check exclusion
            skip = False
            if exclude_dirs:
                for part in rel.parts:
                    if part in exclude_dirs:
                        skip = True
                        break
            if not skip:
                result[str(rel)] = f
    return result

orig_files = get_all_files(ORIG, EXCLUDE_DIRS)
work_files = get_all_files(WORK)

orig_set = set(orig_files.keys())
work_set = set(work_files.keys())

added = work_set - orig_set
removed = orig_set - work_set
common = orig_set & work_set

modified = []
for rel in sorted(common):
    h1 = get_file_hash(orig_files[rel])
    h2 = get_file_hash(work_files[rel])
    if h1 != h2:
        modified.append(rel)

print("=" * 70)
print("FILE DIFFERENCES: Original vs Проверка")
print("=" * 70)
print(f"Original files: {len(orig_files)}")
print(f"Working files:  {len(work_files)}")
print(f"Added:    {len(added)}")
print(f"Removed:  {len(removed)}")
print(f"Modified: {len(modified)}")
print(f"Same:     {len(common) - len(modified)}")

if added:
    print(f"\n--- ADDED FILES ({len(added)}) ---")
    for f in sorted(added):
        size = work_files[f].stat().st_size
        print(f"  + {f}  ({size} bytes)")

if removed:
    print(f"\n--- REMOVED FILES ({len(removed)}) ---")
    for f in sorted(removed):
        print(f"  - {f}")

if modified:
    print(f"\n--- MODIFIED FILES ({len(modified)}) ---")
    for f in sorted(modified):
        o_size = orig_files[f].stat().st_size
        w_size = work_files[f].stat().st_size
        delta = w_size - o_size
        sign = '+' if delta > 0 else ''
        print(f"  ~ {f}  ({o_size} -> {w_size}, {sign}{delta})")
