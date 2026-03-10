# -*- coding: utf-8 -*-
"""Restore Проверка from local backup (before ANY changes)"""
import pathlib
import shutil

backup = pathlib.Path(r"D:\Git\Public_Trade_Module\_backups\2026-02-26_175232\Конфигурация\Проверка")
target = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка")

if not backup.exists():
    print(f"Backup not found: {backup}")
    # List available backups
    backups_dir = pathlib.Path(r"D:\Git\Public_Trade_Module\_backups")
    for d in sorted(backups_dir.iterdir()):
        if d.is_dir():
            proverka = d / "Конфигурация" / "Проверка"
            print(f"  {d.name}: Проверка {'EXISTS' if proverka.exists() else 'MISSING'}")
else:
    # Copy ConfigDumpInfo.xml and Номенклатура.xml from backup
    files = [
        "ConfigDumpInfo.xml",
        "Catalogs/Номенклатура.xml",
    ]
    for f in files:
        src = backup / f
        dst = target / f
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  Restored: {f} ({src.stat().st_size} -> {dst.stat().st_size} bytes)")
        else:
            print(f"  MISSING in backup: {f}")
    
    # Remove ФормаГруппы files if they exist
    form_dir = target / "Catalogs" / "Номенклатура" / "Forms" / "ФормаГруппы"
    form_desc = target / "Catalogs" / "Номенклатура" / "Forms" / "ФормаГруппы.xml"
    if form_dir.exists():
        shutil.rmtree(form_dir)
        print(f"  Removed ФормаГруппы/")
    if form_desc.exists():
        form_desc.unlink()
        print(f"  Removed ФормаГруппы.xml")
    
    # Remove .bak files
    for bak in target.rglob("*.bak"):
        bak.unlink()
        print(f"  Removed: {bak.name}")
    
    print("\nDone! Проверка restored to pre-change state.")
