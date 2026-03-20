"""Compare current config vs backup and show changed files"""
import os, glob

# Use backup that has Конфигурация
backup_dir = r'd:\Git\Public_Trade_Module\_backups\2026-03-20_183603\Конфигурация'
config_dir = r'd:\Git\Public_Trade_Module\Конфигурация'

if not os.path.exists(backup_dir):
    print("Backup not found:", backup_dir)
    exit(1)

backup_files = glob.glob(os.path.join(backup_dir, '**', '*.xml'), recursive=True)
print(f'Files in backup: {len(backup_files)}')

diffs = []
for bfile in backup_files:
    rel = os.path.relpath(bfile, backup_dir)
    cfile = os.path.join(config_dir, rel)
    if os.path.exists(cfile):
        with open(bfile, 'rb') as f:
            bcontent = f.read()
        with open(cfile, 'rb') as f:
            ccontent = f.read()
        if bcontent != ccontent:
            diffs.append(rel)

print(f'Changed files vs backup: {len(diffs)}')
for d in sorted(diffs):
    print(f'  {d}')
