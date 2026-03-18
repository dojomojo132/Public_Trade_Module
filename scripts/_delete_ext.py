"""Удаление расширения из ИБ"""
import subprocess
import os
import sys

v8 = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
ib = r"D:\Confiq\Public Trade Module"
user = "Админ"
ext_name = sys.argv[1] if len(sys.argv) > 1 else "PTM_Fiscal"
out_file = r"D:\Git\Public_Trade_Module\_ext_delete.txt"

print(f"Удаление расширения '{ext_name}' из ИБ...")

result = subprocess.run([
    v8, "DESIGNER",
    "/F", ib,
    "/N", user,
    "/DisableStartupDialogs",
    "/DisableStartupMessages",
    "/ManageCfgExtensions", "-delete", "-Extension", ext_name,
    "/Out", out_file
], capture_output=True, timeout=180)

print(f"Exit code: {result.returncode}")
if os.path.exists(out_file):
    with open(out_file, "r", encoding="utf-8-sig") as f:
        content = f.read()
        print(content if content.strip() else "(пустой вывод — OK)")
