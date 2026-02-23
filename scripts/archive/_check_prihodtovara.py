# -*- coding: utf-8 -*-
import pathlib

# Check if ПриСозданииНаСервере exists in module
f = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Documents\ПриходТовара\Forms\ФормаДокумента\Ext\Form\Module.bsl")
content = f.read_text("utf-8")

for keyword in ["ПриСозданииНаСервере", "НаСервере", "ИспользоватьПодключаемоеОборудование"]:
    idx = content.find(keyword)
    if idx >= 0:
        print(f"Found '{keyword}' at {idx}")
        print(content[max(0,idx-100):idx+200])
        print()
    else:
        print(f"NOT FOUND: '{keyword}'")

# Check Form.xml for existing attributes
form_xml = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Documents\ПриходТовара\Forms\ФормаДокумента\Ext\Form.xml")
xml_content = form_xml.read_text("utf-8")

for keyword in ["ИспользоватьПодключаемоеОборудование", "ПоддерживаемыеТипыПодключаемогоОборудования", "ПодключаемоеОборудованиеБПО", "Attributes"]:
    idx = xml_content.find(keyword)
    if idx >= 0:
        print(f"\nXML: Found '{keyword}' at {idx}")
        print(xml_content[max(0,idx-100):idx+200])
    else:
        print(f"\nXML: NOT FOUND: '{keyword}'")
