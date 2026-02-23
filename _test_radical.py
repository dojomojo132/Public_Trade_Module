# -*- coding: utf-8 -*-
"""
РАДИКАЛЬНЫЙ ТЕСТ:
1. Удаляем ТестыРМК из Проверка/ полностью
2. Восстанавливаем Configuration.xml и ConfigDumpInfo.xml из git checkout (CRLF)
3. Запускаем LoadConfigFromFiles
Если РАБОТАЕТ → проблема ТОЛЬКО в ТестыРМК
Если НЕ РАБОТАЕТ → проблема в чём-то другом
"""
import subprocess, pathlib, shutil, time

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")
PROVERKA = ROOT / "Конфигурация" / "Проверка"
ONE_C = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
IB_PATH = r"D:\Confiq\Public Trade Module"
LOG_PARENT = ROOT / "logs"
LOG_PARENT.mkdir(exist_ok=True)

# Шаг 1: Удаляем ТестыРМК ИЗ ПРОВЕРКА
tests_xml = PROVERKA / "DataProcessors" / "ТестыРМК.xml"
tests_dir = PROVERKA / "DataProcessors" / "ТестыРМК"

print("== Шаг 1: Удаляем ТестыРМК из Проверка/ ==")
if tests_xml.exists():
    tests_xml.unlink()
    print(f"  [DEL] ТестыРМК.xml")
if tests_dir.exists():
    shutil.rmtree(str(tests_dir))
    print(f"  [DEL] ТестыРМК/ папка")

# Шаг 2: Восстанавливаем из git checkout (CRLF)
print()
print("== Шаг 2: git checkout 09e34c3 Configuration.xml и ConfigDumpInfo.xml ==")
for fname in ["Configuration.xml", "ConfigDumpInfo.xml"]:
    res = subprocess.run(
        ["git", "checkout", "09e34c3", "--", f"Конфигурация/Проверка/{fname}"],
        capture_output=True, text=True, cwd=str(ROOT)
    )
    f_path = PROVERKA / fname
    sz = f_path.stat().st_size if f_path.exists() else 0
    crlf = f_path.read_bytes().count(b'\r\n') if f_path.exists() else 0
    print(f"  rc={res.returncode} {fname}: {sz}b CRLF={crlf}")

# Проверяем что ТестыРМК НЕТ
cfg = (PROVERKA / "Configuration.xml").read_bytes()
rmk = "ТестыРМК" in cfg.decode("utf-8-sig", errors="ignore")
print(f"  ТестыРМК в Configuration.xml: {rmk}")

# Шаг 3: LoadConfigFromFiles
print()
print("== Шаг 3: LoadConfigFromFiles ==")
log_path = LOG_PARENT / "test_radical.log"
if log_path.exists():
    log_path.unlink()

result = subprocess.run(
    [ONE_C, "DESIGNER",
     "/F", IB_PATH,
     "/LoadConfigFromFiles", str(PROVERKA),
     "/DisableStartupDialogs", "/DisableStartupMessages",
     "/Out", str(log_path)],
    capture_output=True,
    timeout=90,
)

time.sleep(2)
print(f"  Exit code: {result.returncode}")
if log_path.exists():
    log_bytes = log_path.read_bytes()
    try:
        log_text = log_bytes.decode("utf-8-sig")
    except:
        log_text = log_bytes.decode("cp1251", errors="replace")
    print(f"  Log size: {len(log_bytes)} bytes")
    print(f"  Log content:\n{log_text[:1000]}")
else:
    print(f"  NO LOG! stdout={result.stdout[:200]} stderr={result.stderr[:200]}")

print()
print("Тест завершён.")
