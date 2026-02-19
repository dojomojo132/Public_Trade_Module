# -*- coding: utf-8 -*-
"""
Восстановление ТОЛЬКО новых файлов БПО из коммита f8d6d1a,
без затрагивания модифицированных PTM-объектов.
"""
import subprocess
import os

os.chdir(r"D:\Git\Public_Trade_Module")
os.environ["GIT_CONFIG_PARAMETERS"] = "'core.quotePath=false'"

# 1. Получить список ТОЛЬКО добавленных файлов (не модифицированных)
result = subprocess.run(
    ["git", "diff", "--diff-filter=A", "--name-only", "960be69", "f8d6d1a"],
    capture_output=True, encoding="utf-8", errors="replace"
)
added_files = [f for f in result.stdout.strip().split('\n') if f]

# Фильтрируем - только файлы конфигурации (без Проверка/ - восстановим отдельно)
config_files = [f for f in added_files if f.startswith('Конфигурация/') and '/Проверка/' not in f]

print(f"Всего добавлённых файлов: {len(added_files)}")
print(f"Файлов конфигурации (без Проверка/): {len(config_files)}")

# Исключаем Configuration.xml и ConfigDumpInfo.xml - мерджим вручную
excluded = ['Конфигурация/Configuration.xml', 'Конфигурация/ConfigDumpInfo.xml']
files_to_restore = [f for f in config_files if f not in excluded]

print(f"Файлов к восстановлению: {len(files_to_restore)}")

# 2. Восстановление через git checkout
print("\n=== ВОССТАНОВЛЕНИЕ ФАЙЛОВ ===")
batch_size = 50
total = len(files_to_restore)
errors = []
success = 0

for i in range(0, total, batch_size):
    batch = files_to_restore[i:i+batch_size]
    result = subprocess.run(
        ["git", "checkout", "f8d6d1a", "--"] + batch,
        capture_output=True, encoding="utf-8", errors="replace"
    )
    if result.returncode != 0:
        # Попробуем по одному
        for f in batch:
            r = subprocess.run(
                ["git", "checkout", "f8d6d1a", "--", f],
                capture_output=True, encoding="utf-8", errors="replace"
            )
            if r.returncode != 0:
                errors.append(f"ОШИБКА: {f} - {r.stderr.strip()}")
            else:
                success += 1
    else:
        success += len(batch)
    
    pct = min(100, int((i + len(batch)) / total * 100))
    print(f"  Прогресс: {pct}% ({success} / {total})")

print(f"\n=== ИТОГ ===")
print(f"Восстановлено: {success}")
print(f"Ошибок: {len(errors)}")
for e in errors:
    print(f"  {e}")

# 3. Теперь копируем те же файлы в Проверка/
print("\n=== КОПИРОВАНИЕ В ПРОВЕРКА/ ===")
import shutil
import pathlib

proverka_success = 0
proverka_errors = []

for f in files_to_restore:
    # f = "Конфигурация/CommonModules/МодульXYZ.xml"
    src = pathlib.Path(r"D:\Git\Public_Trade_Module") / f
    # Целевой путь: заменить "Конфигурация/" на "Конфигурация/Проверка/"
    rel = f.replace('Конфигурация/', '', 1)
    dst = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка") / rel
    
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src), str(dst))
        proverka_success += 1
    except Exception as ex:
        proverka_errors.append(f"ОШИБКА: {rel} - {ex}")

print(f"Скопировано в Проверка/: {proverka_success}")
print(f"Ошибок: {len(proverka_errors)}")
for e in proverka_errors[:10]:
    print(f"  {e}")

print("\n=== ГОТОВО ===")
print(f"Файлы БПО восстановлены. Следующий шаг: мердж Configuration.xml и ConfigDumpInfo.xml")
