# -*- coding: utf-8 -*-
"""
Fix CDI configVersions and reload.
The key insight: when we modify Номенклатура.xml, we must also change its 
configVersion in CDI so 1C knows to reload it.
"""
import os
import pathlib
import subprocess
import sys
import re

exe = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
ib_path = r"D:\Confiq\Public Trade Module"
dump_dir = r"D:\Git\Public_Trade_Module\Конфигурация\_DumpVerify"
log_dir = r"D:\Git\Public_Trade_Module\Документация\Валидация\logs"

def run_1c(args, log_name, desc):
    log_file = os.path.join(log_dir, log_name)
    cmd = [exe, "DESIGNER", "/F", ib_path] + args + [
        "/DisableStartupDialogs", "/DisableStartupMessages", "/Out", log_file
    ]
    print(f"\n{'='*60}")
    print(f"  {desc}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, timeout=300)
    log_text = ""
    if pathlib.Path(log_file).exists():
        log_text = pathlib.Path(log_file).read_text(encoding='utf-8-sig').strip()
    print(f"  Exit: {result.returncode}")
    if log_text:
        print(f"  Log: {log_text[:500]}")
    else:
        print(f"  Log: [empty - OK]")
    return result.returncode == 0, log_text

# Fix the CDI in dump
dump_cdi = os.path.join(dump_dir, "ConfigDumpInfo.xml")
cdi_content = pathlib.Path(dump_cdi).read_text(encoding='utf-8-sig')

# Change Catalog.Номенклатура configVersion to force reload
# Original: aa3c09fdda956d4599e92d82f097502f00000000
# New: aa3c09fdda956d4599e92d82f097502e00000000 (changed last digit before zeros)
old_cv = 'aa3c09fdda956d4599e92d82f097502f00000000'
new_cv = 'aa3c09fdda956d4599e92d82f097502e00000000'
if old_cv in cdi_content:
    cdi_content = cdi_content.replace(old_cv, new_cv)
    print(f"Updated Catalog.Номенклатура configVersion")

# Fix ФормаГруппы configVersions (proper format ending with 00000000)
cdi_content = cdi_content.replace(
    '00000000000000000000000000000000FFFFFFFF',
    'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d600000000'
)
print(f"Fixed ФормаГруппы configVersions")

pathlib.Path(dump_cdi).write_text(cdi_content, encoding='utf-8-sig')

# Show relevant CDI section
print("\nCDI Номенклатура entries:")
for line in cdi_content.split('\n'):
    if 'Номенклатура' in line and ('Form' in line or 'configVersion' in line or 'ObjectModule' in line):
        print(f"  {line.strip()}")

# Load from dump
ok, log = run_1c(["/LoadConfigFromFiles", dump_dir], "load-fixed-cv.log", "Load with fixed configVersions")
if not ok:
    print(f"\nStill FAILED! Let me try one more thing...")
    
    # Maybe the issue is that we didn't also need to update Номенклатура configVersion 
    # when it was already modified. Let me check if DefaultFolderForm was added:
    nom_xml = os.path.join(dump_dir, "Catalogs", "Номенклатура.xml")
    nom_c = pathlib.Path(nom_xml).read_text(encoding='utf-8-sig')
    if "DefaultFolderForm" in nom_c:
        print("  DefaultFolderForm IS present in Номенклатура.xml")
    else:
        print("  DefaultFolderForm is NOT present!")
    
    # Check formfile  
    fg = os.path.join(dump_dir, "Catalogs", "Номенклатура", "Forms", "ФормаГруппы.xml")
    if os.path.exists(fg):
        fg_c = pathlib.Path(fg).read_text(encoding='utf-8-sig')
        print(f"  ФормаГруппы.xml exists ({len(fg_c)} chars)")
        print(f"  First 200: {fg_c[:200]}")
    
    # Try without DefaultFolderForm
    print("\n  Trying WITHOUT DefaultFolderForm...")
    nom_c2 = re.sub(r'\s*<DefaultFolderForm>[^<]+</DefaultFolderForm>', '', nom_c)
    pathlib.Path(nom_xml).write_text(nom_c2, encoding='utf-8-sig')
    
    # Also restore original configVersion for Номенклатура
    cdi2 = pathlib.Path(dump_cdi).read_text(encoding='utf-8-sig')
    cdi2 = cdi2.replace(new_cv, old_cv)
    pathlib.Path(dump_cdi).write_text(cdi2, encoding='utf-8-sig')
    
    ok2, log2 = run_1c(["/LoadConfigFromFiles", dump_dir], "load-no-dff.log", "Load without DefaultFolderForm")
    if ok2:
        print("\n  SUCCESS without DefaultFolderForm!")
        ok3, _ = run_1c(["/UpdateDBCfg"], "update-no-dff.log", "UpdateDBCfg")
    else:
        print(f"\n  Still failed: {log2}")
        
        # Last resort: try without ANY CDI changes for new form
        print("\n  Trying without CDI entries for ФормаГруппы...")
        cdi3 = pathlib.Path(dump_cdi).read_text(encoding='utf-8-sig')
        cdi3 = re.sub(r'\s*<Metadata name="Catalog\.Номенклатура\.Form\.ФормаГруппы"[^/]*/>', '', cdi3)
        cdi3 = re.sub(r'\s*<Metadata name="Catalog\.Номенклатура\.Form\.ФормаГруппы\.Form"[^/]*/>', '', cdi3)
        pathlib.Path(dump_cdi).write_text(cdi3, encoding='utf-8-sig')
        
        ok4, log4 = run_1c(["/LoadConfigFromFiles", dump_dir], "load-no-cdi.log", "Load without CDI entries")
        if ok4:
            print("\n  SUCCESS without CDI entries!")
        else:
            print(f"\n  Still failed: {log4}")
