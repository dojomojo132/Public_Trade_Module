# -*- coding: utf-8 -*-
"""
Восстанавливаем ИБ из 1Cv8.dt (17 февраля — до проблемы).
Затем немедленно пробуем LoadConfigFromFiles с актуальной конфигурацией.
"""
import subprocess, pathlib, time

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")
ONE_C = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
IB_PATH = r"D:\Confiq\Public Trade Module"
DT_SOURCE = ROOT / "1Cv8.dt"
LOG_PARENT = ROOT / "logs"
LOG_PARENT.mkdir(exist_ok=True)
PROVERKA = ROOT / "Конфигурация" / "Проверка"

print(f"DT: {DT_SOURCE.name} ({DT_SOURCE.stat().st_size // 1048576} MB, {time.ctime(DT_SOURCE.stat().st_mtime)})")

# Шаг 1: Восстанавливаем Configuration.xml из git checkout 09e34c3 без ТестыРМК
print()
print("== Шаг 1: Подготовка конфигурации (git checkout 09e34c3 без ТестыРМК) ==")

import shutil

# Убираем ТестыРМК если есть
tests_xml = PROVERKA / "DataProcessors" / "ТестыРМК.xml"
tests_dir = PROVERKA / "DataProcessors" / "ТестыРМК"
if tests_xml.exists():
    tests_xml.unlink()
    print("  Удалён ТестыРМК.xml")
if tests_dir.exists():
    shutil.rmtree(str(tests_dir))
    print("  Удалена папка ТестыРМК/")

# Checkout CRLF версий
for fname in ["Configuration.xml", "ConfigDumpInfo.xml"]:
    res = subprocess.run(
        ["git", "checkout", "09e34c3", "--", f"Конфигурация/Проверка/{fname}"],
        capture_output=True, cwd=str(ROOT)
    )
    f = PROVERKA / fname
    print(f"  {fname}: {f.stat().st_size}b CRLF={f.read_bytes().count(b'chr13')} rc={res.returncode}")

# Шаг 2: Восстановление ИБ из 1Cv8.dt
print()
print("== Шаг 2: RestoreIB из 1Cv8.dt ==")
log1 = LOG_PARENT / "restore_maindt.log"
if log1.exists(): log1.unlink()

result1 = subprocess.run(
    [ONE_C, "DESIGNER", "/F", IB_PATH,
     "/RestoreIB", str(DT_SOURCE),
     "/DisableStartupDialogs", "/DisableStartupMessages",
     "/Out", str(log1)],
    capture_output=True, timeout=300
)
time.sleep(3)
print(f"RestoreIB Exit code: {result1.returncode}")
if log1.exists():
    b = log1.read_bytes()
    print(f"Log: {b.decode('utf-8-sig', errors='replace')[:200]}")

if result1.returncode != 0:
    print("ОШИБКА восстановления! Останавливаемся.")
    exit(1)

# Шаг 3: CheckConfig (после restore)
print()
print("== Шаг 3: CheckConfig после RestoreIB ==")
log_cc = LOG_PARENT / "restore_maindt_checkconfig.log"
if log_cc.exists(): log_cc.unlink()

result_cc = subprocess.run(
    [ONE_C, "DESIGNER", "/F", IB_PATH,
     "/CheckConfig",
     "/DisableStartupDialogs", "/DisableStartupMessages",
     "/Out", str(log_cc)],
    capture_output=True, timeout=120
)
time.sleep(2)
print(f"CheckConfig Exit code: {result_cc.returncode}")
if log_cc.exists():
    b_cc = log_cc.read_bytes()
    print(f"Log ({len(b_cc)}b): {b_cc.decode('utf-8-sig', errors='replace')[:500]}")

# Шаг 4: LoadConfigFromFiles
print()
print("== Шаг 4: LoadConfigFromFiles ==")
log_lc = LOG_PARENT / "restore_maindt_loadconfig.log"
if log_lc.exists(): log_lc.unlink()

result_lc = subprocess.run(
    [ONE_C, "DESIGNER", "/F", IB_PATH,
     "/LoadConfigFromFiles", str(PROVERKA),
     "/DisableStartupDialogs", "/DisableStartupMessages",
     "/Out", str(log_lc)],
    capture_output=True, timeout=120
)
time.sleep(2)
print(f"LoadConfig Exit code: {result_lc.returncode}")
if log_lc.exists():
    b_lc = log_lc.read_bytes()
    txt_lc = b_lc.decode("utf-8-sig", errors="replace")
    print(f"Log ({len(b_lc)}b): {txt_lc[:1000]}")
    if "Ошибка" in txt_lc:
        print("ОШИБКА в LoadConfig!")
    else:
        print("LoadConfig УСПЕШЕН!")
else:
    print("Лог не создан!")

print()
print("Тест завершён.")
