# -*- coding: utf-8 -*-
"""Check subsystem XML format for CommonTemplate references"""
from pathlib import Path

DEV = Path(r"D:\Git\Public_Trade_Module\Конфигурация")
subsystem_base = DEV / "Subsystems" / "ПоддержкаОборудования" / "Subsystems" / "ПодключаемоеОборудование" / "Subsystems"

# Check one of the removed subsystems
for sub_name in ["ВесовоеОборудование", "ДисплеиПокупателя"]:
    sub_xml = subsystem_base / f"{sub_name}.xml"
    if sub_xml.exists():
        content = sub_xml.read_text(encoding='utf-8-sig')
        lines = content.split('\n')
        print(f"\n=== {sub_name} - lines with 'Драйвер' ===")
        for i, line in enumerate(lines, 1):
            if 'Драйвер' in line:
                print(f"  L{i}: {line.strip()}")

# Also check ОбъектыЛокализации and ОбъектыИсключитьИзМобильной 
for sub_path in DEV.rglob("Subsystems/**/*.xml"):
    if 'ОбъектыЛокализации' in sub_path.stem or 'ОбъектыИсключитьИзМобильной' in sub_path.stem:
        content = sub_path.read_text(encoding='utf-8-sig')
        # Count driver refs
        driver_count = content.count('Драйвер')
        if driver_count > 0:
            rel = sub_path.relative_to(DEV)
            print(f"\n=== {rel} ({driver_count} refs) ===")
            lines = content.split('\n')
            # Show first 3 driver lines
            shown = 0
            for i, line in enumerate(lines, 1):
                if 'Драйвер' in line and shown < 3:
                    print(f"  L{i}: {line.strip()}")
                    shown += 1
