# -*- coding: utf-8 -*-
"""Ещё варианты - кириллические имена через bat"""
import subprocess
import pathlib
import os
import tempfile

exe = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
ib = r"D:\Confiq\Public Trade Module"
log_base = r"D:\Git\Public_Trade_Module\logs"
os.makedirs(log_base, exist_ok=True)

def read_log(logfile):
    lp = pathlib.Path(logfile)
    if not lp.exists():
        return "(no log)"
    raw = lp.read_bytes()
    for enc in ['utf-8-sig', 'utf-8', 'cp1251']:
        try:
            return raw.decode(enc).strip()[:300]
        except Exception:
            continue
    return "(decode error)"

# Кириллические имена - нужно через bat файл в cp1251
cyrillic_users = [
    "Администратор",
    "Администр",
    "Пользователь",
    "admin",
]

for user in cyrillic_users:
    logfile = os.path.join(log_base, f"_auth_bat_{len(user)}.log")
    dtfile  = os.path.join(log_base, f"_auth_test2.dt")
    
    bat_path = os.path.join(log_base, "_tmp_check.bat")
    bat_content = f'@echo off\r\n"{exe}" DESIGNER /F "{ib}" /U "{user}" /DumpIB "{dtfile}" /DisableStartupDialogs /DisableStartupMessages /Out "{logfile}"\r\n'
    
    with open(bat_path, 'w', encoding='cp1251') as f:
        f.write(bat_content)
    
    print(f"\n[user='{user}']")
    result = subprocess.run(["cmd", "/c", bat_path], capture_output=True, timeout=60)
    print(f"Exit: {result.returncode}")
    print(f"Log: {read_log(logfile)}")

print("\nDone.")
