# -*- coding: utf-8 -*-
import subprocess
import pathlib
import sys
import time

# Пути
ib_path = r"D:\Confiq\Public Trade Module"
config_path = r"D:\Git\Public_Trade_Module\Конфигурация"
exe_path = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
log_dir = pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Валидация\logs")

# Создаём папку для логов
log_dir.mkdir(parents=True, exist_ok=True)

def run_1c_command(action_name, args_list, log_name):
    """Запуск команды 1С с логированием"""
    log_path = log_dir / log_name
    
    print(f"\n{'='*60}")
    print(f"[{action_name}]")
    print(f"{'='*60}")
    
    full_args = [exe_path] + args_list + ["/NAdmin", f"/Out{log_path}", "/DisableStartupMessages", "/DisableStartupDialogs"]
    
    print(f"Команда: {' '.join(str(a) for a in full_args[:4])}...")
    
    start_time = time.time()
    result = subprocess.run(full_args, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=180)
    duration = time.time() - start_time
    
    print(f"Завершено за {duration:.1f} сек, код выхода: {result.returncode}")
    
    if log_path.exists():
        with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
            log_content = f.read()
            if log_content.strip():
                print(f"\nВЫВОД 1С:")
                print(log_content)
            else:
                print("(Лог пуст)")
    
    return result.returncode == 0

# Выполняем последовательность команд
success = True

# 1. Загрузка конфигурации
print("\n" + "#"*60)
print("# ЗАГРУЗКА И ОБНОВЛЕНИЕ КОНФИГУРАЦИИ PTM")
print("#"*60)

success = run_1c_command(
    "1. ЗАГРУЗКА КОНФИГУРАЦИИ",
    ["DESIGNER", f"/F{ib_path}", f"/LoadConfigFromFiles{config_path}"],
    "1_load.log"
)

if not success:
    print("\n✗ ОШИБКА при загрузке конфигурации")
    sys.exit(1)

# 2. Обновление БД
success = run_1c_command(
    "2. ОБНОВЛЕНИЕ БД",
    ["DESIGNER", f"/F{ib_path}", "/UpdateDBCfg"],
    "3_updatedb.log"
)

if success:
    print("\n" + "="*60)
    print("✓ УСПЕШНО: Конфигурация загружена и БД обновлена")
    print("="*60)
    sys.exit(0)
else:
    print("\n" + "="*60)
    print("✗ ОШИБКА: Проверьте логи")
    print("="*60)
    sys.exit(1)
