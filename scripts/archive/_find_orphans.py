# -*- coding: utf-8 -*-
"""Find ALL orphaned files/dirs in Конфигурация/ that don't belong."""
import os

MAIN_CFG = r"D:\Git\Public_Trade_Module\Конфигурация"

# Walk entire config tree looking for .orphan, .bak files
orphans = []
for root, dirs, files in os.walk(MAIN_CFG):
    for f in files:
        if f.endswith(('.orphan', '.bak', '.bak_ru')):
            orphans.append(os.path.join(root, f))
    for d in dirs:
        if d.endswith(('.orphan',)):
            orphans.append(os.path.join(root, d) + "/")

print(f"Найдено {len(orphans)} осиротевших файлов:")
for p in orphans:
    rel = os.path.relpath(p, MAIN_CFG)
    print(f"  {rel}")
