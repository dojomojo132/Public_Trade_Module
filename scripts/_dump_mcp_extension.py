# -*- coding: utf-8 -*-
"""
Выгрузка расширения MCP_Сервер из ИБ в файлы на диск.
Затем можно добавить новые обработки и загрузить обратно.
"""
import subprocess
import pathlib
import sys
import os

# Путь к 1cv8.exe — найти последнюю версию
V8_DIR = pathlib.Path(r"C:\Program Files\1cv8")
v8exe = None
if V8_DIR.exists():
    versions = sorted(
        [d for d in V8_DIR.iterdir() if d.is_dir() and d.name[0].isdigit()],
        key=lambda d: d.name,
        reverse=True
    )
    for v in versions:
        candidate = v / "bin" / "1cv8.exe"
        if candidate.exists():
            v8exe = str(candidate)
            break

if not v8exe:
    print("ОШИБКА: 1cv8.exe не найден!")
    sys.exit(1)

print(f"1cv8.exe: {v8exe}")

# Параметры
IB_PATH = r"D:\Confiq\Public Trade Module"
EXTENSION_NAME = "MCP_Сервер"
DUMP_PATH = r"D:\Git\Public_Trade_Module\MCP_Extension"
LOG_PATH = r"D:\Git\Public_Trade_Module\logs\_dump_extension.log"

# Создать папку для выгрузки
pathlib.Path(DUMP_PATH).mkdir(parents=True, exist_ok=True)
pathlib.Path(LOG_PATH).parent.mkdir(parents=True, exist_ok=True)

# Варианты авторизации
auth_variants = [
    ("Админ", ""),
    ("Admin", ""),
    ("", ""),
    ("Админ", "Админ"),
]

result = None
for user, pwd in auth_variants:
    args = [v8exe, "DESIGNER", "/F", IB_PATH]
    if user:
        args += ["/N", user]
    if pwd:
        args += ["/P", pwd]
    args += [
        "/DumpConfigToFiles", DUMP_PATH,
        "-Extension", EXTENSION_NAME,
        "/DisableStartupDialogs", "/DisableStartupMessages",
        "/Out", LOG_PATH
    ]
    
    cred_str = f"User='{user}'" if user else "No credentials"
    print(f"\nПопытка: {cred_str}")
    
    result = subprocess.run(args, capture_output=True, text=True, timeout=120)
    print(f"Exit code: {result.returncode}")
    
    if result.returncode == 0:
        print(f"УСПЕХ с: {cred_str}")
        break
    
    # Прочитать лог для диагностики
    lp = pathlib.Path(LOG_PATH)
    if lp.exists():
        for enc in ['utf-8-sig', 'utf-8', 'cp1251']:
            try:
                log_text = lp.read_text(encoding=enc).strip()
                if log_text:
                    print(f"Лог: {log_text[:200]}")
                    break
            except:
                continue
print(f"Exit code: {result.returncode}")

if result.stdout:
    print(f"STDOUT: {result.stdout}")
if result.stderr:
    print(f"STDERR: {result.stderr}")

# Прочитать лог
log_file = pathlib.Path(LOG_PATH)
if log_file.exists():
    for enc in ['utf-8', 'cp1251', 'utf-8-sig']:
        try:
            content = log_file.read_text(encoding=enc)
            if content.strip():
                print(f"\nЛог ({enc}):")
                print(content)
                break
        except:
            continue

# Показать что выгрузилось
dump_dir = pathlib.Path(DUMP_PATH)
if dump_dir.exists():
    files = list(dump_dir.rglob("*"))
    if files:
        print(f"\nВыгружено файлов: {len([f for f in files if f.is_file()])}")
        for f in sorted(files):
            rel = f.relative_to(dump_dir)
            prefix = "  📁 " if f.is_dir() else "  📄 "
            print(f"{prefix}{rel}")
    else:
        print("\nПапка пуста — выгрузка не удалась.")
else:
    print("\nПапка не создана.")
