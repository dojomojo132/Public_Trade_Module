# -*- coding: utf-8 -*-
"""Copy Module.bsl from main config to extension."""
import shutil
import os

src = r"D:\Git\Public_Trade_Module\Конфигурация\DataProcessors\РабочееМестоКассира\Forms\Форма\Ext\Form\Module.bsl"
dst_dir = r"D:\Git\Public_Trade_Module\Конфигурация_PTM_Analytics\DataProcessors\Анл_РабочееМестоКассира\Forms\Форма\Ext\Form"

os.makedirs(dst_dir, exist_ok=True)
dst = os.path.join(dst_dir, "Module.bsl")
shutil.copy2(src, dst)
print(f"OK: {os.path.getsize(dst)} bytes copied to {dst}")
