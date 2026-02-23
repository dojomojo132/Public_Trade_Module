# -*- coding: utf-8 -*-
"""
Тест: попробовать LoadConfigFromFiles без ТестыРМК в Configuration.xml.
Восстановить оригинал после теста.
"""
import pathlib, subprocess, glob, time, shutil

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")
PROVERKA = ROOT / "Конфигурация" / "Проверка"
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "test_no_tests_rmk.log"

# === Найти 1cv8.exe ===
exes = (
    glob.glob(r"C:\Program Files\1cv8\*\bin\1cv8.exe") +
    glob.glob(r"C:\Program Files (x86)\1cv8\*\bin\1cv8.exe")
)
if not exes:
    print("1cv8.exe не найден"); exit(1)
EXE = max(exes)  # Самая новая версия
print(f"1cv8.exe: {EXE}")

# === Backup helpers ===
def read_bom(path):
    raw = path.read_bytes()
    bom = raw[:3] if raw[:3] == b"\xef\xbb\xbf" else b""
    return bom, raw[len(bom):].decode("utf-8")

def write_bom(path, bom, text):
    path.write_bytes(bom + text.encode("utf-8"))

# === Сохраняем оригиналы ===
conf = PROVERKA / "Configuration.xml"
cdi  = PROVERKA / "ConfigDumpInfo.xml"
conf_bom, conf_orig = read_bom(conf)
cdi_bom,  cdi_orig  = read_bom(cdi)

# === Создаём временные версии БЕЗ ТестыРМК ===
conf_tmp = conf_orig.replace("\t\t\t<DataProcessor>ТестыРМК</DataProcessor>\r\n", "")
conf_tmp = conf_tmp.replace("\t\t\t<DataProcessor>ТестыРМК</DataProcessor>\n", "")

cdi_lines_to_remove = [
    'DataProcessor.ТестыРМК" id="f7a8b9c0',
    'DataProcessor.ТестыРМК.Form',
]

cdi_tmp_lines = []
for line in cdi_orig.splitlines(keepends=True):
    if not any(s in line for s in cdi_lines_to_remove):
        cdi_tmp_lines.append(line)
cdi_tmp = "".join(cdi_tmp_lines)

# === Записываем временные версии ===
write_bom(conf, conf_bom, conf_tmp)
write_bom(cdi,  cdi_bom,  cdi_tmp)
print("\nВременные файлы записаны (без ТестыРМК)")
print(f"Configuration.xml изменён: {'ТестыРМК' not in conf_tmp}")
print(f"ConfigDumpInfo.xml изменён: {'ТестыРМК' not in cdi_tmp}")

# === Запускаем 1C ===
cmd = [
    EXE, "DESIGNER",
    "/F", r"D:\Confiq\Public Trade Module",
    "/LoadConfigFromFiles", str(PROVERKA),
    "/DisableStartupDialogs", "/DisableStartupMessages",
    "/Out", str(LOG_FILE),
]
print(f"\nЗапуск LoadConfigFromFiles...")
try:
    result = subprocess.run(cmd, timeout=90, capture_output=True)
    excode = result.returncode
except subprocess.TimeoutExpired:
    excode = -2
    print("ТАЙМАУТ!")

# === Читаем лог ===
time.sleep(1)
if LOG_FILE.exists():
    log = LOG_FILE.read_text(encoding="utf-8-sig", errors="replace").strip()
    print(f"Лог: {log[:300]!r}")
else:
    print("Лог не найден")

print(f"Exit code: {excode}")
if excode == 0:
    print("\n==> УСПЕШНО без ТестыРМК! Проблема в файлах ТестыРМК.")
elif excode == 1:
    print("\n==> ОШИБКА и без ТестыРМК! Проблема в другом месте.")
else:
    print(f"\n==> Exit code {excode}")

# === Восстанавливаем оригиналы ===
write_bom(conf, conf_bom, conf_orig)
write_bom(cdi,  cdi_bom,  cdi_orig)
print("\nОригинальные файлы восстановлены.")
