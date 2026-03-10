# -*- coding: utf-8 -*-
"""
Полный тест: сравниваем LF vs CRLF версию конфигурации для 1C LoadConfigFromFiles.
1C на Windows может требовать CRLF в XML-файлах дампа (как создаёт 1С на Windows).
"""
import subprocess, pathlib, time

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")
PROVERKA = ROOT / "Конфигурация" / "Проверка"
ONE_C = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
IB_PATH = r"D:\Confiq\Public Trade Module"
LOG_PARENT = ROOT / "logs"
LOG_PARENT.mkdir(exist_ok=True)

def run_load(log_name, label):
    log_path = LOG_PARENT / log_name
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
        cwd=str(ROOT)
    )
    time.sleep(2)
    code = result.returncode
    if log_path.exists():
        log_bytes = log_path.read_bytes()
        try:
            log_text = log_bytes.decode("utf-8-sig")
        except:
            log_text = log_bytes.decode("cp1251", errors="replace")
        status = "УСПЕХ" if ("Неизвестный объект" in log_text or (code == 0 and len(log_bytes) > 100)) else "ОШИБКА"
        print(f"  [{label}] code={code} log={len(log_bytes)}b: {log_text[:200].strip()}")
    else:
        print(f"  [{label}] code={code} NO LOG, stderr={result.stderr[:100]}")

# ============================================================
print("=== Тест 1: CRLF-версия (git checkout) ===")
# Используем git checkout для восстановления CRLF-версии
for fname in ["Configuration.xml", "ConfigDumpInfo.xml"]:
    res = subprocess.run(
        ["git", "checkout", "09e34c3", "--",
         f"Конфигурация/Проверка/{fname}"],
        capture_output=True,
        text=True,
        cwd=str(ROOT)
    )
    print(f"  git checkout {fname}: rc={res.returncode} {res.stderr[:100].strip()}")

cfg = (PROVERKA / "Configuration.xml").read_bytes()
crlf_count = cfg.count(b'\r\n')
rmk = "ТестыРМК✓" if "ТестыРМК".encode("utf-8") in cfg else "нет ТестыРМК"
print(f"  Configuration.xml: {len(cfg)}b, CRLF={crlf_count}, {rmk}")

run_load("test_crlf.log", "CRLF без ТестыРМК")

# ============================================================
print()
print("=== Тест 2: LF-версия ===")
for fname in ["Configuration.xml", "ConfigDumpInfo.xml"]:
    result = subprocess.run(
        ["git", "show", f"09e34c3:Конфигурация/Проверка/{fname}"],
        capture_output=True, cwd=str(ROOT)
    )
    if result.returncode == 0:
        out_file = PROVERKA / fname
        out_file.write_bytes(result.stdout)
        print(f"  [OK] {fname}: {len(result.stdout)}b, CRLF={result.stdout.count(b'chr13')}")

cfg2 = (PROVERKA / "Configuration.xml").read_bytes()
crlf2 = cfg2.count(b'\r\n')
rmk2 = "ТестыРМК✓" if "ТестыРМК".encode("utf-8") in cfg2 else "нет ТестыРМК"
print(f"  Configuration.xml: {len(cfg2)}b, CRLF={crlf2}, {rmk2}")

run_load("test_lf.log", "LF без ТестыРМК")

print()
print("Тест завершён.")
