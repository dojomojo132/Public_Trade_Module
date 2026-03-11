# -*- coding: utf-8 -*-
"""Замер производительности восстановления из бэкапа"""
import pathlib, time, shutil, sys

ROOT = pathlib.Path(r'd:\Git\Public_Trade_Module')
BK_DIR = ROOT / '_backups'
REF_DIR = BK_DIR / '_reference'
TEMP_DIR = ROOT / '_backups' / '_test_restore'

# Найти бэкапы
all_bk = sorted([d for d in BK_DIR.iterdir() if d.is_dir() and d.name.startswith('2026')])
old_bk = None
new_bk = None
for d in all_bk:
    ct = d / 'Конфигурация' / 'CommonTemplates'
    if ct.exists():
        old_bk = d
    else:
        new_bk = d

print("=== Замер восстановления из бэкапа ===\n")

# --- СТАРЫЙ бэкап ---
if old_bk:
    files_old = [f for f in old_bk.rglob('*') if f.is_file()]
    size_old = sum(f.stat().st_size for f in files_old)
    print(f"СТАРЫЙ бэкап: {old_bk.name}")
    print(f"  Файлов: {len(files_old)}")
    print(f"  Размер: {size_old/1024/1024:.0f} МБ")
    
    # Замер копирования
    dst = TEMP_DIR / 'old'
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    
    t0 = time.perf_counter()
    shutil.copytree(old_bk / 'Конфигурация', dst / 'Конфигурация')
    t1 = time.perf_counter()
    old_time = t1 - t0
    print(f"  Время копирования Конфигурация/: {old_time:.1f} сек")
    
    # Cleanup
    shutil.rmtree(dst)

# --- НОВЫЙ бэкап ---
if new_bk:
    files_new = [f for f in new_bk.rglob('*') if f.is_file()]
    size_new = sum(f.stat().st_size for f in files_new)
    print(f"\nНОВЫЙ бэкап: {new_bk.name}")
    print(f"  Файлов: {len(files_new)}")
    print(f"  Размер: {size_new/1024/1024:.0f} МБ")
    
    dst = TEMP_DIR / 'new'
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    
    # Шаг 1: копирование бэкапа
    t0 = time.perf_counter()
    shutil.copytree(new_bk / 'Конфигурация', dst / 'Конфигурация')
    t1 = time.perf_counter()
    step1 = t1 - t0
    print(f"  Шаг 1 (копирование бэкапа): {step1:.1f} сек")
    
    # Шаг 2: восстановление CommonTemplates из эталона
    ct_ref = REF_DIR / 'CommonTemplates'
    if ct_ref.exists():
        t2 = time.perf_counter()
        shutil.copytree(ct_ref, dst / 'Конфигурация' / 'CommonTemplates')
        t3 = time.perf_counter()
        step2 = t3 - t2
        print(f"  Шаг 2 (CommonTemplates из эталона): {step2:.1f} сек")
    else:
        step2 = 0
        print(f"  Шаг 2: эталон не найден")
    
    new_time = step1 + step2
    print(f"  ИТОГО время: {new_time:.1f} сек")
    
    # Cleanup
    shutil.rmtree(dst)

# Cleanup temp dir
if TEMP_DIR.exists():
    shutil.rmtree(TEMP_DIR)

# --- СРАВНЕНИЕ ---
print("\n=== СРАВНЕНИЕ ===")
if old_bk and new_bk:
    print(f"  Старый: {size_old/1024/1024:.0f} МБ / {old_time:.1f} сек")
    print(f"  Новый:  {size_new/1024/1024:.0f} МБ / {new_time:.1f} сек (+ эталон)")
    if old_time > 0:
        print(f"  Ускорение: {old_time/new_time:.1f}x")
    print(f"  Экономия места: {(size_old - size_new)/1024/1024:.0f} МБ на бэкап")
