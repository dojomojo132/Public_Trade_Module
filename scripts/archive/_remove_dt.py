# -*- coding: utf-8 -*-
"""Удаление устаревших .dt файлов из проекта"""
import pathlib

root = pathlib.Path(r'd:\Git\Public_Trade_Module')
dt_files = list(root.rglob('*.dt'))

total_freed = 0
for f in dt_files:
    size = f.stat().st_size
    total_freed += size
    f.unlink()
    print(f"  Удалён: {f.relative_to(root)}  ({size/1024/1024:.1f} MB)")

print(f"\nУдалено: {len(dt_files)} файлов")
print(f"Освобождено: {total_freed/1024/1024:.0f} MB ({total_freed/1024/1024/1024:.1f} GB)")
