# -*- coding: utf-8 -*-
"""Restore from .bak and re-add ФормаГруппы changes"""
import pathlib
import shutil

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка")

nom_xml = base / "Catalogs" / "Номенклатура.xml"
cdi_xml = base / "ConfigDumpInfo.xml"
nom_bak = nom_xml.with_suffix('.xml.bak')
cdi_bak = cdi_xml.with_suffix('.xml.bak')

# Restore from .bak (which was saved BEFORE revert = our modified version)
if nom_bak.exists():
    shutil.copy2(nom_bak, nom_xml)
    nom_bak.unlink()
    print("Restored Номенклатура.xml from backup (with ФормаГруппы)")
    
if cdi_bak.exists():
    shutil.copy2(cdi_bak, cdi_xml)
    cdi_bak.unlink()
    print("Restored ConfigDumpInfo.xml from backup (with ФормаГруппы)")

# Re-copy form files from source
src_base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")

copies = [
    (src_base / "Catalogs" / "Номенклатура" / "Forms" / "ФормаГруппы.xml",
     base / "Catalogs" / "Номенклатура" / "Forms" / "ФормаГруппы.xml"),
    (src_base / "Catalogs" / "Номенклатура" / "Forms" / "ФормаГруппы" / "Ext" / "Form.xml",
     base / "Catalogs" / "Номенклатура" / "Forms" / "ФормаГруппы" / "Ext" / "Form.xml"),
    (src_base / "Catalogs" / "Номенклатура" / "Forms" / "ФормаГруппы" / "Ext" / "Form" / "Module.bsl",
     base / "Catalogs" / "Номенклатура" / "Forms" / "ФормаГруппы" / "Ext" / "Form" / "Module.bsl"),
]

for src, dst in copies:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.exists():
        shutil.copy2(src, dst)
        print(f"  Copied: {dst.relative_to(base)}")
    else:
        print(f"  MISSING: {src}")

print("\nDone! Проверка restored with ФормаГруппы changes.")
