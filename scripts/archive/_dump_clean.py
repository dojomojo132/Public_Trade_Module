# -*- coding: utf-8 -*-
"""Dump config from ИБ к новой чистой папке (без привязки к ConfigDumpInfo)"""
import subprocess
import pathlib
import shutil
import os

exe = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
ib_path = r"D:\Confiq\Public Trade Module"
dump_path = r"D:\Git\Public_Trade_Module\_dump_clean"
log_path = r"D:\Git\Public_Trade_Module\logs\dump-clean.log"

print("1. Cleaning dump folder...")
if os.path.exists(dump_path):
    shutil.rmtree(dump_path)
os.makedirs(dump_path, exist_ok=True)

print("2. DumpConfigToFiles (no User param, default)...")
cmd = [
    exe, "DESIGNER",
    "/F", ib_path,
    "/DumpConfigToFiles", dump_path,
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
    # Check key files
    cdi = pathlib.Path(dump_path) / "ConfigDumpInfo.xml"
    if cdi.exists():
        text = cdi.read_text(encoding='utf-8-sig')
        for line in text.split('\n'):
            if 'Номенклатура' in line:
                print(f"  CDI: {line.strip()}")
    
    fg_xml = pathlib.Path(dump_path) / "Catalogs" / "Номенклатура" / "Forms" / "ФормаГруппы.xml"
    if fg_xml.exists():
        print(f"  ФормаГруппы.xml EXISTS: {fg_xml.read_text(encoding='utf-8-sig')[:200]}")
    else:
        print(f"  ФормаГруппы.xml NOT FOUND")

print("\nDone!")
