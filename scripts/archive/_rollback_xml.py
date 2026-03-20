"""Restore XML files from backup to sync IB state
Run this to restore old XML which matches the IB state,
then re-apply our changes cleanly.
"""
import os, shutil

backup_dir = r'd:\Git\Public_Trade_Module\_backups\2026-03-20_183603\Конфигурация'
config_dir = r'd:\Git\Public_Trade_Module\Конфигурация'
save_dir = r'd:\Git\Public_Trade_Module\_saved_new_xml'

os.makedirs(save_dir, exist_ok=True)

changed_files = [
    r'Catalogs\НалоговыеГруппы.xml',
    r'Catalogs\Номенклатура.xml',
    r'Catalogs\Номенклатура\Forms\ФормаСписка\Ext\Form.xml',
    r'Catalogs\Номенклатура\Forms\ФормаЭлемента\Ext\Form.xml',
]

for rel in changed_files:
    src = os.path.join(config_dir, rel)
    bsrc = os.path.join(backup_dir, rel)

    if not os.path.exists(bsrc):
        print(f'BACKUP NOT FOUND: {rel}')
        continue

    dst_save = os.path.join(save_dir, os.path.basename(rel) + '.new')
    shutil.copy2(src, dst_save)
    print(f'Saved: {os.path.basename(rel)}.new')

    shutil.copy2(bsrc, src)
    print(f'Restored from backup: {rel}')
    print()

print('Done! Files restored to backup state.')
print(f'New versions saved to: {save_dir}')
