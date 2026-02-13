# -*- coding: utf-8 -*-
"""Recreate ИБ and load config from clean commit"""
import subprocess
import pathlib
import shutil

IB_PATH = pathlib.Path(r"D:\Confiq\Public Trade Module")
BIN_1C = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
PROVERKA = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка")
LOG = pathlib.Path(r"D:\Git\Public_Trade_Module\_ib_log.txt")

# Step 1: Delete existing ИБ files
print("=== STEP 1: Delete ИБ files ===")
for f in IB_PATH.glob("*"):
    if f.is_file():
        try:
            f.unlink()
            print(f"  Deleted: {f.name}")
        except Exception as e:
            print(f"  ERROR deleting {f.name}: {e}")
    elif f.is_dir():
        try:
            shutil.rmtree(f)
            print(f"  Deleted dir: {f.name}/")
        except Exception as e:
            print(f"  ERROR deleting {f.name}/: {e}")

# Step 2: Create fresh empty ИБ
print("\n=== STEP 2: Create fresh ИБ ===")
cmd = f'"{BIN_1C}" CREATEINFOBASE File="{IB_PATH}"; /DisableStartupDialogs /DisableStartupMessages /Out "{LOG}"'
print(f"  CMD: {cmd}")
r = subprocess.run(cmd, capture_output=True, shell=True, timeout=120)
print(f"  Exit code: {r.returncode}")
if LOG.exists():
    print(f"  Log: {LOG.read_text(encoding='utf-8').strip()}")

# Step 3: Load config from Проверка (clean commit)
print("\n=== STEP 3: Load config from Проверка ===")
r = subprocess.run([
    BIN_1C, "DESIGNER",
    "/F", str(IB_PATH),
    "/LoadConfigFromFiles", str(PROVERKA),
    "/DisableStartupDialogs", "/DisableStartupMessages",
    "/Out", str(LOG)
], capture_output=True, timeout=300)
print(f"  Exit code: {r.returncode}")
if LOG.exists():
    log_content = LOG.read_text(encoding='utf-8').strip()
    print(f"  Log: {log_content}")
    if r.returncode == 0 or "успешно" in log_content.lower():
        print("\n  *** CONFIG LOADED SUCCESSFULLY! ***")
    else:
        print("\n  *** CONFIG LOAD FAILED ***")

# Step 4: Update DB if load was successful
if r.returncode == 0:
    print("\n=== STEP 4: Update DB ===")
    r2 = subprocess.run([
        BIN_1C, "DESIGNER",
        "/F", str(IB_PATH),
        "/UpdateDBCfg",
        "/DisableStartupDialogs", "/DisableStartupMessages",
        "/Out", str(LOG)
    ], capture_output=True, timeout=300)
    print(f"  Exit code: {r2.returncode}")
    if LOG.exists():
        print(f"  Log: {LOG.read_text(encoding='utf-8').strip()}")
