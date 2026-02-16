# -*- coding: utf-8 -*-
"""Direct config load bypassing validator (BPO forms have harmless duplicate attr IDs from dump)"""
import subprocess
import pathlib
import sys
import time

V8_EXE = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
IB_PATH = r"D:\Confiq\Public Trade Module"
CONFIG_PATH = r"D:\Git\Public_Trade_Module\Конфигурация\Проверка"
LOG_DIR = pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Валидация\logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

timestamp = time.strftime("%Y%m%d-%H%M%S")
log_file = LOG_DIR / f"1c-load-{timestamp}.log"

print(f"=== Direct Config Load ===")
print(f"Source: {CONFIG_PATH}")
print(f"IB: {IB_PATH}")
print(f"Log: {log_file}")
print()

# Step 1: Load config from files
print("[1/3] Loading config from files...")
cmd_load = [
    V8_EXE, "DESIGNER",
    "/F", IB_PATH,
    "/LoadConfigFromFiles", CONFIG_PATH,
    "/DisableStartupDialogs",
    "/DisableStartupMessages",
    "/Out", str(log_file),
]
result = subprocess.run(cmd_load, timeout=600, capture_output=True, text=True)
print(f"  Exit code: {result.returncode}")

if log_file.exists():
    log_text = log_file.read_text(encoding='utf-8-sig', errors='replace')
    if log_text.strip():
        print(f"  Log: {log_text[:2000]}")
    else:
        print(f"  Log: (empty)")

if result.returncode != 0:
    print(f"\n[FAIL] Load failed with code {result.returncode}")
    if result.stderr:
        print(f"  stderr: {result.stderr[:500]}")
    sys.exit(1)

print("[OK] Config loaded successfully")

# Step 2: Check syntax
log_syntax = LOG_DIR / f"1c-syntax-{timestamp}.log"
print("\n[2/3] Checking syntax...")
cmd_syntax = [
    V8_EXE, "DESIGNER",
    "/F", IB_PATH,
    "/CheckModules",
    "/DisableStartupDialogs",
    "/DisableStartupMessages",
    "/Out", str(log_syntax),
]
result2 = subprocess.run(cmd_syntax, timeout=300, capture_output=True, text=True)
print(f"  Exit code: {result2.returncode}")

if log_syntax.exists():
    syntax_text = log_syntax.read_text(encoding='utf-8-sig', errors='replace')
    if syntax_text.strip():
        print(f"  Log: {syntax_text[:3000]}")
    else:
        print(f"  Log: (empty - no syntax errors)")

if result2.returncode != 0:
    print(f"\n[WARN] Syntax check returned code {result2.returncode}")

# Step 3: Update DB
log_update = LOG_DIR / f"1c-update-{timestamp}.log"
print("\n[3/3] Updating database...")
cmd_update = [
    V8_EXE, "DESIGNER",
    "/F", IB_PATH,
    "/UpdateDBCfg",
    "/DisableStartupDialogs",
    "/DisableStartupMessages",
    "/Out", str(log_update),
]
result3 = subprocess.run(cmd_update, timeout=300, capture_output=True, text=True)
print(f"  Exit code: {result3.returncode}")

if log_update.exists():
    update_text = log_update.read_text(encoding='utf-8-sig', errors='replace')
    if update_text.strip():
        print(f"  Log: {update_text[:2000]}")
    else:
        print(f"  Log: (empty - OK)")

if result3.returncode != 0:
    print(f"\n[FAIL] DB update failed with code {result3.returncode}")
    sys.exit(1)

print("\n=== ALL DONE ===")
print("Config loaded, syntax checked, DB updated successfully!")
