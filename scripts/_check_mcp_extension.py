# -*- coding: utf-8 -*-
"""Проверка расширения: выгрузка + проверка."""
import subprocess
import pathlib
import sys
import os

exe = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
ib = r"D:\Confiq\Public Trade Module"
dump = r"D:\Git\Public_Trade_Module\MCP_Extension_check"
log = r"D:\Git\Public_Trade_Module\logs\_check_ext.log"

os.makedirs(dump, exist_ok=True)
os.makedirs(os.path.dirname(log), exist_ok=True)

# Выгрузить расширение (проверка что оно на месте)
args = [exe, "DESIGNER", "/F", ib, "/N", "Админ",
        "/DumpConfigToFiles", dump,
        "-Extension", "MCP_Сервер",
        "/DisableStartupDialogs", "/DisableStartupMessages",
        "/Out", log]

print("Проверка расширения MCP_Сервер...")
r = subprocess.run(args, capture_output=True, timeout=60)
print(f"Exit code: {r.returncode}")

lp = pathlib.Path(log)
if lp.exists():
    for enc in ['utf-8-sig', 'utf-8', 'cp1251']:
        try:
            content = lp.read_text(encoding=enc).strip()
            if content:
                print(f"Log: {content}")
                break
        except:
            continue

# Показать файлы
dp = pathlib.Path(dump)
if dp.exists():
    files = sorted([f for f in dp.rglob("*") if f.is_file()])
    print(f"\nФайлов в расширении: {len(files)}")
    for f in files:
        print(f"  {f.relative_to(dp)}")

# Проверить CheckConfig для расширения
log2 = r"D:\Git\Public_Trade_Module\logs\_check_ext_syntax.log"
args2 = [exe, "DESIGNER", "/F", ib, "/N", "Админ",
         "/CheckConfig",
         "-Extension", "MCP_Сервер",
         "/DisableStartupDialogs", "/DisableStartupMessages",
         "/Out", log2]

print("\n\nПроверка синтаксиса расширения...")
r2 = subprocess.run(args2, capture_output=True, timeout=120)
print(f"Exit code: {r2.returncode}")

lp2 = pathlib.Path(log2)
if lp2.exists():
    for enc in ['utf-8-sig', 'utf-8', 'cp1251']:
        try:
            content = lp2.read_text(encoding=enc).strip()
            if content:
                print(f"Log:\n{content}")
                break
        except:
            continue
    if not content or not content.strip():
        print("Log: (пусто - ошибок нет)")
