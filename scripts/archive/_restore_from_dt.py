# -*- coding: utf-8 -*-
"""
Восстанавливаем ИБ из 1Cv8.dt (февраль 17, до проблемы).
Затем тестируем CheckConfig и LoadConfigFromFiles.
"""
import subprocess, pathlib, time

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")
ONE_C = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
IB_PATH = r"D:\Confiq\Public Trade Module"
DT_SOURCE = ROOT / "1Cv8.dt"
LOG_PARENT = ROOT / "logs"
LOG_PARENT.mkdir(exist_ok=True)

PROVERKA = ROOT / "Конфигурация" / "Проверка"

print(f"DT source: {DT_SOURCE} ({DT_SOURCE.stat().st_size // 1048576} MB)")
print(f"Modified: {time.ctime(DT_SOURCE.stat().st_mtime)}")

# Шаг 1: RestoreIB из 1Cv8.dt
print()
print("== Шаг 1: RestoreIB из 1Cv8.dt ==")
log1 = LOG_PARENT / "restore_from_1cv8dt.log"
if log1.exists(): log1.unlink()

result1 = subprocess.run(
    [ONE_C, "DESIGNER",
     "/F", IB_PATH,
     "/RestoreIB", str(DT_SOURCE),
     "/DisableStartupDialogs", "/DisableStartupMessages",
     "/Out", str(log1)],
    capture_output=True, timeout=300
)
time.sleep(3)
print(f"Exit code: {result1.returncode}")
if log1.exists():
    b = log1.read_bytes()
    print(f"Log ({len(b)}b): {b.decode('utf-8-sig', errors='replace')[:300]}")

# Шаг 2: CheckConfig
print()
print("== Шаг 2: CheckConfig ==")
log2 = LOG_PARENT / "after_restore_checkconfig.log"
if log2.exists(): log2.unlink()

result2 = subprocess.run(
    [ONE_C, "DESIGNER",
     "/F", IB_PATH,
     "/CheckConfig",
     "/DisableStartupDialogs", "/DisableStartupMessages",
     "/Out", str(log2)],
    capture_output=True, timeout=120
)
time.sleep(2)
print(f"Exit code: {result2.returncode}")
if log2.exists():
    b2 = log2.read_bytes()
    print(f"Log ({len(b2)}b): {b2.decode('utf-8-sig', errors='replace')[:500]}")

print()
print("Готово.")
