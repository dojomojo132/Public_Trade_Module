# -*- coding: utf-8 -*-
"""Восстановление базы из .dt и загрузка конфигурации"""
import subprocess
import pathlib
import shutil

v8 = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
ib = r"D:\Confiq\Public Trade Module"
dt_file = pathlib.Path(r"D:\Git\Public_Trade_Module\1Cv8.dt")
log_dir = pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Валидация\logs")

log_dir.mkdir(parents=True, exist_ok=True)

# Проверяем наличие .dt файла
if not dt_file.exists():
    print(f"ОШИБКА: {dt_file} не найден")
    exit(1)

print(f"dt файл: {dt_file} ({dt_file.stat().st_size / 1024 / 1024:.1f} MB)")

# 1. Восстановление из .dt
log_restore = log_dir / "restore_dt.log"
print(f"\n1. Восстановление базы из {dt_file.name}...")

args = [
    v8,
    "DESIGNER",
    "/F", ib,
    "/N", "Admin",
    "/RestoreIB", str(dt_file),
    "/DisableStartupDialogs",
    "/DisableStartupMessages",
    "/Out", str(log_restore),
]

result = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
print(f"  Код: {result.returncode}")

if log_restore.exists():
    with open(log_restore, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read().strip()
        if content:
            print(f"  Лог: {content}")
        else:
            print(f"  Лог: (пустой — тихий успех)")

if result.returncode != 0:
    print("ОШИБКА восстановления! Попробуем создать новую базу...")
    
    # Удаляем все файлы из каталога базы
    ib_path = pathlib.Path(ib)
    if ib_path.exists():
        for item in ib_path.iterdir():
            if item.is_file() and item.name.startswith("1Cv8"):
                item.unlink()
                print(f"  Удалён: {item.name}")
            elif item.is_dir():
                pass  # Не трогаем подпапки
    
    # Создаём новую базу
    log_create = log_dir / "create_ib.log"
    args_create = [
        v8,
        "CREATEINFOBASE",
        f'File="{ib}"',
        "/DisableStartupDialogs",
        "/DisableStartupMessages",
        "/Out", str(log_create),
    ]
    
    result2 = subprocess.run(args_create, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
    print(f"  Создание базы: код {result2.returncode}")
    
    # Повторяем восстановление
    result = subprocess.run(args, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=600)
    print(f"  Восстановление: код {result.returncode}")
    
    if log_restore.exists():
        with open(log_restore, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read().strip()
            if content:
                print(f"  Лог: {content}")

print("\n2. Теперь пробуем выгрузку конфигурации (проверка целостности)...")
dump_dir = pathlib.Path(r"D:\Git\Public_Trade_Module\_dump_from_db")
if dump_dir.exists():
    shutil.rmtree(dump_dir)
dump_dir.mkdir(parents=True)

log_dump = log_dir / "dump_test.log"
args_dump = [
    v8,
    "DESIGNER",
    "/F", ib,
    "/N", "Admin",
    "/DumpConfigToFiles", str(dump_dir),
    "/DisableStartupDialogs",
    "/DisableStartupMessages",
    "/Out", str(log_dump),
]

result = subprocess.run(args_dump, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=300)
print(f"  Код: {result.returncode}")

if log_dump.exists():
    with open(log_dump, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read().strip()
        if content:
            print(f"  Лог: {content}")
        else:
            print(f"  Выгрузка успешна (тихий лог)")

# Подсчитываем файлы
if dump_dir.exists():
    files = list(dump_dir.rglob("*"))
    file_count = len([f for f in files if f.is_file()])
    dir_count = len([f for f in files if f.is_dir()])
    print(f"\n  Выгружено: {dir_count} папок, {file_count} файлов")
    
    for item in sorted(dump_dir.iterdir()):
        if item.is_dir():
            sub_count = len(list(item.rglob("*")))
            print(f"    {item.name}/ ({sub_count})")
        else:
            print(f"    {item.name} ({item.stat().st_size} B)")
