# -*- coding: utf-8 -*-
"""Load config into fresh ИБ and update DB"""
import subprocess
import pathlib

IB_PATH = pathlib.Path(r"D:\Confiq\Public Trade Module")
BIN_1C = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
PROVERKA = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка")
LOG = pathlib.Path(r"D:\Git\Public_Trade_Module\_ib_log.txt")

# Step 1: Load config
print("=== Load config ===")
cmd = f'"{BIN_1C}" DESIGNER /F "{IB_PATH}" /LoadConfigFromFiles "{PROVERKA}" /DisableStartupDialogs /DisableStartupMessages /Out "{LOG}"'
r = subprocess.run(cmd, capture_output=True, shell=True, timeout=300)
print(f"  Exit code: {r.returncode}")
if LOG.exists():
    log = LOG.read_text(encoding='utf-8').strip()
    print(f"  Log: {log}")
    if r.returncode != 0:
        print("\n  *** LOAD FAILED ***")
        exit(1)

# Step 2: Update DB
print("\n=== Update DB ===")
cmd2 = f'"{BIN_1C}" DESIGNER /F "{IB_PATH}" /UpdateDBCfg /DisableStartupDialogs /DisableStartupMessages /Out "{LOG}"'
r2 = subprocess.run(cmd2, capture_output=True, shell=True, timeout=300)
print(f"  Exit code: {r2.returncode}")
if LOG.exists():
    print(f"  Log: {LOG.read_text(encoding='utf-8').strip()}")

# Step 3: Check config
print("\n=== Check config (syntax) ===")
cmd3 = f'"{BIN_1C}" DESIGNER /F "{IB_PATH}" /CheckConfig -ThinClient -WebClient -Server -ExternalConnection -ThickClientOrdinaryApplication -ExternalConnectionServer /DisableStartupDialogs /DisableStartupMessages /Out "{LOG}"'
r3 = subprocess.run(cmd3, capture_output=True, shell=True, timeout=300)
print(f"  Exit code: {r3.returncode}")
if LOG.exists():
    print(f"  Log: {LOG.read_text(encoding='utf-8').strip()}")

if r.returncode == 0 and r2.returncode == 0:
    print("\n*** ALL DONE SUCCESSFULLY! ***")
else:
    print("\n*** SOME STEPS FAILED ***")
