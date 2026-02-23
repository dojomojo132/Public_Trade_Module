# -*- coding: utf-8 -*-
"""Fix Form.xml to use compact format (no Properties wrappers)"""
import pathlib

FORM_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<Form xmlns="http://v8.1c.ru/8.3/xcf/logform" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:dcscor="http://v8.1c.ru/8.1/data-composition-system/core" xmlns:dcssch="http://v8.1c.ru/8.1/data-composition-system/schema" xmlns:dcsset="http://v8.1c.ru/8.1/data-composition-system/settings" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
\t<AutoCommandBar name="\u0424\u043e\u0440\u043c\u0430\u041a\u043e\u043c\u0430\u043d\u0434\u043d\u0430\u044f\u041f\u0430\u043d\u0435\u043b\u044c" id="-1">
\t\t<ChildItems>
\t\t\t<Button name="\u0424\u043e\u0440\u043c\u0430\u0421\u0444\u043e\u0440\u043c\u0438\u0440\u043e\u0432\u0430\u0442\u044c" id="1">
\t\t\t\t<Type>CommandBarButton</Type>
\t\t\t\t<CommandName>Form.Command.\u0421\u0444\u043e\u0440\u043c\u0438\u0440\u043e\u0432\u0430\u0442\u044c</CommandName>
\t\t\t\t<DefaultButton>true</DefaultButton>
\t\t\t\t<ExtendedTooltip name="\u0424\u043e\u0440\u043c\u0430\u0421\u0444\u043e\u0440\u043c\u0438\u0440\u043e\u0432\u0430\u0442\u044c\u0420\u0430\u0441\u0448\u0438\u0440\u0435\u043d\u043d\u0430\u044f\u041f\u043e\u0434\u0441\u043a\u0430\u0437\u043a\u0430" id="2"/>
\t\t\t</Button>
\t\t</ChildItems>
\t</AutoCommandBar>
\t<ChildItems>
\t\t<SpreadsheetDocumentField name="\u0420\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u041e\u0442\u0447\u0435\u0442\u0430" id="3">
\t\t\t<DataPath>\u0420\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u041e\u0442\u0447\u0435\u0442\u0430</DataPath>
\t\t\t<HorizontalStretch>true</HorizontalStretch>
\t\t\t<VerticalStretch>true</VerticalStretch>
\t\t\t<ContextMenu name="\u0420\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u041e\u0442\u0447\u0435\u0442\u0430\u041a\u043e\u043d\u0442\u0435\u043a\u0441\u0442\u043d\u043e\u0435\u041c\u0435\u043d\u044e" id="4"/>
\t\t\t<ExtendedTooltip name="\u0420\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u041e\u0442\u0447\u0435\u0442\u0430\u0420\u0430\u0441\u0448\u0438\u0440\u0435\u043d\u043d\u0430\u044f\u041f\u043e\u0434\u0441\u043a\u0430\u0437\u043a\u0430" id="5"/>
\t\t</SpreadsheetDocumentField>
\t</ChildItems>
\t<Attributes>
\t\t<Attribute name="\u041e\u0442\u0447\u0435\u0442" id="1">
\t\t\t<Type>
\t\t\t\t<v8:Type>cfg:ReportObject.\u0421\u043f\u0440\u0430\u0432\u043e\u0447\u043d\u0438\u043a\u041d\u043e\u043c\u0435\u043d\u043a\u043b\u0430\u0442\u0443\u0440\u044b</v8:Type>
\t\t\t</Type>
\t\t\t<MainAttribute>true</MainAttribute>
\t\t</Attribute>
\t\t<Attribute name="\u0420\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u041e\u0442\u0447\u0435\u0442\u0430" id="2">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>\u0420\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<Type>
\t\t\t\t<v8:Type>v8ui:SpreadsheetDocument</v8:Type>
\t\t\t</Type>
\t\t</Attribute>
\t</Attributes>
\t<Commands>
\t\t<Command name="\u0421\u0444\u043e\u0440\u043c\u0438\u0440\u043e\u0432\u0430\u0442\u044c" id="1">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>\u0421\u0444\u043e\u0440\u043c\u0438\u0440\u043e\u0432\u0430\u0442\u044c</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<Action>\u0421\u0444\u043e\u0440\u043c\u0438\u0440\u043e\u0432\u0430\u0442\u044c</Action>
\t\t</Command>
\t</Commands>
</Form>
'''

BASE = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")
COPY = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка")

for base in [BASE, COPY]:
    p = base / "Reports" / "СправочникНоменклатуры" / "Forms" / "ФормаОтчета" / "Ext" / "Form.xml"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(FORM_XML, encoding='utf-8')
    print(f"  OK: {base.name}")

print("\nForm.xml fixed!")
