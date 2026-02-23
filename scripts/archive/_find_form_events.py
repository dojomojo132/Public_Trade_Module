# -*- coding: utf-8 -*-
import pathlib

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка")
form_xml = base / "Documents" / "ПриходТовара" / "Forms" / "ФормаДокумента" / "Ext" / "Form.xml"

if form_xml.exists():
    content = form_xml.read_text(encoding="utf-8")
    # Search for event handlers
    for keyword in ["ПриОткрытии", "ПриЗакрытии", "ОбработкаОповещения", "Handlers", "OnOpen", "OnClose", "NotificationProcessing"]:
        idx = content.find(keyword)
        if idx >= 0:
            start = max(0, idx - 100)
            end = min(len(content), idx + 200)
            print(f"=== Found '{keyword}' at position {idx} ===")
            print(content[start:end])
            print()
    
    # Show first 200 chars to see structure
    print("=== Form XML structure (first 500 chars) ===")
    print(content[:500])
else:
    print(f"File not found: {form_xml}")
