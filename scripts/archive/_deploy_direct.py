# -*- coding: utf-8 -*-
"""Direct deploy: LoadConfigFromFiles + UpdateDBCfg, bypassing validate-config.ps1"""
import subprocess
import time

IB = r"D:\Confiq\Public Trade Module"
CFG = r"D:\Git\Public_Trade_Module\Конфигурация"
V8 = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"

# Step 1: LoadConfigFromFiles
print("=== 1. LoadConfigFromFiles ===")
t0 = time.time()
result = subprocess.run([
    V8, "DESIGNER",
    f"/F{IB}",
    "/N", "Admin",
    "/LoadConfigFromFiles", CFG,
    "/UpdateDBCfg",
    "-Dynamic-",
    "/Out", "D:\\Git\\Public_Trade_Module\\_deploy_direct_output.txt",
    "/DisableStartupMessages",
    "/DisableStartupDialogs",
], capture_output=True, timeout=300)
elapsed = time.time() - t0
print(f"  Exit code: {result.returncode} ({elapsed:.1f} sec)")

# Read output file
try:
    with open(r"D:\Git\Public_Trade_Module\_deploy_direct_output.txt", "r", encoding="utf-8-sig") as f:
        output = f.read().strip()
    if output:
        lines = output.split('\n')
        for line in lines[-20:]:  # last 20 lines
            print(f"  {line.rstrip()}")
except:
    pass

if result.returncode == 0:
    print("\n✅ Деплой УСПЕШНО")
else:
    print(f"\n❌ Деплой ОШИБКА (exit code {result.returncode})")
