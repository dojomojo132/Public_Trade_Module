# -*- coding: utf-8 -*-
import pathlib

form_xml = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация_PTM_Driver_Vchasno\DataProcessors\Вчсн_КассаПанель\Forms\Форма\Ext\Form.xml")

content = '<?xml version="1.0" encoding="UTF-8"?>\r\n'
content += '<Form xmlns="http://v8.1c.ru/8.3/xcf/logform" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:dcscor="http://v8.1c.ru/8.1/data-composition-system/core" xmlns:dcssch="http://v8.1c.ru/8.1/data-composition-system/schema" xmlns:dcsset="http://v8.1c.ru/8.1/data-composition-system/settings" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">\r\n'
content += '\t<AutoCommandBar name="\u0424\u043e\u0440\u043c\u0430\u041a\u043e\u043c\u0430\u043d\u0434\u043d\u0430\u044f\u041f\u0430\u043d\u0435\u043b\u044c" id="-1"/>\r\n'
content += '\t<Attributes>\r\n'
content += '\t\t<Attribute name="\u041e\u0431\u044a\u0435\u043a\u0442" id="1">\r\n'
content += '\t\t\t<Type>\r\n'
content += '\t\t\t\t<v8:Type>cfg:DataProcessorObject.\u0412\u0447\u0441\u043d_\u041a\u0430\u0441\u0441\u0430\u041f\u0430\u043d\u0435\u043b\u044c</v8:Type>\r\n'
content += '\t\t\t</Type>\r\n'
content += '\t\t\t<MainAttribute>true</MainAttribute>\r\n'
content += '\t\t\t<SavedData>true</SavedData>\r\n'
content += '\t\t</Attribute>\r\n'
content += '\t</Attributes>\r\n'
content += '</Form>\r\n'

# Write with BOM using utf-8-sig
form_xml.write_text(content, encoding="utf-8-sig", newline="")
print(f"Written {form_xml.stat().st_size}B")

# Verify
data = form_xml.read_bytes()
print(f"BOM: {data[:3] == b'\\xef\\xbb\\xbf'}")

# Also write empty Module.bsl with BOM
mod = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация_PTM_Driver_Vchasno\DataProcessors\Вчсн_КассаПанель\Forms\Форма\Ext\Form\Module.bsl")
mod.write_text("\r\n", encoding="utf-8-sig", newline="")
print(f"Module.bsl: {mod.stat().st_size}B")
