# -*- coding: utf-8 -*-
"""Restore IB from stable 1Cv8.dt in project root"""
import subprocess
import pathlib
import os

exe = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
ib_path = r"D:\Confiq\Public Trade Module"
dt_path = r"D:\Git\Public_Trade_Module\1Cv8.dt"
log_path = r"D:\Git\Public_Trade_Module\Документация\Валидация\logs\restore-stable.log"

if not os.path.exists(dt_path):
    print(f"STABLE DT NOT FOUND: {dt_path}")
    print(f"Size would help: checking...")
    import sys
    sys.exit(1)

dt_size = os.path.getsize(dt_path) / 1024
print(f"Stable DT: {dt_path} ({dt_size:.0f} KB)")

cmd = [
    exe, "DESIGNER",
    "/F", ib_path,
    "/N", "Admin",
    "/RestoreIB", dt_path,
    "/DisableStartupDialogs",
    "/DisableStartupMessages",
    "/Out", log_path
]

print(f"Restoring from stable 1Cv8.dt...")
result = subprocess.run(cmd, timeout=600)
print(f"Exit code: {result.returncode}")

log = pathlib.Path(log_path)
if log.exists():
    content = log.read_text(encoding='utf-8-sig').strip()
    print(f"Log: {content[:500] if content else '[EMPTY]'}")
