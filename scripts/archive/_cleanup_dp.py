# -*- coding: utf-8 -*-
"""Удалить обработку Анл_МассоваяУстановкаНалоговыхГрупп из PTM_Analytics."""
import shutil, os, pathlib

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация_PTM_Analytics")
DP_NAME = "Анл_МассоваяУстановкаНалоговыхГрупп"

# 1. Delete folder and xml
dp_folder = ROOT / "DataProcessors" / DP_NAME
dp_xml = ROOT / "DataProcessors" / f"{DP_NAME}.xml"

for p in [dp_folder, dp_xml]:
    if p.exists():
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
        print(f"Deleted: {p.relative_to(ROOT)}")
    else:
        print(f"Not found: {p.relative_to(ROOT)}")

# Check if DataProcessors folder is now empty (besides other DPs)
dp_dir = ROOT / "DataProcessors"
if dp_dir.exists():
    remaining = list(dp_dir.iterdir())
    print(f"\nRemaining in DataProcessors/: {[x.name for x in remaining]}")
else:
    print("\nDataProcessors/ folder doesn't exist")

print("\nDone!")
