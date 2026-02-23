# -*- coding: utf-8 -*-
"""Найти все установленные версии 1cv8."""
import pathlib, glob

versions = sorted(
    glob.glob(r"C:\Program Files\1cv8\*\bin\1cv8.exe") +
    glob.glob(r"C:\Program Files (x86)\1cv8\*\bin\1cv8.exe")
)
print("Установленные версии 1cv8.exe:")
for v in versions:
    from packaging.version import Version
    ver_part = pathlib.Path(v).parts[-3]
    print(f"  {ver_part}: {v}")
