# -*- coding: utf-8 -*-
import pathlib
ib = pathlib.Path(r'D:\Confiq\Public Trade Module')
for f in ib.iterdir():
    if f.suffix in ('.dt', '.1CD', '.1CL'):
        print(f"{f.stat().st_size/1024/1024:.1f} MB  {f.name}")
