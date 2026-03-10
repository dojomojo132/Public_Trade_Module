# -*- coding: utf-8 -*-
"""Test: copy ФормаЭлемента's Form.xml and Module.bsl to ФормаГруппы to isolate the problem"""
import pathlib
import shutil

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Catalogs\Номенклатура\Forms")

# Source: working form
src_form = base / "ФормаЭлемента" / "Ext" / "Form.xml"
src_mod = base / "ФормаЭлемента" / "Ext" / "Form" / "Module.bsl"

# Destination: broken form
dst_form = base / "ФормаГруппы" / "Ext" / "Form.xml"
dst_mod = base / "ФормаГруппы" / "Ext" / "Form" / "Module.bsl"

# Backup current ФормаГруппы files
backup_dir = pathlib.Path(r"D:\Git\Public_Trade_Module\_form_temp_backup")
backup_dir.mkdir(exist_ok=True)
if dst_form.exists():
    shutil.copy2(dst_form, backup_dir / "Form.xml.bak")
    print(f"Backed up Form.xml ({dst_form.stat().st_size} bytes)")
if dst_mod.exists():
    shutil.copy2(dst_mod, backup_dir / "Module.bsl.bak")
    print(f"Backed up Module.bsl ({dst_mod.stat().st_size} bytes)")

# Copy ФормаЭлемента files to ФормаГруппы
shutil.copy2(src_form, dst_form)
print(f"\nCopied ФормаЭлемента/Form.xml -> ФормаГруппы/Form.xml ({src_form.stat().st_size} bytes)")
shutil.copy2(src_mod, dst_mod)
print(f"Copied ФормаЭлемента/Module.bsl -> ФормаГруппы/Module.bsl ({src_mod.stat().st_size} bytes)")

print("\nNow try deploy to see if 1C accepts the form with ФормаЭлемента's content")
