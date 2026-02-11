# -*- coding: utf-8 -*-
import subprocess
import pathlib
import sys

# Пути
ib_path = r"D:\Git\Public_Trade_Module\ИБ\PTM"
config_path = r"D:\Git\Public_Trade_Module\Конфигурация"
exe_path = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
log_path = pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Валидация\logs\load_manual.log")

# Создаем папку для лога
log_path.parent.mkdir(parents=True, exist_ok=True)

print("Загрузка конфигурации из файлов...")
print(f"ИБ: {ib_path}")
print(f"Конфигурация: {config_path}")
print(f"Лог: {log_path}")

# Запускаем 1С
args = [
    exe_path,
    "DESIGNER",
    f"/F{ib_path}",
    f"/LoadConfigFromFiles{config_path}",
    f"/Out{log_path}",
    "/DisableStartupMessages",
    "/DisableStartupDialogs"
]

result = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace')

print(f"\nЗавершено с кодом: {result.returncode}")

if log_path.exists():
    print("\n=== ЛОГ 1С ===")
    with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
        log_content = f.read()
        print(log_content)
else:
    print("Лог-файл не создан")

if result.returncode == 0:
    print("\n✓ УСПЕШНО: Конфигурация загружена из файлов")
else:
    print(f"\n✗ ОШИБКА: Загрузка завершилась с кодом {result.returncode}")

sys.exit(result.returncode)
