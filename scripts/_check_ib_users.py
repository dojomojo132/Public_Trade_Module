# -*- coding: utf-8 -*-
"""Проверяем авторизацию ИБ - пробуем разные варианты пользователей"""
import subprocess
import pathlib
import sys

IB_PATH = r"D:\Confiq\Public Trade Module"
C1V8 = r"C:\Program Files\1cv8\8.3.27.1814\bin\1cv8.exe"

# Если не нашли 1cv8 - ищем его
if not pathlib.Path(C1V8).exists():
    # Поиск через _find_1cv8.py подход
    for version_dir in sorted(pathlib.Path(r"C:\Program Files\1cv8").glob("*"), reverse=True):
        exe = version_dir / "bin" / "1cv8.exe"
        if exe.exists():
            C1V8 = str(exe)
            break

print(f"1cv8: {C1V8}")
print(f"ИБ: {IB_PATH}")
print()

# Список вариантов авторизации для проверки
variants = [
    ("", ""),           # без авторизации
    ("Admin", ""),      # Admin без пароля
    ("Администратор", ""),  # Администратор без пароля
    ("Админ", ""),      # Админ без пароля
]

log_file = pathlib.Path(r"D:\Git\Public_Trade_Module\logs\_auth_test.log")

for user, password in variants:
    args = [C1V8, "DESIGNER", "/F", IB_PATH]
    if user:
        args += ["/U", user]
    if password is not None:
        args += ["/P", password]
    args += [
        "/DumpIB", r"D:\Git\Public_Trade_Module\logs\_test_auth_dump.dt",
        "/DisableStartupDialogs", "/DisableStartupMessages",
        "/Out", str(log_file)
    ]
    
    user_label = user if user else "(пусто)"
    print(f"Попытка: user={user_label} password='{password}'")
    
    result = subprocess.run(args, capture_output=True, timeout=30)
    
    log_text = ""
    if log_file.exists():
        raw = log_file.read_bytes()
        if raw[:3] == b'\xef\xbb\xbf':
            log_text = raw.decode('utf-8-sig')
        elif raw[:2] == b'\xff\xfe':
            log_text = raw.decode('utf-16')
        else:
            log_text = raw.decode('cp1251', errors='replace')
        log_file.unlink()
    
    print(f"  Exit code: {result.returncode}")
    print(f"  Log: {log_text.strip()[:200]}")
    
    if result.returncode == 0:
        print("  ✓ УСПЕХ!")
        break
    print()
