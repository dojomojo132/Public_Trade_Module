# -*- coding: utf-8 -*-
"""
Загрузка расширения MCP_Сервер из файлов обратно в ИБ.
Шаги:
1. LoadConfigFromFiles для расширения
2. UpdateDBCfg для расширения
"""
import subprocess
import pathlib
import sys
import os
import time

# Путь к 1cv8.exe
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
EXT_FILES_PATH = r"D:\Git\Public_Trade_Module\MCP_Extension"
LOG_DIR = r"D:\Git\Public_Trade_Module\logs"

os.makedirs(LOG_DIR, exist_ok=True)


def run_1c(description, extra_args, timeout=120):
    """Запускает 1cv8.exe с аргументами и возвращает результат."""
    log_file = os.path.join(LOG_DIR, f"_mcp_ext_{description}.log")
    
    args = [
        v8exe, "DESIGNER",
        "/F", IB_PATH,
        "/N", "Админ",
    ] + extra_args + [
        "/DisableStartupDialogs",
        "/DisableStartupMessages",
        "/Out", log_file
    ]
    
    print(f"\n{'='*60}")
    print(f"[{description}] Запуск...")
    print(f"Команда: {' '.join(args)}")
    
    result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    print(f"Exit code: {result.returncode}")
    
    # Прочитать лог
    lp = pathlib.Path(log_file)
    log_content = ""
    if lp.exists():
        for enc in ['utf-8-sig', 'utf-8', 'cp1251']:
            try:
                log_content = lp.read_text(encoding=enc).strip()
                if log_content:
                    break
            except:
                continue
    
    if log_content:
        print(f"Лог:\n{log_content}")
    else:
        print("Лог: (пусто)")
    
    return result.returncode, log_content


# === ШАГ 1: Загрузка файлов расширения ===
print("\n" + "="*60)
print("ШАГ 1: Загрузка конфигурации расширения из файлов...")
print("="*60)

exit_code, log = run_1c("load_ext", [
    "/LoadConfigFromFiles", EXT_FILES_PATH,
    "-Extension", EXTENSION_NAME,
])

if exit_code != 0:
    print(f"\nОШИБКА загрузки расширения (exit code {exit_code})")
    print("Проверьте лог выше.")
    sys.exit(1)

print("\n✓ Загрузка расширения успешна!")

# === ШАГ 2: Обновление БД расширения ===
print("\n" + "="*60)
print("ШАГ 2: Обновление конфигурации БД для расширения...")
print("="*60)

exit_code, log = run_1c("update_ext_db", [
    "/UpdateDBCfg",
    "-Extension", EXTENSION_NAME,
])

if exit_code != 0:
    print(f"\nОШИБКА обновления БД расширения (exit code {exit_code})")
    print("Проверьте лог выше.")
    sys.exit(1)

print("\n✓ Обновление БД расширения успешно!")

print("\n" + "="*60)
print("ГОТОВО! Расширение MCP_Сервер обновлено.")
print("Новые инструменты:")
print("  - execute_query")
print("  - get_register_data")
print("  - get_document_movements")
print("  - list_enum_values")
print("  - get_predefined_values")
print("="*60)
