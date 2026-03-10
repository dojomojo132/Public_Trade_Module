# -*- coding: utf-8 -*-
"""Restore ИБ from .dt backup"""
import subprocess
import pathlib
import os
import time

exe = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
ib_path = r"D:\Confiq\Public Trade Module"
backup_dir = pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Валидация\backups")
log_path = r"D:\Git\Public_Trade_Module\logs\restore.log"

# Find latest backup
backups = sorted(backup_dir.glob("PTM-backup-*.dt"), key=lambda f: f.stat().st_mtime, reverse=True)
if not backups:
    print("No backups found!")
    exit(1)

latest = backups[0]
print(f"1. Restoring from: {latest.name} ({latest.stat().st_size // 1024} KB)")

# Kill any 1cv8 processes first
print("2. Killing 1cv8.exe...")
subprocess.run(["taskkill", "/F", "/IM", "1cv8.exe"], capture_output=True)
time.sleep(2)

# Restore
print("3. RestoreIB...")
cmd = [
    exe, "DESIGNER",
    "/F", ib_path,
    "/N", "Admin",
    "/RestoreIB", str(latest),
    "/DisableStartupDialogs",
    "/DisableStartupMessages",
    "/Out", log_path
]
result = subprocess.run(cmd, timeout=300)
log_text = ""
if pathlib.Path(log_path).exists():
    log_text = pathlib.Path(log_path).read_text(encoding='utf-8-sig').strip()
print(f"  Exit code: {result.returncode}")
print(f"  Log: {log_text[:1000] if log_text else '[EMPTY]'}")

if result.returncode == 0:
    print("\n✓ ИБ восстановлена!")
else:
    print("\n✗ Восстановление не удалось")

print("\nDone!")
