# -*- coding: utf-8 -*-
"""
Полная синхронизация рабочих папок из дампа ИБ.
Заменяет содержимое Конфигурация/ и Конфигурация/Проверка/ файлами из _dump_from_ib/
"""
import pathlib
import shutil

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")
DUMP = ROOT / "_dump_from_ib"
KONFIG = ROOT / "Конфигурация"
PROVERKA = KONFIG / "Проверка"

def sync_folder(src: pathlib.Path, dst: pathlib.Path, label: str):
    """Полная замена dst содержимым src"""
    print(f"\n=== Синхронизация: {label} ===")
    print(f"  Источник: {src}")
    print(f"  Цель:     {dst}")
    
    if not src.exists():
        print(f"  ОШИБКА: источник не найден!")
        return False
    
    # Удаляем целевую папку полностью
    if dst.exists():
        old_files = sum(1 for f in dst.rglob("*") if f.is_file())
        shutil.rmtree(dst)
        print(f"  Удалено: {old_files} старых файлов")
    
    # Копируем из дампа
    shutil.copytree(src, dst)
    new_files = sum(1 for f in dst.rglob("*") if f.is_file())
    print(f"  Скопировано: {new_files} файлов")
    return True

# 1. Синхронизация Проверка (из неё делается деплой)
ok1 = sync_folder(DUMP, PROVERKA, "Конфигурация/Проверка")

# 2. Синхронизация основная Конфигурация
#    Но в основной папке лежит подпапка Проверка — её нужно сохранить
#    Поэтому: удаляем всё из Конфигурация КРОМЕ папки Проверка, потом копируем файлы из дампа
print(f"\n=== Синхронизация: Конфигурация (без Проверка) ===")

# Удаляем всё из Конфигурация кроме Проверка
for item in KONFIG.iterdir():
    if item.name == "Проверка":
        continue
    if item.is_dir():
        shutil.rmtree(item)
    else:
        item.unlink()
print(f"  Очищено (кроме Проверка)")

# Копируем содержимое дампа в Конфигурацию
copied = 0
for item in DUMP.iterdir():
    dst_item = KONFIG / item.name
    if item.is_dir():
        shutil.copytree(item, dst_item)
    else:
        shutil.copy2(item, dst_item)
    copied += 1
    
konfig_files = sum(1 for f in KONFIG.rglob("*") if f.is_file() and "Проверка" not in str(f.relative_to(KONFIG)).split("\\")[0:1])
print(f"  Скопировано: {copied} элементов верхнего уровня")

# Итоговая проверка
print("\n=== ИТОГ ===")
proverka_files = sum(1 for f in PROVERKA.rglob("*") if f.is_file())
konfig_total = sum(1 for f in KONFIG.rglob("*") if f.is_file())
print(f"  Проверка:      {proverka_files} файлов")
print(f"  Конфигурация:  {konfig_total} файлов (включая Проверка)")
print(f"\nСинхронизация завершена!")
