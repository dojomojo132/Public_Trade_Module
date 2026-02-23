# -*- coding: utf-8 -*-
"""Тест: временно убрать ТестыРМК из Проверка/, запустить 1С загрузку, вернуть."""
import pathlib, subprocess, sys

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")
PROVERKA = ROOT / "Конфигурация" / "Проверка"

# Правим только Проверка/ (не Конфигурация/)
conf  = PROVERKA / "Configuration.xml"
cdi   = PROVERKA / "ConfigDumpInfo.xml"

# — читаем с BOM-сохранением —
def read_bom(path):
    raw = path.read_bytes()
    bom = raw[:3] if raw[:3] == b"\xef\xbb\xbf" else b""
    return bom, raw[len(bom):].decode("utf-8")

def write_bom(path, bom, text):
    path.write_bytes(bom + text.encode("utf-8"))

# Сохраняем оригиналы
conf_bom, conf_orig = read_bom(conf)
cdi_bom,  cdi_orig  = read_bom(cdi)

# Убираем ТестыРМК
conf_temp = conf_orig.replace("\t\t\t<DataProcessor>ТестыРМК</DataProcessor>\n", "")
cdi_temp  = cdi_orig
for line in [
    '\t\t<Metadata name="DataProcessor.ТестыРМК" id="f7a8b9c0-d1e2-4f3a-5b6c-7d8e9f0a1b2c" configVersion="a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d600000000" />\n',
    '\t\t<Metadata name="DataProcessor.ТестыРМК.Form.Форма" id="a2b3c4d5-e6f7-4a8b-9c0d-e1f2a3b4c5d6" configVersion="b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e700000000" />\n',
    '\t\t<Metadata name="DataProcessor.ТестыРМК.Form.Форма.Form" id="a2b3c4d5-e6f7-4a8b-9c0d-e1f2a3b4c5d6.0" configVersion="c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f800000000" />\n',
]:
    cdi_temp = cdi_temp.replace(line, "")

write_bom(conf, conf_bom, conf_temp)
write_bom(cdi,  cdi_bom,  cdi_temp)
print("Временные файлы записаны (ТестыРМК убран из Проверка/)")

# Запускаем 1С LoadConfigFromFiles
cmd = [
    r"C:\Program Files\1cv8\8.3.27.1765\bin\1cv8.exe",
    "DESIGNER",
    "/F", r"D:\Confiq\Public Trade Module",
    "/LoadConfigFromFiles", str(PROVERKA),
    "/DisableStartupDialogs", "/DisableStartupMessages",
    "/Out", str(ROOT / "logs" / "test_without_tests_rmk.log"),
]
# Попробуем найти 1cv8.exe
import glob
exes = (
    glob.glob(r"C:\Program Files\1cv8\*\bin\1cv8.exe") +
    glob.glob(r"C:\Program Files (x86)\1cv8\*\bin\1cv8.exe")
)
if not exes:
    print("1cv8.exe не найден — тест только из файлов")
else:
    cmd[0] = exes[-1]
    print(f"Запуск: {' '.join(cmd[:5])}")
    result = subprocess.run(cmd, timeout=60)
    logpath = ROOT / "logs" / "test_without_tests_rmk.log"
    if logpath.exists():
        log = logpath.read_text(encoding="utf-8-sig", errors="replace").strip()
        print(f"Лог: {log[:200]!r}")
    print(f"Exit code: {result.returncode}")

# Восстанавливаем оригиналы
write_bom(conf, conf_bom, conf_orig)
write_bom(cdi,  cdi_bom,  cdi_orig)
print("\nОригинальные файлы восстановлены.")
