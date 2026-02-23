# -*- coding: utf-8 -*-
import shutil
import pathlib

base_src = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\DataProcessors\ИнформацияНоменклатуры")
base_dst = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\DataProcessors\ИнформацияНоменклатуры")

files = [
    "Forms/Форма/Ext/Form.xml",
    "Forms/Форма/Ext/Form/Module.bsl",
]

for f in files:
    src = base_src / f
    dst = base_dst / f
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(src), str(dst))
    print(f"  Synced: {f}")

print("Done!")
