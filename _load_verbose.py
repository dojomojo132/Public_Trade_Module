# -*- coding: utf-8 -*-
import subprocess
import pathlib
import sys
import time

ib = pathlib.Path(r"D:\Git\Public_Trade_Module\ИБ\PTM")
config = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")
exe = pathlib.Path(r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe")

print("="*70)
print("ЗАГРУЗКА КОНФИГУРАЦИИ 1С")
print("="*70)
print(f"\nИБ: {ib}")
print(f"Конфигурация: {config}")
print(f"1С: {exe}")

# Проверяем существование
if not ib.exists():
    print(f"\n✗ ОШИБКА: ИБ не найдена по пути {ib}")
    sys.exit(1)

if not config.exists():
    print(f"\n✗ ОШИБКА: Папка конфигурации не найдена {config}")
    sys.exit(1)

if not exe.exists():
    print(f"\n✗ ОШИБКА: Исполняемый файл 1С не найден {exe}")
    sys.exit(1)

print("\n✓ Все пути проверены")
print("\nЗапуск загрузки...")
print("-"*70)

start = time.time()

# Запускаем без лога, весь вывод в stdout
result = subprocess.run(
    [
        str(exe),
        "DESIGNER",
        f"/F{ib}",
        f"/LoadConfigFromFiles{config}",
        "/DisableStartupDialogs"
    ],
    capture_output=True,
    text=True,
    encoding='cp866',  # Windows console encoding
    errors='replace',
    timeout=180
)

duration = time.time() - start

print("-"*70)
print(f"\nВремя выполнения: {duration:.1f} сек")
print(f"Код возврата: {result.returncode}")

if result.stdout:
    print("\n" + "="*70)
    print("STDOUT:")
    print("="*70)
    print(result.stdout)

if result.stderr:
    print("\n" + "="*70)
    print("STDERR:")
    print("="*70)
    print(result.stderr)

if result.returncode == 0:
    print("\n" + "="*70)
    print("✓ УСПЕШНО: Конфигурация загружена")
    print("="*70)
else:
    print("\n" + "="*70)
    print(f"✗ ОШИБКА: Загрузка завершилась с кодом {result.returncode}")
    print("="*70)
    print("\nВозможные причины:")
    print("- Блокировка от другого процесса 1С")
    print("- Ошибки в XML-структуре конфигурации")
    print("- Недостаточно прав доступа")

sys.exit(result.returncode)
