# -*- coding: utf-8 -*-
"""Расширенный тест: убрать ТестыРМК ПОЛНОСТЬЮ (файлы + конфиг) и попробовать загрузку."""
import pathlib, subprocess, glob, time, shutil, os

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")
PROVERKA = ROOT / "Конфигурация" / "Проверка"
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "test_full_remove.log"

exes = sorted(glob.glob(r"C:\Program Files\1cv8\*\bin\1cv8.exe"), reverse=True)
EXE = exes[0]
print(f"1cv8.exe: {EXE}")

def read_bom(path):
    raw = path.read_bytes()
    bom = raw[:3] if raw[:3] == b"\xef\xbb\xbf" else b""
    return bom, raw[len(bom):].decode("utf-8")

def write_bom(path, bom, text):
    path.write_bytes(bom + text.encode("utf-8"))

# Сохраняем оригиналы
conf = PROVERKA / "Configuration.xml"
cdi  = PROVERKA / "ConfigDumpInfo.xml"
conf_bom, conf_orig = read_bom(conf)
cdi_bom,  cdi_orig  = read_bom(cdi)

# Создаём временные версии БЕЗ ТестыРМК
conf_tmp = conf_orig.replace("\t\t\t<DataProcessor>ТестыРМК</DataProcessor>\r\n", "")
conf_tmp = conf_tmp.replace("\t\t\t<DataProcessor>ТестыРМК</DataProcessor>\n", "")

cdi_filter = ['DataProcessor.ТестыРМК" id="f7a8b9c0', 'DataProcessor.ТестыРМК.Form']
cdi_tmp = "\n".join(
    line for line in cdi_orig.splitlines()
    if not any(s in line for s in cdi_filter)
) + "\n"

write_bom(conf, conf_bom, conf_tmp)
write_bom(cdi,  cdi_bom,  cdi_tmp)

# Временно переместить папку DataProcessors/ТестыРМК в другое место
dp_dir = PROVERKA / "DataProcessors" / "ТестыРМК"
dp_xml = PROVERKA / "DataProcessors" / "ТестыРМК.xml"
tmp_dir = ROOT / "_temp_tests_rmk"
tmp_xml = ROOT / "_temp_tests_rmk.xml"

if dp_dir.exists():
    shutil.move(str(dp_dir), str(tmp_dir))
    print(f"Временно перемещена папка: {dp_dir.name}/ → _temp_tests_rmk/")
if dp_xml.exists():
    shutil.move(str(dp_xml), str(tmp_xml))
    print(f"Временно перемещен файл: ТестыРМК.xml → _temp_tests_rmk.xml")

print(f"\nЗапуск LoadConfigFromFiles (полностью без ТестыРМК)...")
cmd = [
    EXE, "DESIGNER",
    "/F", r"D:\Confiq\Public Trade Module",
    "/LoadConfigFromFiles", str(PROVERKA),
    "/DisableStartupDialogs", "/DisableStartupMessages",
    "/Out", str(LOG_FILE),
]
try:
    result = subprocess.run(cmd, timeout=90, capture_output=True)
    excode = result.returncode
except subprocess.TimeoutExpired:
    excode = -2

time.sleep(1)
if LOG_FILE.exists():
    log = LOG_FILE.read_text(encoding="utf-8-sig", errors="replace").strip()
    print(f"Лог: {log[:300]!r}")
print(f"Exit code: {excode}")

if excode == 0:
    print("\n==> УСПЕШНО без ТестыРМК файлов! Ошибка была ТОЛЬКО в файлах ТестыРМК.")
elif excode == 1:
    print("\n==> ОШИБКА и без ТестыРМК файлов! Ошибка в другом месте конфигурации.")
else:
    print(f"\n==> Exit code {excode}")

# Восстанавливаем всё
write_bom(conf, conf_bom, conf_orig)
write_bom(cdi,  cdi_bom,  cdi_orig)
if tmp_dir.exists():
    shutil.move(str(tmp_dir), str(dp_dir))
if tmp_xml.exists():
    shutil.move(str(tmp_xml), str(dp_xml))
print("\nВсё восстановлено.")
