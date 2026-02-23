# -*- coding: utf-8 -*-
"""
Тестируем: откат из PTM-backup-20260223-232558.dt (перед первым неудачным deploy),
затем CheckConfig и LoadConfigFromFiles.
"""
import subprocess, pathlib, time

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")
ONE_C = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
IB_PATH = r"D:\Confiq\Public Trade Module"
BACKUPS = ROOT / "Документация" / "Валидация" / "backups"
LOG_PARENT = ROOT / "logs"
LOG_PARENT.mkdir(exist_ok=True)
PROVERKA = ROOT / "Конфигурация" / "Проверка"

# Первый бэкап = состояние ИБ ПЕРЕД первым неудачным деплоем
backup_file = BACKUPS / "PTM-backup-20260223-232558.dt"
print(f"Бэкап: {backup_file.name} ({backup_file.stat().st_size // 1048576} MB)")

# Шаг 1: RestoreIB
print()
print("== Шаг 1: RestoreIB из первого бэкапа ==")
log1 = LOG_PARENT / "restore_test.log"
if log1.exists(): log1.unlink()

result1 = subprocess.run(
    [ONE_C, "DESIGNER",
     "/F", IB_PATH,
     "/RestoreIB", str(backup_file),
     "/DisableStartupDialogs", "/DisableStartupMessages",
     "/Out", str(log1)],
    capture_output=True, timeout=300
)
time.sleep(3)
print(f"Exit code: {result1.returncode}")
if log1.exists():
    b = log1.read_bytes()
    txt = b.decode("utf-8-sig", errors="replace")
    print(f"Log ({len(b)}b): {txt[:300]}")

# Шаг 2: CheckConfig
print()
print("== Шаг 2: CheckConfig ==")
log2 = LOG_PARENT / "restore_checkconfig.log"
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
print(f"CheckConfig Exit code: {result2.returncode}")
if log2.exists():
    b2 = log2.read_bytes()
    txt2 = b2.decode("utf-8-sig", errors="replace")
    print(f"Log ({len(b2)}b): {txt2[:500]}")

# Шаг 3: Если CheckConfig OK, то LoadConfigFromFiles
if result2.returncode == 0:
    print()
    print("== Шаг 3: LoadConfigFromFiles (CheckConfig прошёл!) ==")
    # Восстанавливаем Configuration.xml с ТестыРМК из baseline (CRLF version)
    # Сначала делаем git checkout чистого baseline
    for fname in ["Configuration.xml", "ConfigDumpInfo.xml"]:
        res = subprocess.run(
            ["git", "checkout", "09e34c3", "--", f"Конфигурация/Проверка/{fname}"],
            capture_output=True, text=True, cwd=str(ROOT)
        )
        print(f"  checkout {fname}: rc={res.returncode}")
    
    log3 = LOG_PARENT / "restore_loadconfig.log"
    if log3.exists(): log3.unlink()
    
    result3 = subprocess.run(
        [ONE_C, "DESIGNER",
         "/F", IB_PATH,
         "/LoadConfigFromFiles", str(PROVERKA),
         "/DisableStartupDialogs", "/DisableStartupMessages",
         "/Out", str(log3)],
        capture_output=True, timeout=120
    )
    time.sleep(2)
    print(f"LoadConfig Exit code: {result3.returncode}")
    if log3.exists():
        b3 = log3.read_bytes()
        txt3 = b3.decode("utf-8-sig", errors="replace")
        print(f"Log ({len(b3)}b): {txt3[:1000]}")
else:
    print()
    print("CheckConfig ПРОВАЛЁН — даже в этом бэкапе конфигурация неправильная!")

print()
print("Тест завершён.")
