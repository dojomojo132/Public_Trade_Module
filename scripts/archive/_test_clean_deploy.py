# -*- coding: utf-8 -*-
"""
МИНИМАЛЬНЫЙ ТЕСТ: восстанавливаем Configuration.xml и ConfigDumpInfo.xml
100% из git 09e34c3 (без ТестыРМК), запускаем LoadConfigFromFiles напрямую.
Цель: проверить — работает ли ЧИСТЫЙ baseline?
"""
import subprocess, pathlib, time

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")
PROVERKA = ROOT / "Конфигурация" / "Проверка"
ONE_C = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
IB_PATH = r"D:\Confiq\Public Trade Module"
LOG_PATH = ROOT / "logs" / "test_clean_baseline.log"

# Шаг 1: Восстанавливаем файлы из git 09e34c3
print("== Шаг 1: Восстановление Configuration.xml и ConfigDumpInfo.xml из git ==")

for fname in ["Configuration.xml", "ConfigDumpInfo.xml"]:
    result = subprocess.run(
        ["git", "show", f"09e34c3:Конфигурация/Проверка/{fname}"],
        capture_output=True, cwd=str(ROOT)
    )
    if result.returncode == 0:
        out_file = PROVERKA / fname
        out_file.write_bytes(result.stdout)
        crlf = result.stdout.count(b'\r\n')
        print(f"  [OK] {fname}: {len(result.stdout)} bytes, CRLF={crlf}")
    else:
        print(f"  [ERR] {fname}: {result.stderr[:100]}")

# Проверяем что ТестыРМК НЕТ в Configuration.xml
cfg = (PROVERKA / "Configuration.xml").read_bytes()
if "ТестыРМК".encode("utf-8") in cfg:
    print("  [WARN] ТестыРМК ещё есть в Configuration.xml!")
else:
    print("  Без ТестыРМК ✓")

# Шаг 2: LoadConfigFromFiles
print()
print("== Шаг 2: LoadConfigFromFiles ==")
LOG_PATH.parent.mkdir(exist_ok=True)
if LOG_PATH.exists():
    LOG_PATH.unlink()

result = subprocess.run(
    [ONE_C, "DESIGNER",
     "/F", IB_PATH,
     "/LoadConfigFromFiles", str(PROVERKA),
     "/DisableStartupDialogs", "/DisableStartupMessages",
     "/Out", str(LOG_PATH)],
    capture_output=True,
    timeout=90,
    cwd=str(ROOT)
)

time.sleep(2)
print(f"  Exit code: {result.returncode}")
if LOG_PATH.exists():
    log_bytes = LOG_PATH.read_bytes()
    try:
        log_text = log_bytes.decode("utf-8-sig")
    except:
        log_text = log_bytes.decode("cp1251", errors="replace")
    print(f"  Log size: {len(log_bytes)} bytes")
    print(f"  Log content: {log_text[:500]}")
else:
    print("  Log file NOT created!")
    if result.stdout:
        print(f"  stdout: {result.stdout[:300].decode('cp1251', errors='replace')}")
    if result.stderr:
        print(f"  stderr: {result.stderr[:300].decode('cp1251', errors='replace')}")

print()
print("Тест завершён.")
