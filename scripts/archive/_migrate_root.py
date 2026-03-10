"""
Миграция: все _*.py из корня → scripts/archive/
Исключение: _ptm_analyze.py остаётся в корне.
"""
import os, shutil, glob

ROOT = r'd:\Git\Public_Trade_Module'
ARCHIVE = os.path.join(ROOT, 'scripts', 'archive')

files = sorted(glob.glob(os.path.join(ROOT, '_*.py')))
moved = []
skipped = []

for src in files:
    name = os.path.basename(src)
    if name == '_ptm_analyze.py':
        skipped.append(name)
        continue
    dst = os.path.join(ARCHIVE, name)
    if os.path.exists(dst):
        # Если в архиве уже есть — добавляем суффикс _root
        base, ext = os.path.splitext(name)
        dst = os.path.join(ARCHIVE, f'{base}_root{ext}')
    shutil.move(src, dst)
    moved.append(name)

print(f'Moved to scripts/archive/: {len(moved)} files')
print(f'Skipped (stays in root): {skipped}')
if moved:
    for f in moved:
        print(f'  + {f}')
