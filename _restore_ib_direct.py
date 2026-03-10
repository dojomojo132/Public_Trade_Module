# -*- coding: utf-8 -*-
import subprocess
import pathlib
import sys

exe = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
ib = r"D:\Confiq\Public Trade Module"
dt = pathlib.Path(r"D:\Git\Public_Trade_Module") / "Документация" / "Валидация" / "backups" / "PTM-backup-20260226-175821.dt"
log = pathlib.Path(r"D:\Git\Public_Trade_Module\logs\restore-direct.log")

print(f"DT exists: {dt.exists()} ({dt.stat().st_size // 1024 // 1024} MB)")
print(f"1cv8 exists: {pathlib.Path(exe).exists()}")

args = [
    exe, "DESIGNER",
    f'/F "{ib}"',
    '/N "Admin"',
    f'/RestoreIB "{dt}"',
    "/DisableStartupDialogs",
    "/DisableStartupMessages",
    f'/Out "{log}"'
]

cmd = f'"{exe}" DESIGNER /F "{ib}" /N "Admin" /RestoreIB "{dt}" /DisableStartupDialogs /DisableStartupMessages /Out "{log}"'
print(f"Running: {cmd}")

result = subprocess.run(cmd, shell=True, capture_output=True, timeout=300)
print(f"Exit code: {result.returncode}")

if log.exists():
    content = log.read_text(encoding="utf-8-sig")
    print(f"Log ({log.stat().st_size} bytes):")
    print(content)
else:
    print("No log file created")

if result.stdout:
    print(f"STDOUT: {result.stdout.decode('utf-8', errors='replace')}")
if result.stderr:
    print(f"STDERR: {result.stderr.decode('utf-8', errors='replace')}")
