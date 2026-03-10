# -*- coding: utf-8 -*-
"""
Восстановить ИБ из бэкапа 232753 (сегодня, до наших работ)
и попробовать LoadConfigFromFiles с текущей конфигурацией.
"""
import subprocess, pathlib, time

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")
ONE_C = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
IB_PATH = r"D:\Confiq\Public Trade Module"
BACKUPS = ROOT / "Документация" / "Валидация" / "backups"
LOG_PARENT = ROOT / "logs"
LOG_PARENT.mkdir(exist_ok=True)
PROVERKA = ROOT / "Конфигурация" / "Проверка"

backup = BACKUPS / "PTM-backup-20260223-232753.dt"
print(f"Бэкап: {backup.name} ({backup.stat().st_size // 1048576} MB)")
print(f"Время: 23:27 (до наших работ с тестами)")

# Восстановление
print("\n== RestoreIB ==")
log1 = LOG_PARENT / "restore_232753.log"
if log1.exists(): log1.unlink()

result1 = subprocess.run(
    [ONE_C, "DESIGNER", "/F", IB_PATH,
     "/RestoreIB", str(backup),
     "/DisableStartupDialogs", "/DisableStartupMessages",
     "/Out", str(log1)],
    capture_output=True, timeout=300
)
time.sleep(3)
print(f"Exit code: {result1.returncode}")
if log1.exists():
    print(f"Log: {log1.read_bytes().decode('utf-8-sig', errors='replace')[:200]}")

# CheckConfig (проверим состояние конфига в бэкапе)
print("\n== CheckConfig ==")
log2 = LOG_PARENT / "restore_232753_check.log"
if log2.exists(): log2.unlink()

result2 = subprocess.run(
    [ONE_C, "DESIGNER", "/F", IB_PATH,
     "/CheckConfig",
     "/DisableStartupDialogs", "/DisableStartupMessages",
     "/Out", str(log2)],
    capture_output=True, timeout=120
)
time.sleep(2)
print(f"CheckConfig Exit code: {result2.returncode}")
if log2.exists():
    b2 = log2.read_bytes()
    txt2 = b2.decode("utf-8-sig", errors="replace")
    print(f"Log ({len(b2)}b): {txt2[:300]}")

if result2.returncode != 0:
    print("\nКонфиг в бэкапе ПОВРЕЖДЁН — нужно запустить LoadConfigFromFiles")
    print("\n== LoadConfigFromFiles ==")
    log3 = LOG_PARENT / "restore_232753_load.log"
    if log3.exists(): log3.unlink()
    
    result3 = subprocess.run(
        [ONE_C, "DESIGNER", "/F", IB_PATH,
         "/LoadConfigFromFiles", str(PROVERKA),
         "/DisableStartupDialogs", "/DisableStartupMessages",
         "/Out", str(log3)],
        capture_output=True, timeout=180
    )
    time.sleep(2)
    print(f"LoadConfig Exit code: {result3.returncode}")
    if log3.exists():
        b3 = log3.read_bytes()
        txt3 = b3.decode("utf-8-sig", errors="replace")
        print(f"Log ({len(b3)}b): {txt3[:500]}")
    else:
        print("Лог не создан!")

print("\nГотово.")
