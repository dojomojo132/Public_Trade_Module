# -*- coding: utf-8 -*-
"""Создать эталон CommonTemplates в _backups/_reference/"""
import pathlib, shutil

ROOT = pathlib.Path(r'd:\Git\Public_Trade_Module')
ct_src = ROOT / 'Конфигурация' / 'CommonTemplates'
ref_dir = ROOT / '_backups' / '_reference'
ct_dst = ref_dir / 'CommonTemplates'

if ct_dst.exists():
    print('Эталон уже существует')
else:
    ref_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ct_src, ct_dst)
    size = sum(f.stat().st_size for f in ct_dst.rglob('*') if f.is_file())
    print(f'Эталон создан: {ct_dst}')
    print(f'Размер: {size/1024/1024:.1f} МБ')
    print(f'Шаблонов: {len([d for d in ct_dst.iterdir() if d.is_dir()])}')
