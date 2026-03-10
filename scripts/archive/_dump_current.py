# -*- coding: utf-8 -*-
"""Dump config from ИБ, then merge our form on top, then load back"""
import subprocess
import pathlib
import shutil
import os

exe = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
ib_path = r"D:\Confiq\Public Trade Module"
dump_path = r"D:\Git\Public_Trade_Module\Конфигурация\_DumpTemp"
log_dir = r"D:\Git\Public_Trade_Module\Документация\Валидация\logs"

# Step 1: DumpConfigToFiles
print("Step 1: DumpConfigToFiles to _DumpTemp...")
if os.path.exists(dump_path):
    shutil.rmtree(dump_path)
os.makedirs(dump_path)

log1 = os.path.join(log_dir, "dump-config.log")
cmd1 = [
    exe, "DESIGNER",
    "/F", ib_path,
    "/DumpConfigToFiles", dump_path,
    "/DisableStartupDialogs",
    "/DisableStartupMessages",
    "/Out", log1
]
result = subprocess.run(cmd1, timeout=300)
log1_text = pathlib.Path(log1).read_text(encoding='utf-8-sig').strip() if pathlib.Path(log1).exists() else "[NO LOG]"
print(f"  Exit code: {result.returncode}")
print(f"  Log: {log1_text[:300] if log1_text else '[EMPTY]'}")

if result.returncode != 0:
    print("FAILED!")
    import sys; sys.exit(1)

# Check what we got
print(f"\nDump contains:")
for root, dirs, files in os.walk(dump_path):
    level = root.replace(dump_path, '').count(os.sep)
    indent = ' ' * 2 * level
    print(f"{indent}{os.path.basename(root)}/")
    subindent = ' ' * 2 * (level + 1)
    for file in files[:10]:
        print(f"{subindent}{file}")
    if len(files) > 10:
        print(f"{subindent}... and {len(files)-10} more")
