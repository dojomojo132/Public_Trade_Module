# -*- coding: utf-8 -*-
"""Run UpdateDBCfg for PTM InfoBase after LoadConfigFromFiles."""
import subprocess
import sys
import pathlib

cmd = [
    "1cv8.exe", "DESIGNER",
    "/F", r"D:\Confiq\Public Trade Module",
    "/N", "Admin",
    "/UpdateDBCfg",
    "/DisableStartupDialogs",
    "/DisableStartupMessages",
    "/Out", r"D:\Git\Public_Trade_Module\Документация\Валидация\logs\updatedb_manual.log"
]

print(f"Running: {' '.join(cmd)}")
result = subprocess.run(cmd, capture_output=True, timeout=180)
print(f"Exit code: {result.returncode}")

log = pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Валидация\logs\updatedb_manual.log")
if log.exists():
    content = log.read_text(encoding="utf-8-sig")
    if content.strip():
        print(f"Log:\n{content}")
    else:
        print("Log is empty (no errors)")
else:
    print("No log file created")

if result.returncode == 0:
    print("[OK] UpdateDBCfg completed successfully")
else:
    print(f"[FAIL] UpdateDBCfg failed with exit code {result.returncode}")

sys.exit(result.returncode)
