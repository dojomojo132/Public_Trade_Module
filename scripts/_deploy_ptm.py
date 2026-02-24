# -*- coding: utf-8 -*-
"""Deploy PTM config via Python (bypasses PowerShell Cyrillic encoding)"""
import subprocess
import pathlib
import sys
import datetime

IB_PATH = r"D:\Confiq\Public Trade Module"
CONFIG_PATH = r"D:\Git\Public_Trade_Module\Конфигурация\Проверка"
LOGS_DIR = pathlib.Path(r"D:\Git\Public_Trade_Module\logs")
BACKUPS_DIR = pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Валидация\backups")
V8 = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
USER = "Админ"
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

LOGS_DIR.mkdir(exist_ok=True)
BACKUPS_DIR.mkdir(parents=True, exist_ok=True)

def run_1c(action_name, extra_args, timeout=300):
    log_file = LOGS_DIR / f"deploy-{action_name}-{TIMESTAMP}.log"
    args = [V8, "DESIGNER", "/F", IB_PATH, "/N", USER]
    args += extra_args
    args += ["/DisableStartupDialogs", "/DisableStartupMessages", "/Out", str(log_file)]
    
    print(f"\n[{action_name}] Running...")
    result = subprocess.run(args, timeout=timeout, capture_output=True, text=True)
    
    log_content = ""
    if log_file.exists():
        log_content = log_file.read_text(encoding="utf-8-sig").strip()
    
    print(f"[{action_name}] Exit code: {result.returncode}")
    if log_content:
        for line in log_content.split("\n")[:50]:
            print(f"  {line}")
    
    return result.returncode, log_content

print("=" * 60)
print(f"PTM Deploy via Python - {TIMESTAMP}")
print("=" * 60)

# Step 1: Backup
backup_path = BACKUPS_DIR / f"PTM-backup-{TIMESTAMP}.dt"
code, log = run_1c("backup", ["/DumpIB", str(backup_path)], timeout=180)
if code != 0:
    print(f"\nFAIL: Backup failed! Aborting.")
    sys.exit(1)
print(f"Backup OK: {backup_path.name}")

# Step 2: Load config from files
code, log = run_1c("loadconfig", ["/LoadConfigFromFiles", CONFIG_PATH], timeout=300)
if code != 0:
    print(f"\nFAIL: LoadConfig failed!")
    sys.exit(2)
print("LoadConfig OK")

# Step 3: Syntax check
code, log = run_1c("checkconfig", ["/CheckConfig", "-ThinClient", "-Server", "-ExternalConnection", "-ThickClientOrdinaryApplication"], timeout=180)
print(f"CheckConfig done (code={code})")

# Step 4: Update DB
code, log = run_1c("updatedb", ["/UpdateDBCfg", "-Dynamic-"], timeout=300)
if code != 0:
    print(f"\nFAIL: UpdateDBCfg failed!")
    sys.exit(4)
print("UpdateDBCfg OK")

print("\n" + "=" * 60)
print("DEPLOY SUCCESSFUL!")
print("=" * 60)

# Step 5: Open Designer
print("\nOpening Designer...")
subprocess.Popen([V8, "DESIGNER", "/F", IB_PATH, "/N", USER])
print("Designer launched.")
