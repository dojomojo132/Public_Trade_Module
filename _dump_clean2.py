# -*- coding: utf-8 -*-
"""Kill 1cv8.exe designers and dump config"""
import subprocess
import pathlib
import shutil
import os
import time

exe = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
ib_path = r"D:\Confiq\Public Trade Module"
dump_path = r"D:\Git\Public_Trade_Module\_dump_clean"
log_path = r"D:\Git\Public_Trade_Module\logs\dump-clean.log"

# Step 1: Kill all 1cv8.exe processes
print("1. Killing 1cv8.exe processes...")
result = subprocess.run(["taskkill", "/F", "/IM", "1cv8.exe"], capture_output=True, text=True)
print(f"  {result.stdout.strip()}")
time.sleep(3)

# Step 2: Clean dump folder
print("2. Cleaning dump folder...")
if os.path.exists(dump_path):
    shutil.rmtree(dump_path)
os.makedirs(dump_path, exist_ok=True)

# Step 3: Dump
print("3. DumpConfigToFiles...")
cmd = [
    exe, "DESIGNER",
    "/F", ib_path,
    "/N", "Admin",
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
    cdi = pathlib.Path(dump_path) / "ConfigDumpInfo.xml"
    if cdi.exists():
        text = cdi.read_text(encoding='utf-8-sig')
        for line in text.split('\n'):
            if 'Номенклатура' in line:
                print(f"  CDI: {line.strip()}")
    
    fg_xml = pathlib.Path(dump_path) / "Catalogs" / "Номенклатура" / "Forms" / "ФормаГруппы.xml"
    if fg_xml.exists():
        text = fg_xml.read_text(encoding='utf-8-sig')
        print(f"  ФормаГруппы.xml: {text[:300]}")
    else:
        print("  ФормаГруппы.xml NOT FOUND in dump")
    
    nom_xml = pathlib.Path(dump_path) / "Catalogs" / "Номенклатура.xml"
    if nom_xml.exists():
        text = nom_xml.read_text(encoding='utf-8-sig')
        for line in text.split('\n'):
            if 'DefaultFolderForm' in line or 'ФормаГруппы' in line:
                print(f"  Nom: {line.strip()}")

print("\nDone!")
