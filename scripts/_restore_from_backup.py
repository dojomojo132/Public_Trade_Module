# -*- coding: utf-8 -*-
"""
Восстанавливает все файлы конфигурации из бэкапа до рефакторинга.
Backup: _backups/2026-03-20_224120 (создан "Перед рефакторингом СтавкаНДС/ФОП")
"""
import os
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE = r'd:\Git\Public_Trade_Module'
BACKUP = os.path.join(BASE, '_backups', '2026-03-20_224120')

if not os.path.exists(BACKUP):
    print(f"ОШИБКА: Бэкап не найден: {BACKUP}")
    sys.exit(1)

print(f"Источник: {BACKUP}")
print(f"Назначение: {BASE}")
print()

restored = []
errors = []

for root, dirs, files in os.walk(BACKUP):
    for fname in files:
        src = os.path.join(root, fname)
        rel = os.path.relpath(src, BACKUP)
        dst = os.path.join(BASE, rel)
        
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            restored.append(rel)
            print(f"  [OK] {rel}")
        except Exception as e:
            errors.append((rel, str(e)))
            print(f"  [ERR] {rel}: {e}")

print()
print(f"Восстановлено: {len(restored)} файлов")
if errors:
    print(f"Ошибок: {len(errors)}")
    for rel, err in errors:
        print(f"  {rel}: {err}")
else:
    print("Ошибок нет.")
