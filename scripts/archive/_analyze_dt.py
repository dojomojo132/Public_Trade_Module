# -*- coding: utf-8 -*-
"""Анализ .dt файлов в проекте"""
import pathlib

root = pathlib.Path(r'd:\Git\Public_Trade_Module')
dt_files = list(root.rglob('*.dt'))

for f in dt_files:
    size_mb = f.stat().st_size / 1024 / 1024
    rel = f.relative_to(root)
    print(f"  {size_mb:8.1f} MB  {rel}")

print(f"\nВсего: {len(dt_files)} файлов")

if dt_files:
    total = sum(f.stat().st_size for f in dt_files)
    print(f"Общий размер: {total/1024/1024:.1f} MB")

# Also check _backups for .dt
bk_dir = root / '_backups'
if bk_dir.exists():
    dt_in_bk = list(bk_dir.rglob('*.dt'))
    if dt_in_bk:
        total_bk = sum(f.stat().st_size for f in dt_in_bk)
        print(f"\nВ _backups: {len(dt_in_bk)} .dt файлов, {total_bk/1024/1024:.1f} MB")

# Check gitignore for .dt
gitignore = root / '.gitignore'
if gitignore.exists():
    content = gitignore.read_text(encoding='utf-8', errors='ignore')
    if '*.dt' in content or '.dt' in content:
        print("\n.dt в .gitignore: ДА")
    else:
        print("\n.dt в .gitignore: НЕТ (!!)")
