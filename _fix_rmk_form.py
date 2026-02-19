# -*- coding: utf-8 -*-
"""
РМК: 1) Remove ПолеПоискаТовара2 from Form.xml
     2) Add BPO form attributes
     3) Add OnClose + OnCreateAtServer events
     4) Remove АктивироватьПоиск from table events
"""
import pathlib
import re

base = pathlib.Path(r"D:\Git\Public_Trade_Module")

form_xmls = [
    base / "Конфигурация" / "Проверка" / "DataProcessors" / "РабочееМестоКассира" / "Forms" / "Форма" / "Ext" / "Form.xml",
    base / "Конфигурация" / "DataProcessors" / "РабочееМестоКассира" / "Forms" / "Форма" / "Ext" / "Form.xml",
]

for form_xml in form_xmls:
    if not form_xml.exists():
        print(f"  [!] Not found: {form_xml}")
        continue
    
    content = form_xml.read_text(encoding="utf-8")
    folder = "Проверка" if "Проверка" in str(form_xml) else "Конфигурация"
    changes = []
    
    # 1. Remove ПолеПоискаТовара2 InputField block (id=71, context=72, tooltip=73)
    # Pattern: <InputField name="ПолеПоискаТовара2" ...> ... </InputField>
    pattern = r'\s*<InputField name="ПолеПоискаТовара2"[^>]*>.*?</InputField>'
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, '', content, flags=re.DOTALL)
        changes.append("Removed ПолеПоискаТовара2")
    
    # 2. Add OnClose event if missing
    if 'name="OnClose"' not in content:
        content = content.replace(
            '<Event name="NotificationProcessing">ОбработкаОповещения</Event>',
            '<Event name="OnClose">ПриЗакрытии</Event>\n\t\t<Event name="NotificationProcessing">ОбработкаОповещения</Event>'
        )
        changes.append("Added OnClose event")
    
    # 3. Add OnCreateAtServer event if missing  
    if 'name="OnCreateAtServer"' not in content:
        content = content.replace(
            '<Event name="OnOpen">ПриОткрытии</Event>',
            '<Event name="OnCreateAtServer">ПриСозданииНаСервере</Event>\n\t\t<Event name="OnOpen">ПриОткрытии</Event>'
        )
        changes.append("Added OnCreateAtServer event")
    
    # 4. Add BPO form attributes if missing
    if 'ИспользоватьПодключаемоеОборудование' not in content:
        # Find closing </Attributes> or last attribute
        # Add two new attributes
        attr_block = '''
\t\t<Attribute name="ИспользоватьПодключаемоеОборудование" id="100">
\t\t\t<Type>
\t\t\t\t<v8:Type>xs:boolean</v8:Type>
\t\t\t</Type>
\t\t</Attribute>
\t\t<Attribute name="ПоддерживаемыеТипыПодключаемогоОборудования" id="101">
\t\t\t<Type>
\t\t\t\t<v8:Type>xs:string</v8:Type>
\t\t\t\t<v8:StringQualifiers>
\t\t\t\t\t<v8:Length>0</v8:Length>
\t\t\t\t\t<v8:AllowedLength>Variable</v8:AllowedLength>
\t\t\t\t</v8:StringQualifiers>
\t\t\t</Type>
\t\t</Attribute>'''
        
        # Insert before </Attributes>
        content = content.replace('</Attributes>', attr_block + '\n\t</Attributes>')
        changes.append("Added BPO form attributes (ids 100, 101)")
    
    # 5. Remove АктивироватьПоиск from table events (OnActivateRow, OnActivateField, AfterDeleteRow)
    for event_name in ['OnActivateRow', 'OnActivateField', 'AfterDeleteRow']:
        pattern = rf'\s*<Event name="{event_name}">АктивироватьПоиск</Event>'
        if re.search(pattern, content):
            content = re.sub(pattern, '', content)
            changes.append(f"Removed АктивироватьПоиск from {event_name}")
    
    form_xml.write_text(content, encoding="utf-8")
    print(f"  [{folder}] Changes: {', '.join(changes)}")

print("\nDone!")
