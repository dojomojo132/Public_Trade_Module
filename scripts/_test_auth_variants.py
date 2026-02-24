# -*- coding: utf-8 -*-
"""Проверяем варианты авторизации в ИБ"""
import subprocess
import pathlib
import os
import time

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

# Варианты: (описание, доп_аргументы)
variants = [
    ("no /U at all",          []),
    ("empty /U",              ["/U", ""]),
    ("Admin Latin",           ["/U", "Admin"]),
    ("Administrator Latin",   ["/U", "Administrator"]),
]

for desc, u_args in variants:
    logfile = os.path.join(log_base, f"_auth_{desc.replace(' ', '_')}.log")
    dtfile  = os.path.join(log_base, f"_auth_test.dt")
    cmd = [exe, "DESIGNER", "/F", ib] + u_args + [
        "/DumpIB", dtfile,
        "/DisableStartupDialogs",
        "/DisableStartupMessages",
        "/Out", logfile
    ]
    print(f"\n[{desc}]")
    print("CMD:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, timeout=60)
    print(f"Exit: {result.returncode}")
    print(f"Log: {read_log(logfile)}")

print("\nDone.")
