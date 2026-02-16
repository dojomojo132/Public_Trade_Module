# -*- coding: utf-8 -*-
"""
Шаг 1: Создать временную ИБ, загрузить БПО_ДЕМО XML → выгрузить .cf
"""
import subprocess
import pathlib
import shutil
import sys
import time

V8_EXE = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
BPO_XML = r"D:\Git\БПО_ДЕМО"
TEMP_IB = r"D:\Confiq\BPO_TEMP"
BPO_CF = r"D:\Git\Public_Trade_Module\CF\BPO_DEMO.cf"

def run_1c(args_str, description, timeout=600):
    """Запуск 1cv8.exe с параметрами"""
    cmd = f'"{V8_EXE}" {args_str}'
    print(f"\n{'='*60}")
    print(f"[ЭТАП] {description}")
    print(f"[CMD]  {cmd}")
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

# 1. Очистить/Создать временную ИБ
temp_path = pathlib.Path(TEMP_IB)
if temp_path.exists():
    print(f"\n[INFO] Удаляю старую временную ИБ: {TEMP_IB}")
    shutil.rmtree(TEMP_IB)

print(f"[INFO] Создаю временную ИБ: {TEMP_IB}")

# CREATEINFOBASE
ok = run_1c(
    f'CREATEINFOBASE "File={TEMP_IB}" /DisableStartupDialogs',
    "Создание временной ИБ"
)
if not ok:
    print("[ОШИБКА] Не удалось создать ИБ!")
    sys.exit(1)

# 2. Загрузить БПО XML в ИБ
ok = run_1c(
    f'DESIGNER /F "{TEMP_IB}" /LoadConfigFromFiles "{BPO_XML}" /DisableStartupDialogs /DisableStartupMessages',
    "Загрузка БПО XML в временную ИБ"
)
if not ok:
    print("[ОШИБКА] Не удалось загрузить БПО XML!")
    sys.exit(2)

# 3. Обновить БД
ok = run_1c(
    f'DESIGNER /F "{TEMP_IB}" /UpdateDBCfg /DisableStartupDialogs /DisableStartupMessages',
    "Обновление БД временной ИБ"
)
if not ok:
    print("[ПРЕДУПРЕЖДЕНИЕ] Обновление БД не удалось, но продолжаем (для .cf не критично)")

# 4. Выгрузить как .cf
cf_dir = pathlib.Path(BPO_CF).parent
cf_dir.mkdir(parents=True, exist_ok=True)

ok = run_1c(
    f'DESIGNER /F "{TEMP_IB}" /DumpCfg "{BPO_CF}" /DisableStartupDialogs /DisableStartupMessages',
    "Выгрузка БПО как .cf"
)
if not ok:
    print("[ОШИБКА] Не удалось выгрузить .cf!")
    sys.exit(3)

# 5. Проверяем результат
cf_path = pathlib.Path(BPO_CF)
if cf_path.exists():
    size_mb = cf_path.stat().st_size / 1024 / 1024
    print(f"\n{'='*60}")
    print(f"[УСПЕХ] БПО .cf создан: {BPO_CF}")
    print(f"[РАЗМЕР] {size_mb:.1f} МБ")
    print(f"{'='*60}")
else:
    print("[ОШИБКА] Файл .cf не найден!")
    sys.exit(4)

# 6. Удалить временную ИБ
print(f"\n[INFO] Удаляю временную ИБ...")
try:
    shutil.rmtree(TEMP_IB)
    print("[OK] Временная ИБ удалена")
except Exception as e:
    print(f"[ПРЕДУПРЕЖДЕНИЕ] Не удалось удалить временную ИБ: {e}")

print(f"\n{'='*60}")
print("[ГОТОВО] Следующий шаг:")
print("  1. Откройте Конфигуратор PTM (deploy-config.ps1 -Action Designer)")
print(f"  2. Конфигурация → Сравнить, объединить с конфигурацией из файла")
print(f"  3. Выберите файл: {BPO_CF}")
print(f"{'='*60}")
