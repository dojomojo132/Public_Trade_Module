# -*- coding: utf-8 -*-
"""Write full form XML (with all buttons/commands) but keep empty Module.bsl"""
import pathlib

form_xml = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация_PTM_Driver_Vchasno\DataProcessors\Вчсн_КассаПанель\Forms\Форма\Ext\Form.xml")

content = '''\
<?xml version="1.0" encoding="UTF-8"?>
<Form xmlns="http://v8.1c.ru/8.3/xcf/logform" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:dcscor="http://v8.1c.ru/8.1/data-composition-system/core" xmlns:dcssch="http://v8.1c.ru/8.1/data-composition-system/schema" xmlns:dcsset="http://v8.1c.ru/8.1/data-composition-system/settings" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
\t<AutoCommandBar name="\u0424\u043e\u0440\u043c\u0430\u041a\u043e\u043c\u0430\u043d\u0434\u043d\u0430\u044f\u041f\u0430\u043d\u0435\u043b\u044c" id="-1"/>
\t<ChildItems>
\t\t<InputField name="\u041a\u0430\u0441\u0441\u043e\u0432\u043e\u0435\u041e\u0431\u043e\u0440\u0443\u0434\u043e\u0432\u0430\u043d\u0438\u0435" id="1">
\t\t\t<DataPath>\u041a\u0430\u0441\u0441\u043e\u0432\u043e\u0435\u041e\u0431\u043e\u0440\u0443\u0434\u043e\u0432\u0430\u043d\u0438\u0435</DataPath>
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>\u041a\u0430\u0441\u0441\u043e\u0432\u043e\u0435 \u043e\u0431\u043e\u0440\u0443\u0434\u043e\u0432\u0430\u043d\u0438\u0435</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<ContextMenu name="\u041a\u0430\u0441\u0441\u043e\u0432\u043e\u0435\u041e\u0431\u043e\u0440\u0443\u0434\u043e\u0432\u0430\u043d\u0438\u0435\u041a\u043e\u043d\u0442\u0435\u043a\u0441\u0442\u043d\u043e\u0435\u041c\u0435\u043d\u044e" id="2"/>
\t\t\t<ExtendedTooltip name="\u041a\u0430\u0441\u0441\u043e\u0432\u043e\u0435\u041e\u0431\u043e\u0440\u0443\u0434\u043e\u0432\u0430\u043d\u0438\u0435\u0420\u0430\u0441\u0448\u0438\u0440\u0435\u043d\u043d\u0430\u044f\u041f\u043e\u0434\u0441\u043a\u0430\u0437\u043a\u0430" id="3"/>
\t\t</InputField>
\t\t<InputField name="\u0421\u0443\u043c\u043c\u0430" id="4">
\t\t\t<DataPath>\u0421\u0443\u043c\u043c\u0430</DataPath>
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>\u0421\u0443\u043c\u043c\u0430</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<ContextMenu name="\u0421\u0443\u043c\u043c\u0430\u041a\u043e\u043d\u0442\u0435\u043a\u0441\u0442\u043d\u043e\u0435\u041c\u0435\u043d\u044e" id="5"/>
\t\t\t<ExtendedTooltip name="\u0421\u0443\u043c\u043c\u0430\u0420\u0430\u0441\u0448\u0438\u0440\u0435\u043d\u043d\u0430\u044f\u041f\u043e\u0434\u0441\u043a\u0430\u0437\u043a\u0430" id="6"/>
\t\t</InputField>
\t\t<UsualGroup name="\u0413\u0440\u0443\u043f\u043f\u0430\u041a\u043d\u043e\u043f\u043e\u043a" id="7">
\t\t\t<Group>Horizontal</Group>
\t\t\t<Representation>None</Representation>
\t\t\t<ShowTitle>false</ShowTitle>
\t\t\t<ExtendedTooltip name="\u0413\u0440\u0443\u043f\u043f\u0430\u041a\u043d\u043e\u043f\u043e\u043a\u0420\u0430\u0441\u0448\u0438\u0440\u0435\u043d\u043d\u0430\u044f\u041f\u043e\u0434\u0441\u043a\u0430\u0437\u043a\u0430" id="8"/>
\t\t\t<ChildItems>
\t\t\t\t<Button name="\u041e\u0442\u043a\u0440\u044b\u0442\u044c\u0421\u043c\u0435\u043d\u0443" id="9">
\t\t\t\t\t<Type>UsualButton</Type>
\t\t\t\t\t<CommandName>Form.Command.\u041e\u0442\u043a\u0440\u044b\u0442\u044c\u0421\u043c\u0435\u043d\u0443</CommandName>
\t\t\t\t\t<ExtendedTooltip name="\u041e\u0442\u043a\u0440\u044b\u0442\u044c\u0421\u043c\u0435\u043d\u0443\u0420\u0430\u0441\u0448\u0438\u0440\u0435\u043d\u043d\u0430\u044f\u041f\u043e\u0434\u0441\u043a\u0430\u0437\u043a\u0430" id="10"/>
\t\t\t\t</Button>
\t\t\t\t<Button name="X\u041e\u0442\u0447\u0435\u0442" id="11">
\t\t\t\t\t<Type>UsualButton</Type>
\t\t\t\t\t<CommandName>Form.Command.X\u041e\u0442\u0447\u0435\u0442</CommandName>
\t\t\t\t\t<ExtendedTooltip name="X\u041e\u0442\u0447\u0435\u0442\u0420\u0430\u0441\u0448\u0438\u0440\u0435\u043d\u043d\u0430\u044f\u041f\u043e\u0434\u0441\u043a\u0430\u0437\u043a\u0430" id="12"/>
\t\t\t\t</Button>
\t\t\t\t<Button name="Z\u041e\u0442\u0447\u0435\u0442" id="13">
\t\t\t\t\t<Type>UsualButton</Type>
\t\t\t\t\t<CommandName>Form.Command.Z\u041e\u0442\u0447\u0435\u0442</CommandName>
\t\t\t\t\t<ExtendedTooltip name="Z\u041e\u0442\u0447\u0435\u0442\u0420\u0430\u0441\u0448\u0438\u0440\u0435\u043d\u043d\u0430\u044f\u041f\u043e\u0434\u0441\u043a\u0430\u0437\u043a\u0430" id="14"/>
\t\t\t\t</Button>
\t\t\t\t<Button name="\u0412\u043d\u0435\u0441\u0435\u043d\u0438\u0435" id="15">
\t\t\t\t\t<Type>UsualButton</Type>
\t\t\t\t\t<CommandName>Form.Command.\u0412\u043d\u0435\u0441\u0435\u043d\u0438\u0435</CommandName>
\t\t\t\t\t<ExtendedTooltip name="\u0412\u043d\u0435\u0441\u0435\u043d\u0438\u0435\u0420\u0430\u0441\u0448\u0438\u0440\u0435\u043d\u043d\u0430\u044f\u041f\u043e\u0434\u0441\u043a\u0430\u0437\u043a\u0430" id="16"/>
\t\t\t\t</Button>
\t\t\t\t<Button name="\u0418\u0437\u044a\u044f\u0442\u0438\u0435" id="17">
\t\t\t\t\t<Type>UsualButton</Type>
\t\t\t\t\t<CommandName>Form.Command.\u0418\u0437\u044a\u044f\u0442\u0438\u0435</CommandName>
\t\t\t\t\t<ExtendedTooltip name="\u0418\u0437\u044a\u044f\u0442\u0438\u0435\u0420\u0430\u0441\u0448\u0438\u0440\u0435\u043d\u043d\u0430\u044f\u041f\u043e\u0434\u0441\u043a\u0430\u0437\u043a\u0430" id="18"/>
\t\t\t\t</Button>
\t\t\t</ChildItems>
\t\t</UsualGroup>
\t\t<LabelField name="\u0421\u0442\u0440\u043e\u043a\u0430\u0421\u0442\u0430\u0442\u0443\u0441\u0430" id="19">
\t\t\t<DataPath>\u0421\u0442\u0440\u043e\u043a\u0430\u0421\u0442\u0430\u0442\u0443\u0441\u0430</DataPath>
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>\u0421\u0442\u0430\u0442\u0443\u0441</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<ContextMenu name="\u0421\u0442\u0440\u043e\u043a\u0430\u0421\u0442\u0430\u0442\u0443\u0441\u0430\u041a\u043e\u043d\u0442\u0435\u043a\u0441\u0442\u043d\u043e\u0435\u041c\u0435\u043d\u044e" id="20"/>
\t\t\t<ExtendedTooltip name="\u0421\u0442\u0440\u043e\u043a\u0430\u0421\u0442\u0430\u0442\u0443\u0441\u0430\u0420\u0430\u0441\u0448\u0438\u0440\u0435\u043d\u043d\u0430\u044f\u041f\u043e\u0434\u0441\u043a\u0430\u0437\u043a\u0430" id="21"/>
\t\t</LabelField>
\t</ChildItems>
\t<Attributes>
\t\t<Attribute name="\u041e\u0431\u044a\u0435\u043a\u0442" id="100">
\t\t\t<Type>
\t\t\t\t<v8:Type>cfg:DataProcessorObject.\u0412\u0447\u0441\u043d_\u041a\u0430\u0441\u0441\u0430\u041f\u0430\u043d\u0435\u043b\u044c</v8:Type>
\t\t\t</Type>
\t\t\t<MainAttribute>true</MainAttribute>
\t\t\t<SavedData>true</SavedData>
\t\t</Attribute>
\t\t<Attribute name="\u041a\u0430\u0441\u0441\u043e\u0432\u043e\u0435\u041e\u0431\u043e\u0440\u0443\u0434\u043e\u0432\u0430\u043d\u0438\u0435" id="101">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>\u041a\u0430\u0441\u0441\u043e\u0432\u043e\u0435 \u043e\u0431\u043e\u0440\u0443\u0434\u043e\u0432\u0430\u043d\u0438\u0435</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<Type>
\t\t\t\t<v8:Type>cfg:CatalogRef.\u041a\u0430\u0441\u0441\u043e\u0432\u043e\u0435\u041e\u0431\u043e\u0440\u0443\u0434\u043e\u0432\u0430\u043d\u0438\u0435</v8:Type>
\t\t\t</Type>
\t\t</Attribute>
\t\t<Attribute name="\u0421\u0443\u043c\u043c\u0430" id="102">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>\u0421\u0443\u043c\u043c\u0430</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<Type>
\t\t\t\t<v8:Type>xs:decimal</v8:Type>
\t\t\t\t<v8:NumberQualifiers>
\t\t\t\t\t<v8:Digits>15</v8:Digits>
\t\t\t\t\t<v8:FractionDigits>2</v8:FractionDigits>
\t\t\t\t\t<v8:AllowedSign>Any</v8:AllowedSign>
\t\t\t\t</v8:NumberQualifiers>
\t\t\t</Type>
\t\t</Attribute>
\t\t<Attribute name="\u0421\u0442\u0440\u043e\u043a\u0430\u0421\u0442\u0430\u0442\u0443\u0441\u0430" id="103">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>\u0421\u0442\u0430\u0442\u0443\u0441</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<Type>
\t\t\t\t<v8:Type>xs:string</v8:Type>
\t\t\t\t<v8:StringQualifiers>
\t\t\t\t\t<v8:Length>0</v8:Length>
\t\t\t\t\t<v8:AllowedLength>Variable</v8:AllowedLength>
\t\t\t\t</v8:StringQualifiers>
\t\t\t</Type>
\t\t</Attribute>
\t</Attributes>
\t<Commands>
\t\t<Command name="\u041e\u0442\u043a\u0440\u044b\u0442\u044c\u0421\u043c\u0435\u043d\u0443" id="1">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>\u041e\u0442\u043a\u0440\u044b\u0442\u044c \u0441\u043c\u0435\u043d\u0443</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<Action>\u041e\u0442\u043a\u0440\u044b\u0442\u044c\u0421\u043c\u0435\u043d\u0443</Action>
\t\t</Command>
\t\t<Command name="X\u041e\u0442\u0447\u0435\u0442" id="2">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>X-\u043e\u0442\u0447\u0435\u0442</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<Action>X\u041e\u0442\u0447\u0435\u0442</Action>
\t\t</Command>
\t\t<Command name="Z\u041e\u0442\u0447\u0435\u0442" id="3">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Z-\u043e\u0442\u0447\u0435\u0442 (\u0437\u0430\u043a\u0440\u044b\u0442\u044c \u0441\u043c\u0435\u043d\u0443)</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<Action>Z\u041e\u0442\u0447\u0435\u0442</Action>
\t\t</Command>
\t\t<Command name="\u0412\u043d\u0435\u0441\u0435\u043d\u0438\u0435" id="4">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>\u0412\u043d\u0435\u0441\u0435\u043d\u0438\u0435</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<Action>\u0412\u043d\u0435\u0441\u0435\u043d\u0438\u0435</Action>
\t\t</Command>
\t\t<Command name="\u0418\u0437\u044a\u044f\u0442\u0438\u0435" id="5">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>\u0418\u0437\u044a\u044f\u0442\u0438\u0435</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<Action>\u0418\u0437\u044a\u044f\u0442\u0438\u0435</Action>
\t\t</Command>
\t</Commands>
</Form>
'''

# Write with BOM + CRLF
content_crlf = content.replace("\n", "\r\n")
form_xml.write_text(content_crlf, encoding="utf-8-sig", newline="")
print(f"Written {form_xml.stat().st_size}B - full form XML with empty Module.bsl")
