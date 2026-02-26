# -*- coding: utf-8 -*-
"""Load config with ФормаГруппы and then UpdateDBCfg"""
import subprocess
import pathlib

exe = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
ib_path = r"D:\Confiq\Public Trade Module"
src_path = r"D:\Git\Public_Trade_Module\Конфигурация\Проверка"

# Step 1: LoadConfigFromFiles
log1 = r"D:\Git\Public_Trade_Module\Документация\Валидация\logs\load-with-form.log"
cmd1 = [
    exe, "DESIGNER",
    "/F", ib_path,
    "/LoadConfigFromFiles", src_path,
    "/DisableStartupDialogs",
    "/DisableStartupMessages",
    "/Out", log1
]

print("Step 1: LoadConfigFromFiles...")
result = subprocess.run(cmd1, timeout=300)
log1_content = pathlib.Path(log1).read_text(encoding='utf-8-sig').strip() if pathlib.Path(log1).exists() else "[NO LOG]"
print(f"  Exit code: {result.returncode}")
print(f"  Log: {log1_content[:500] if log1_content else '[EMPTY - SUCCESS]'}")

if result.returncode != 0:
    print("\nFAILED! Stopping.")
    import sys
    sys.exit(1)

# Step 2: UpdateDBCfg
log2 = r"D:\Git\Public_Trade_Module\Документация\Валидация\logs\update-with-form.log"
cmd2 = [
    exe, "DESIGNER",
    "/F", ib_path,
    "/UpdateDBCfg",
    "/DisableStartupDialogs",
    "/DisableStartupMessages",
    "/Out", log2
]

print("\nStep 2: UpdateDBCfg...")
result = subprocess.run(cmd2, timeout=300)
log2_content = pathlib.Path(log2).read_text(encoding='utf-8-sig').strip() if pathlib.Path(log2).exists() else "[NO LOG]"
print(f"  Exit code: {result.returncode}")
print(f"  Log: {log2_content[:500] if log2_content else '[EMPTY - SUCCESS]'}")
