# -*- coding: utf-8 -*-
"""
Шаг 2: Выгрузить объединённую конфигурацию в XML (обе папки: Конфигурация/ и Конфигурация/Проверка/)
"""
import subprocess
import pathlib
import shutil
import time
import sys

V8_EXE = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
IB_PATH = r"D:\Confiq\Public Trade Module"
CONFIG_DIR = r"D:\Git\Public_Trade_Module\Конфигурация"
CHECK_DIR = r"D:\Git\Public_Trade_Module\Конфигурация\Проверка"

def run_1c(args_str, description, timeout=600):
    """Запуск 1cv8.exe"""
    cmd = f'"{V8_EXE}" {args_str}'
    print(f"\n{'='*60}")
    print(f"[ЭТАП] {description}")
    print(f"[CMD]  {cmd[:200]}...")
    print(f"{'='*60}")
    
    start = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=True)
    elapsed = time.time() - start
    
    print(f"[TIME] {elapsed:.1f} сек")
    print(f"[CODE] {result.returncode}")
    if result.stdout:
        print(f"[STDOUT] {result.stdout[:500]}")
    if result.stderr:
        print(f"[STDERR] {result.stderr[:500]}")
    
    return result.returncode == 0

# 1. Выгрузить в основную папку
print("[INFO] Выгружаем конфигурацию в XML...")

# Выгружаем в папку Проверка (deploy использует именно её)
ok = run_1c(
    f'DESIGNER /F "{IB_PATH}" /DumpConfigToFiles "{CHECK_DIR}" /DisableStartupDialogs /DisableStartupMessages',
    "Выгрузка конфигурации в Конфигурация/Проверка"
)
if not ok:
    print("[ОШИБКА] Не удалось выгрузить конфигурацию!")
    sys.exit(1)

print(f"\n[INFO] Выгрузка завершена в: {CHECK_DIR}")

# 2. Подсчитаем количество файлов
check_path = pathlib.Path(CHECK_DIR)
xml_count = len(list(check_path.rglob("*.xml")))
bsl_count = len(list(check_path.rglob("*.bsl")))
print(f"[INFO] XML файлов: {xml_count}")
print(f"[INFO] BSL файлов: {bsl_count}")

# 3. Также выгружаем в основную папку (для git-контроля)
# Для этого нужно скопировать ключевые файлы из Проверка -> Конфигурация
# Но НЕ саму папку Проверка (чтобы не зациклить)
config_root = pathlib.Path(CONFIG_DIR)
check_root = pathlib.Path(CHECK_DIR)

print(f"\n[INFO] Синхронизируем Конфигурация/ с Конфигурация/Проверка/...")

# Копируем все файлы/папки из Проверка в Конфигурация, кроме самой папки Проверка
for item in check_root.iterdir():
    dest = config_root / item.name
    if item.name == "Проверка":
        continue  # Пропускаем вложенную Проверку
    
    if item.is_file():
        shutil.copy2(str(item), str(dest))
    elif item.is_dir():
        if dest.exists():
            shutil.rmtree(str(dest))
        shutil.copytree(str(item), str(dest))

print("[OK] Синхронизация завершена!")

# 4. Бэкап .dt
print(f"\n[INFO] Выгружаем .dt для git...")
dt_path = pathlib.Path(r"D:\Git\Public_Trade_Module\1Cv8.dt")
ok = run_1c(
    f'DESIGNER /F "{IB_PATH}" /DumpIB "{dt_path}" /DisableStartupDialogs /DisableStartupMessages',
    "Выгрузка .dt"
)
if ok:
    size_mb = dt_path.stat().st_size / 1024 / 1024
    print(f"[OK] .dt выгружен: {size_mb:.1f} МБ")

print(f"\n{'='*60}")
print("[ГОТОВО] Конфигурация выгружена в XML!")
print("  Следующий шаг: git commit + настройка сканера")
print(f"{'='*60}")
