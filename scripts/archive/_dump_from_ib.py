# -*- coding: utf-8 -*-
import subprocess
import pathlib
import shutil
import time

exe = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
ib = r"D:\Confiq\Public Trade Module"
dump_dir = pathlib.Path(r"D:\Git\Public_Trade_Module\_dump_from_ib")
log = pathlib.Path(r"D:\Git\Public_Trade_Module\logs\dump-from-ib.log")

# Clean dump dir
if dump_dir.exists():
    shutil.rmtree(dump_dir)
dump_dir.mkdir(parents=True)
print(f"Dump dir: {dump_dir}")

cmd = f'"{exe}" DESIGNER /F "{ib}" /N "Admin" /DumpConfigToFiles "{dump_dir}" /DisableStartupDialogs /DisableStartupMessages /Out "{log}"'
print(f"Running DumpConfigToFiles...")
start = time.time()

result = subprocess.run(cmd, shell=True, capture_output=True, timeout=300)
elapsed = time.time() - start
print(f"Exit code: {result.returncode} ({elapsed:.1f} sec)")

if log.exists():
    content = log.read_text(encoding="utf-8-sig")
    print(f"Log: {content.strip()}")

# Count files
files = list(dump_dir.rglob("*"))
file_count = sum(1 for f in files if f.is_file())
dir_count = sum(1 for f in files if f.is_dir())
print(f"Dumped: {file_count} files in {dir_count} directories")
