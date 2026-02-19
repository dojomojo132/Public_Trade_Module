# -*- coding: utf-8 -*-
import pathlib

# Check _ДемоЧек form for ПриСозданииНаСервере setup
base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка")

# Find _ДемоЧек form module
demo_form = base / "Documents" / "_ДемоЧек" / "Forms" / "ФормаДокумента" / "Ext" / "Form" / "Module.bsl"
if demo_form.exists():
    content = demo_form.read_text("utf-8")
    # Search for ПриСозданииНаСервере and equipment setup
    for keyword in ["ПриСозданииНаСервере", "ПодключаемоеОборудование", "МенеджерОборудования", "ИспользоватьПодключаемое"]:
        idx = content.find(keyword)
        if idx >= 0:
            start = max(0, idx - 100)
            end = min(len(content), idx + 300)
            print(f"=== '{keyword}' at {idx} ===")
            print(content[start:end])
            print()
else:
    print(f"Not found: {demo_form}")

# Also check _ДемоШтрихкоды
demo2 = base / "InformationRegisters" / "_ДемоШтрихкоды" / "Forms" / "ФормаЗаписи" / "Ext" / "Form" / "Module.bsl"
if demo2.exists():
    content2 = demo2.read_text("utf-8")
    # Find ПриОткрытии and connection
    print("=" * 80)
    print(f"=== _ДемоШтрихкоды ===")
    idx = content2.find("ПриОткрытии")
    if idx >= 0:
        print(content2[max(0,idx-100):idx+400])
