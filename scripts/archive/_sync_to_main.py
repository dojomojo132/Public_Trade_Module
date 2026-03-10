# -*- coding: utf-8 -*-
"""Sync ФормаГруппы files from Проверка (canonical dump) to Конфигурация"""
import pathlib
import shutil

src_base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Catalogs\Номенклатура")
dst_base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Catalogs\Номенклатура")

# Copy form directory
src_form = src_base / "Forms" / "ФормаГруппы"
dst_form = dst_base / "Forms" / "ФормаГруппы"
if dst_form.exists():
    shutil.rmtree(dst_form)
shutil.copytree(src_form, dst_form)
print(f"Synced directory: ФормаГруппы/")

# Copy form descriptor
src_desc = src_base / "Forms" / "ФормаГруппы.xml"
dst_desc = dst_base / "Forms" / "ФормаГруппы.xml"
shutil.copy2(src_desc, dst_desc)
print(f"Synced: ФормаГруппы.xml")

# Copy Номенклатура.xml
src_nom = src_base.parent / "Номенклатура.xml"
dst_nom = dst_base.parent / "Номенклатура.xml"
shutil.copy2(src_nom, dst_nom)
print(f"Synced: Номенклатура.xml")

# Copy ConfigDumpInfo.xml
src_cdi = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\ConfigDumpInfo.xml")
dst_cdi = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\ConfigDumpInfo.xml")
shutil.copy2(src_cdi, dst_cdi)
print(f"Synced: ConfigDumpInfo.xml")

# Copy Configuration.xml
src_cfg = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Configuration.xml")
dst_cfg = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Configuration.xml")
shutil.copy2(src_cfg, dst_cfg)
print(f"Synced: Configuration.xml")

# Copy ObjectModule.bsl too (has the auto-fill logic from earlier)
src_om = src_base / "Ext" / "ObjectModule.bsl"
dst_om = dst_base / "Ext" / "ObjectModule.bsl"
if src_om.exists():
    dst_om.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_om, dst_om)
    print(f"Synced: ObjectModule.bsl")

# Also sync _ДемоТипыШтрихкодов changes
src_demo = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\ChartsOfCharacteristicTypes\_ДемоТипыШтрихкодов")
dst_demo = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\ChartsOfCharacteristicTypes\_ДемоТипыШтрихкодов")
if src_demo.exists() and dst_demo.exists():
    # Only copy Predefined.xml
    pred_src = src_demo / "Predefined.xml"
    pred_dst = dst_demo / "Predefined.xml"
    if pred_src.exists():
        shutil.copy2(pred_src, pred_dst)
        print(f"Synced: _ДемоТипыШтрихкодов/Predefined.xml")

# Sync _ДемоТипыШтрихкодов.xml
src_demo_xml = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\ChartsOfCharacteristicTypes\_ДемоТипыШтрихкодов.xml")
dst_demo_xml = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\ChartsOfCharacteristicTypes\_ДемоТипыШтрихкодов.xml")
if src_demo_xml.exists():
    shutil.copy2(src_demo_xml, dst_demo_xml)
    print(f"Synced: _ДемоТипыШтрихкодов.xml")

print("\nSync complete!")
