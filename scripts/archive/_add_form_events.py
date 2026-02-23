# -*- coding: utf-8 -*-
"""
Add OnOpen/OnClose events to ПриходТовара Form.xml (both folders)
"""
import pathlib

base_folders = [
    pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка"),
    pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация"),
]

for base in base_folders:
    form_xml = base / "Documents" / "ПриходТовара" / "Forms" / "ФормаДокумента" / "Ext" / "Form.xml"
    if not form_xml.exists():
        print(f"  [SKIP] {form_xml}")
        continue
    
    content = form_xml.read_text(encoding="utf-8")
    
    # Add OnOpen and OnClose events to the Events section
    old_events = '<Event name="NotificationProcessing">ОбработкаОповещения</Event>'
    new_events = (
        '<Event name="NotificationProcessing">ОбработкаОповещения</Event>\n'
        '\t\t<Event name="OnOpen">ПриОткрытии</Event>\n'
        '\t\t<Event name="OnClose">ПриЗакрытии</Event>'
    )
    
    if "OnOpen" in content:
        print(f"  [ALREADY] OnOpen already exists in {form_xml.parent.parent.parent.name}")
        continue
    
    content = content.replace(old_events, new_events, 1)
    form_xml.write_text(content, encoding="utf-8")
    print(f"  [OK] Added OnOpen + OnClose events to {form_xml.relative_to(base)}")

print("\nDone!")
