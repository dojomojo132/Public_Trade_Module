# -*- coding: utf-8 -*-
"""Run UpdateDBCfg without user"""
import subprocess
import pathlib

exe = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
ib_path = r"D:\Confiq\Public Trade Module"
log_path = r"D:\Git\Public_Trade_Module\Документация\Валидация\logs\update-db.log"

cmd = [
    exe, "DESIGNER",
    "/F", ib_path,
    "/UpdateDBCfg",
    "/DisableStartupDialogs",
    "/DisableStartupMessages",
    "/Out", log_path
]

print("Running UpdateDBCfg...")
result = subprocess.run(cmd, timeout=300)
print(f"Exit code: {result.returncode}")

log = pathlib.Path(log_path)
if log.exists():
    content = log.read_text(encoding='utf-8-sig').strip()
    print(f"Log: {content[:500] if content else '[EMPTY - SUCCESS]'}")
