# -*- coding: utf-8 -*-
import pathlib
base = pathlib.Path(r"D:\Git\Public_Trade_Module\Документация\Спецификации")
for f in sorted(base.iterdir()):
    print(f"{f.name}  ({f.stat().st_size} bytes)")
