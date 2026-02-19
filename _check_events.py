# -*- coding: utf-8 -*-
import pathlib

base = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка")
form_xml = base / "Documents" / "ПриходТовара" / "Forms" / "ФормаДокумента" / "Ext" / "Form.xml"

content = form_xml.read_text(encoding="utf-8")

# Find the Events section
events_start = content.find("<Events>")
events_end = content.find("</Events>")
if events_start >= 0 and events_end >= 0:
    events_section = content[events_start:events_end + len("</Events>")]
    print("=== Current Events section ===")
    print(events_section)
    print()

    # Check what events are declared
    for event in ["OnOpen", "OnClose", "BeforeClose", "NotificationProcessing", "OnCreateAtServer", "ChoiceProcessing"]:
        if event in events_section:
            print(f"  [YES] {event}")
        else:
            print(f"  [NO]  {event}")
