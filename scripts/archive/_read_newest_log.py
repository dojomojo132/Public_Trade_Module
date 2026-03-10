# -*- coding: utf-8 -*-
"""Читаем лог самого деплой-скрипта."""
import pathlib, time

# Проверяем лог деплой-скрипта (не 1С, а PowerShell deploy)
ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")

# Смотрим все логи за сегодня, отсортированные по дате
LOGS = ROOT / "Документация" / "Валидация" / "logs"
all_logs = sorted(LOGS.glob("*.log"), key=lambda f: f.stat().st_mtime)

# Показываем самые новые
print(f"Всего логов: {len(all_logs)}")
print("Последние 8 файлов:")
for log in all_logs[-8:]:
    mtime = time.ctime(log.stat().st_mtime)
    size = log.stat().st_size
    print(f"  {log.name} ({size}b) - {mtime}")

# Читаем самый новый лог
print()
newest = all_logs[-1]
print(f"=== САМЫЙ НОВЫЙ ЛОГ: {newest.name} ===")
try:
    content = newest.read_bytes().decode("utf-8-sig")
except:
    content = newest.read_bytes().decode("cp1251", errors="replace")
print(content[:3000])

# Проверяем наличие deploy-log в корне
deploy_log = ROOT / "_deploy_log.txt"
if deploy_log.exists():
    mtime = time.ctime(deploy_log.stat().st_mtime)
    size = deploy_log.stat().st_size
    print(f"\n=== {deploy_log.name} ({size}b, {mtime}) ===")
    try:
        txt = deploy_log.read_bytes().decode("utf-8", errors="replace")
    except:
        txt = deploy_log.read_bytes().decode("cp1251", errors="replace")
    # Последние 3000 символов
    if len(txt) > 3000:
        print("... (показано последние 3000 символов)")
        print(txt[-3000:])
    else:
        print(txt)
