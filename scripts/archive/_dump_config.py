# -*- coding: utf-8 -*-
"""Dump current IB config to files and compare with Проверка"""
import subprocess
import pathlib
import os

# First, find 1cv8.exe
result = subprocess.run(
    ['where', '1cv8.exe'],
    capture_output=True, text=True
)
if result.returncode == 0:
    exe = result.stdout.strip().split('\n')[0]
else:
    # Try standard path
    exe = r"C:\Program Files\1cv8\8.3.27.1508\bin\1cv8.exe"
    if not os.path.exists(exe):
        # Search
        for path in pathlib.Path(r"C:\Program Files\1cv8").rglob("1cv8.exe"):
            exe = str(path)
            break

print(f"1cv8.exe: {exe}")

# Dump config to temp folder
dump_dir = pathlib.Path(r"D:\Git\Public_Trade_Module\_dump_current")
dump_dir.mkdir(exist_ok=True)

ib_path = r"D:\Confiq\Public Trade Module"
log_path = r"D:\Git\Public_Trade_Module\Документация\Валидация\logs\dump-test.log"

cmd = [
    exe, "DESIGNER",
    "/F", ib_path,
    "/N", "Admin", 
    "/DumpConfigToFiles", str(dump_dir),
    "/DisableStartupDialogs",
    "/DisableStartupMessages",
    "/Out", log_path
]

print(f"Running: {' '.join(cmd[:5])}...")
result = subprocess.run(cmd, timeout=300)
print(f"Exit code: {result.returncode}")

# Read log
log = pathlib.Path(log_path)
if log.exists():
    content = log.read_text(encoding='utf-8-sig').strip()
    print(f"Log: {content[:500] if content else '[EMPTY - OK]'}")
