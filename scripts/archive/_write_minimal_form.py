# -*- coding: utf-8 -*-
import pathlib

form_xml = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация_PTM_Driver_Vchasno\DataProcessors\Вчсн_КассаПанель\Forms\Форма\Ext\Form.xml")

content = """\xef\xbb\xbf<?xml version="1.0" encoding="UTF-8"?>
<Form xmlns="http://v8.1c.ru/8.3/xcf/logform" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:dcscor="http://v8.1c.ru/8.1/data-composition-system/core" xmlns:dcssch="http://v8.1c.ru/8.1/data-composition-system/schema" xmlns:dcsset="http://v8.1c.ru/8.1/data-composition-system/settings" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
\t<AutoCommandBar name="ФормаКоманднаяПанель" id="-1"/>
\t<Attributes>
\t\t<Attribute name="Объект" id="1">
\t\t\t<Type>
\t\t\t\t<v8:Type>cfg:DataProcessorObject.Вчсн_КассаПанель</v8:Type>
\t\t\t</Type>
\t\t\t<MainAttribute>true</MainAttribute>
\t\t\t<SavedData>true</SavedData>
\t\t</Attribute>
\t</Attributes>
</Form>
"""

# Write with CRLF
content_crlf = content.replace("\n", "\r\n")
form_xml.write_bytes(content_crlf.encode("utf-8"))
print(f"Written {form_xml.stat().st_size}B to Form.xml")

# Verify BOM
data = form_xml.read_bytes()
print(f"BOM: {'YES' if data[:3]==b'\\xef\\xbb\\xbf' else 'NO'}")
print(f"CRLF: {'YES' if b'\\r\\n' in data else 'NO'}")
