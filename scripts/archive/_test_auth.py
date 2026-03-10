# -*- coding: utf-8 -*-
"""Direct 1C deploy bypassing PowerShell encoding issues"""
import subprocess
import pathlib
import sys

IB_PATH = r"D:\Confiq\Public Trade Module"
CONFIG_PATH = r"D:\Git\Public_Trade_Module\Конфигурация\Проверка"
BACKUP_PATH = r"D:\Git\Public_Trade_Module\Документация\Валидация\backups\manual-backup.dt"
LOG_PATH = r"D:\Git\Public_Trade_Module\logs\manual-deploy.log"

# Try to find 1cv8.exe
v8_path = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"

# Credentials to try
credentials = [
    ("Админ", ""),
    ("Админ", "Админ"),
    ("Admin", ""),
    ("Admin", "Админ"),
    ("Admin", "Admin"),
    ("", ""),
]

print("=== Testing 1C connection ===")
for user, pwd in credentials:
    args = [v8_path, "DESIGNER", "/F", IB_PATH]
    if user:
        args += ["/N", user]
    if pwd:
        args += ["/P", pwd]
    args += ["/DumpIB", BACKUP_PATH,
             "/DisableStartupDialogs", "/DisableStartupMessages",
             "/Out", LOG_PATH]
    
    cred_str = f"User='{user}' Pass='{pwd}'" if user else "No credentials"
    print(f"\nTrying: {cred_str}")
    print(f"  Command: 1cv8.exe DESIGNER /F \"{IB_PATH}\" {'/N \"'+user+'\"' if user else ''} {'/P \"'+pwd+'\"' if pwd else ''} /DumpIB ...")
    
    result = subprocess.run(args, timeout=60, capture_output=True, text=True)
    
    # Read log
    log_file = pathlib.Path(LOG_PATH)
    log_content = log_file.read_text(encoding="utf-8-sig") if log_file.exists() else "(no log)"
    
    print(f"  Exit code: {result.returncode}")
    print(f"  Log: {log_content.strip()}")
    
    if result.returncode == 0:
        print(f"\n=== SUCCESS with: {cred_str} ===")
        # Clean up backup
        backup = pathlib.Path(BACKUP_PATH)
        if backup.exists():
            backup.unlink()
        sys.exit(0)

print("\n=== All credential combinations failed ===")
sys.exit(1)
