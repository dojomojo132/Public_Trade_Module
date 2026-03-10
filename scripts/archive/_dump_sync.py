# -*- coding: utf-8 -*-
"""Dump config from ИБ для получения актуальных UUID"""
import subprocess
import pathlib
import shutil
import os

exe = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
ib_path = r"D:\Confiq\Public Trade Module"
dump_path = r"D:\Git\Public_Trade_Module\_dump_current_sync"
log_dir = r"D:\Git\Public_Trade_Module\Документация\Валидация\logs"

# DumpConfigToFiles
print("DumpConfigToFiles...")
if os.path.exists(dump_path):
    shutil.rmtree(dump_path)
os.makedirs(dump_path)

log1 = os.path.join(log_dir, "dump-sync.log")
cmd1 = [
    exe, "DESIGNER",
    "/F", ib_path,
    "/N", "Admin",
    "/DumpConfigToFiles", dump_path,
    "/DisableStartupDialogs",
    "/DisableStartupMessages",
    "/Out", log1
]
result = subprocess.run(cmd1, timeout=300)
log1_text = pathlib.Path(log1).read_text(encoding='utf-8-sig').strip() if pathlib.Path(log1).exists() else "[NO LOG]"
print(f"  Exit code: {result.returncode}")
if log1_text:
    print(f"  Log: {log1_text[:500]}")

if result.returncode == 0:
    # Read key files
    cdi = pathlib.Path(dump_path) / "ConfigDumpInfo.xml"
    if cdi.exists():
        text = cdi.read_text(encoding='utf-8-sig')
        # Find ФормаГруппы entries
        for line in text.split('\n'):
            if 'ФормаГруппы' in line or 'Номенклатура"' in line:
                print(f"  CDI: {line.strip()}")
    
    # Check Номенклатура.xml for DefaultFolderForm
    nom = pathlib.Path(dump_path) / "Catalogs" / "Номенклатура.xml"
    if nom.exists():
        text = nom.read_text(encoding='utf-8-sig')
        for line in text.split('\n'):
            if 'DefaultFolderForm' in line or 'ФормаГруппы' in line:
                print(f"  Nom: {line.strip()}")
    
    # Check ФормаГруппы descriptor
    fg = pathlib.Path(dump_path) / "Catalogs" / "Номенклатура" / "Forms" / "ФормаГруппы.xml"
    if fg.exists():
        text = fg.read_text(encoding='utf-8-sig')
        for line in text.split('\n'):
            if 'uuid' in line.lower() or 'Name' in line:
                print(f"  FG: {line.strip()}")
    else:
        print("  ФормаГруппы.xml NOT FOUND in dump")
else:
    print("  DUMP FAILED!")
    print(f"  Full log: {log1_text}")

print("\nDone!")
