# -*- coding: utf-8 -*-
import pathlib
import shutil

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")

copies = [
    # (source, destination)
    (base / "Catalogs" / "Номенклатура" / "Forms" / "ФормаГруппы.xml",
     base / "Проверка" / "Catalogs" / "Номенклатура" / "Forms" / "ФормаГруппы.xml"),
    
    (base / "Catalogs" / "Номенклатура" / "Forms" / "ФормаГруппы" / "Ext" / "Form.xml",
     base / "Проверка" / "Catalogs" / "Номенклатура" / "Forms" / "ФормаГруппы" / "Ext" / "Form.xml"),
    
    (base / "Catalogs" / "Номенклатура" / "Forms" / "ФормаГруппы" / "Ext" / "Form" / "Module.bsl",
     base / "Проверка" / "Catalogs" / "Номенклатура" / "Forms" / "ФормаГруппы" / "Ext" / "Form" / "Module.bsl"),
    
    (base / "Catalogs" / "Номенклатура.xml",
     base / "Проверка" / "Catalogs" / "Номенклатура.xml"),
    
    (base / "ConfigDumpInfo.xml",
     base / "Проверка" / "ConfigDumpInfo.xml"),
]

for src, dst in copies:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.exists():
        shutil.copy2(src, dst)
        print(f"  OK: {src.name} -> {dst.relative_to(base)}")
    else:
        print(f"  MISSING: {src}")

print("\nDone!")
