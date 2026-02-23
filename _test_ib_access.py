# -*- coding: utf-8 -*-
"""Проверяем состояние информационной базы."""
import subprocess, pathlib, time

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")
ONE_C = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
IB_PATH = r"D:\Confiq\Public Trade Module"
LOG_PARENT = ROOT / "logs"
LOG_PARENT.mkdir(exist_ok=True)

print(f"IB path: {IB_PATH}")
ib = pathlib.Path(IB_PATH)
print(f"IB exists: {ib.exists()}")

if ib.exists():
    files = list(ib.iterdir())
    print(f"IB files ({len(files)}): {[f.name for f in files[:20]]}")
else:
    print("IB NOT FOUND!")

# Тест 1: DumpIB (проверка доступности IB)
print()
print("== Тест DumpIB ==")
log_path = LOG_PARENT / "test_dumpib.log"
dump_path = ROOT / "logs" / "test_dump.dt"

if log_path.exists(): log_path.unlink()
if dump_path.exists(): dump_path.unlink()

result = subprocess.run(
    [ONE_C, "DESIGNER",
     "/F", IB_PATH,
     "/DumpIB", str(dump_path),
     "/DisableStartupDialogs", "/DisableStartupMessages",
     "/Out", str(log_path)],
    capture_output=True, timeout=120
)
time.sleep(2)
print(f"Exit code: {result.returncode}")
if log_path.exists():
    log_b = log_path.read_bytes()
    print(f"Log ({len(log_b)}b): {log_b.decode('utf-8-sig', errors='replace')[:200]}")

# Тест 2: CheckConfig
print()
print("== Тест CheckConfig ==")
log2 = LOG_PARENT / "test_checkconfig.log"
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
    log2_b = log2.read_bytes()
    txt2 = log2_b.decode("utf-8-sig", errors="replace")
    print(f"Log ({len(log2_b)}b): {txt2[:500]}")

print()
print("Готово.")
