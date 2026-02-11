# -*- coding: utf-8 -*-
import subprocess
import pathlib
import sys

ib = r"D:\Git\Public_Trade_Module\ИБ\PTM"
config = r"D:\Git\Public_Trade_Module\Конфигурация"
exe = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
log = pathlib.Path(r"D:\Git\Public_Trade_Module\temp_load.log")

print("Загрузка конфигурации с логированием...")

# Загрузка с логом
result = subprocess.run(
    [exe, "DESIGNER", f"/F{ib}", f"/LoadConfigFromFiles{config}", f"/Out{log}", "/DisableStartupDialogs"],
    capture_output=True,
    text=True,
    encoding='cp866',  # Кодировка консоли Windows
    errors='replace',
    timeout=120
)

print(f"\nКод завершения: {result.returncode}")

# Читаем лог
if log.exists():
    print("\n" + "="*60)
    print("ЛОГ 1С:")
    print("="*60)
    with open(log, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
        print(content if content.strip() else "(пустой)")
    log.unlink()  # Удаляем временный лог

# Вывод из stdout/stderr
if result.stdout:
    print("\n" + "="*60)
    print("STDOUT:")
    print("="*60)
    print(result.stdout)

if result.stderr:
    print("\n" + "="*60)
    print("STDERR:")
    print("="*60)
    print(result.stderr)

sys.exit(result.returncode)
