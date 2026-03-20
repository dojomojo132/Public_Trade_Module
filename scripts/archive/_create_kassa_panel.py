# -*- coding: utf-8 -*-
"""Создание обработки Вчсн_КассаПанель в расширении PTM_Driver_Vchasno"""

import pathlib
import secrets

BOM = b'\xef\xbb\xbf'
BASE = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация_PTM_Driver_Vchasno")
DP_DIR = BASE / "DataProcessors" / "Вчсн_КассаПанель"

DP_UUID = "2883ee47-4938-49f5-9e22-ecdc7da45143"
FORM_UUID = "f0187071-42d3-41f9-829a-72619dd94cb3"


def cv():
    return secrets.token_hex(16) + "00000000"


def write_bom(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    content = content.replace('\r\n', '\n').replace('\n', '\r\n')
    path.write_bytes(BOM + content.encode('utf-8'))
    print(f"  ✓ BOM {path.relative_to(BASE)}")


def write_utf8(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    content = content.replace('\r\n', '\n').replace('\n', '\r\n')
    path.write_bytes(content.encode('utf-8'))
    print(f"  ✓     {path.relative_to(BASE)}")


# === 1. DataProcessor объект XML ===
dp_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
\t<DataProcessor uuid="{DP_UUID}">
\t\t<Properties>
\t\t\t<Name>Вчсн_КассаПанель</Name>
\t\t\t<Synonym>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Панель управления кассой</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Synonym>
\t\t\t<Comment/>
\t\t\t<UseStandardCommands>true</UseStandardCommands>
\t\t\t<DefaultForm>DataProcessor.Вчсн_КассаПанель.Form.Форма</DefaultForm>
\t\t\t<AuxiliaryForm/>
\t\t\t<IncludeHelpInContents>false</IncludeHelpInContents>
\t\t\t<ExtendedPresentation/>
\t\t\t<Explanation/>
\t\t</Properties>
\t\t<ChildObjects>
\t\t\t<Form>Форма</Form>
\t\t</ChildObjects>
\t</DataProcessor>
</MetaDataObject>
'''

# === 2. ObjectModule.bsl (пустой) ===
obj_bsl = ""

# === 3. Дескриптор формы (Forms/Форма.xml) ===
form_descriptor = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
\t<Form uuid="{FORM_UUID}" owner="{DP_UUID}">
\t\t<Properties>
\t\t\t<Name>Форма</Name>
\t\t\t<Synonym>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Форма</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Synonym>
\t\t\t<Comment/>
\t\t\t<FormType>Managed</FormType>
\t\t\t<IncludeHelpInContents>false</IncludeHelpInContents>
\t\t\t<UsePurposes>
\t\t\t\t<v8:Value xsi:type="app:ApplicationUsePurpose">PlatformApplication</v8:Value>
\t\t\t</UsePurposes>
\t\t\t<ExtendedPresentation/>
\t\t</Properties>
\t</Form>
</MetaDataObject>
'''

# === 4. Form.xml (BOM + CRLF) ===
form_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<Form xmlns="http://v8.1c.ru/8.3/xcf/logform" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:dcscor="http://v8.1c.ru/8.1/data-composition-system/core" xmlns:dcssch="http://v8.1c.ru/8.1/data-composition-system/schema" xmlns:dcsset="http://v8.1c.ru/8.1/data-composition-system/settings" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
\t<AutoCommandBar name="ФормаКоманднаяПанель" id="-1"/>
\t<Events>
\t\t<Event name="OnCreateAtServer">ПриСозданииНаСервере</Event>
\t</Events>
\t<ChildItems>
\t\t<InputField name="КассовоеОборудование" id="1">
\t\t\t<DataPath>КассовоеОборудование</DataPath>
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Кассовое оборудование</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<ContextMenu name="КассовоеОборудованиеКонтекстноеМеню" id="2"/>
\t\t\t<ExtendedTooltip name="КассовоеОборудованиеРасширеннаяПодсказка" id="3"/>
\t\t</InputField>
\t\t<InputField name="Сумма" id="4">
\t\t\t<DataPath>Сумма</DataPath>
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Сумма</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<ContextMenu name="СуммаКонтекстноеМеню" id="5"/>
\t\t\t<ExtendedTooltip name="СуммаРасширеннаяПодсказка" id="6"/>
\t\t</InputField>
\t\t<UsualGroup name="ГруппаКнопок" id="7">
\t\t\t<Group>Horizontal</Group>
\t\t\t<ContextMenu name="ГруппаКнопокКонтекстноеМеню" id="8"/>
\t\t\t<ExtendedTooltip name="ГруппаКнопокРасширеннаяПодсказка" id="9"/>
\t\t\t<ChildItems>
\t\t\t\t<Button name="ОткрытьСмену" id="10">
\t\t\t\t\t<Type>UsualButton</Type>
\t\t\t\t\t<CommandName>ОткрытьСмену</CommandName>
\t\t\t\t\t<Title>
\t\t\t\t\t\t<v8:item>
\t\t\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t\t\t<v8:content>Открыть смену</v8:content>
\t\t\t\t\t\t</v8:item>
\t\t\t\t\t</Title>
\t\t\t\t\t<ExtendedTooltip name="ОткрытьСменуРасширеннаяПодсказка" id="11"/>
\t\t\t\t</Button>
\t\t\t\t<Button name="XОтчет" id="12">
\t\t\t\t\t<Type>UsualButton</Type>
\t\t\t\t\t<CommandName>XОтчет</CommandName>
\t\t\t\t\t<Title>
\t\t\t\t\t\t<v8:item>
\t\t\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t\t\t<v8:content>X-отчет</v8:content>
\t\t\t\t\t\t</v8:item>
\t\t\t\t\t</Title>
\t\t\t\t\t<ExtendedTooltip name="XОтчетРасширеннаяПодсказка" id="13"/>
\t\t\t\t</Button>
\t\t\t\t<Button name="ZОтчет" id="14">
\t\t\t\t\t<Type>UsualButton</Type>
\t\t\t\t\t<CommandName>ZОтчет</CommandName>
\t\t\t\t\t<Title>
\t\t\t\t\t\t<v8:item>
\t\t\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t\t\t<v8:content>Z-отчет (закрыть смену)</v8:content>
\t\t\t\t\t\t</v8:item>
\t\t\t\t\t</Title>
\t\t\t\t\t<ExtendedTooltip name="ZОтчетРасширеннаяПодсказка" id="15"/>
\t\t\t\t</Button>
\t\t\t\t<Button name="Внесение" id="16">
\t\t\t\t\t<Type>UsualButton</Type>
\t\t\t\t\t<CommandName>Внесение</CommandName>
\t\t\t\t\t<Title>
\t\t\t\t\t\t<v8:item>
\t\t\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t\t\t<v8:content>Внесение</v8:content>
\t\t\t\t\t\t</v8:item>
\t\t\t\t\t</Title>
\t\t\t\t\t<ExtendedTooltip name="ВнесениеРасширеннаяПодсказка" id="17"/>
\t\t\t\t</Button>
\t\t\t\t<Button name="Изъятие" id="18">
\t\t\t\t\t<Type>UsualButton</Type>
\t\t\t\t\t<CommandName>Изъятие</CommandName>
\t\t\t\t\t<Title>
\t\t\t\t\t\t<v8:item>
\t\t\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t\t\t<v8:content>Изъятие</v8:content>
\t\t\t\t\t\t</v8:item>
\t\t\t\t\t</Title>
\t\t\t\t\t<ExtendedTooltip name="ИзъятиеРасширеннаяПодсказка" id="19"/>
\t\t\t\t</Button>
\t\t\t</ChildItems>
\t\t</UsualGroup>
\t\t<LabelField name="СтрокаСтатуса" id="20">
\t\t\t<DataPath>СтрокаСтатуса</DataPath>
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Статус</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<ReadOnly>true</ReadOnly>
\t\t\t<ContextMenu name="СтрокаСтатусаКонтекстноеМеню" id="21"/>
\t\t\t<ExtendedTooltip name="СтрокаСтатусаРасширеннаяПодсказка" id="22"/>
\t\t</LabelField>
\t</ChildItems>
\t<Attributes>
\t\t<Attribute name="Объект" id="100">
\t\t\t<Type>
\t\t\t\t<v8:Type>cfg:DataProcessorObject.Вчсн_КассаПанель</v8:Type>
\t\t\t</Type>
\t\t\t<MainAttribute>true</MainAttribute>
\t\t\t<SavedData>true</SavedData>
\t\t</Attribute>
\t\t<Attribute name="КассовоеОборудование" id="101">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Кассовое оборудование</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<Type>
\t\t\t\t<v8:Type>cfg:CatalogRef.КассовоеОборудование</v8:Type>
\t\t\t</Type>
\t\t</Attribute>
\t\t<Attribute name="Сумма" id="102">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Сумма</v8:content>
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
\t\t<Attribute name="СтрокаСтатуса" id="103">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Статус</v8:content>
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
\t\t<Command name="ОткрытьСмену" id="1">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Открыть смену</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<Action>ОткрытьСмену</Action>
\t\t</Command>
\t\t<Command name="XОтчет" id="2">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>X-отчет</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<Action>XОтчет</Action>
\t\t</Command>
\t\t<Command name="ZОтчет" id="3">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Z-отчет</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<Action>ZОтчет</Action>
\t\t</Command>
\t\t<Command name="Внесение" id="4">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Внесение</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<Action>Внесение</Action>
\t\t</Command>
\t\t<Command name="Изъятие" id="5">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Изъятие</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<Action>Изъятие</Action>
\t\t</Command>
\t</Commands>
</Form>
'''

# === 5. Module.bsl (BOM + CRLF) ===
module_bsl = '''#Область ОбработчикиСобытийФормы

&НаСервере
Процедура ПриСозданииНаСервере(Отказ, СтандартнаяОбработка)
\tКассовоеОборудование = Справочники.КассовоеОборудование.ПустаяСсылка();
КонецПроцедуры

#КонецОбласти

#Область ОбработчикиКомандФормы

&НаКлиенте
Процедура ОткрытьСмену(Команда)
\tРезультатСервер = ОткрытьСменуНаСервере();
\tПоказатьСтатус(РезультатСервер);
КонецПроцедуры

&НаСервере
Функция ОткрытьСменуНаСервере()
\tРез = ВызватьОперациюПРРО(0);
\tВозврат Рез;
КонецФункции

&НаКлиенте
Процедура XОтчет(Команда)
\tРез = XОтчетНаСервере();
\tПоказатьСтатус(Рез);
КонецПроцедуры

&НаСервере
Функция XОтчетНаСервере()
\tВозврат ВызватьОперациюПРРО(10);
КонецФункции

&НаКлиенте
Процедура ZОтчет(Команда)
\tРез = ZОтчетНаСервере();
\tПоказатьСтатус(Рез);
КонецПроцедуры

&НаСервере
Функция ZОтчетНаСервере()
\tВозврат ВызватьОперациюПРРО(11);
КонецФункции

&НаКлиенте
Процедура Внесение(Команда)
\tРез = ВнесениеНаСервере(Сумма);
\tПоказатьСтатус(Рез);
КонецПроцедуры

&НаСервере
Функция ВнесениеНаСервере(Знач СуммаОп)
\tВозврат ВызватьВнесениеИзъятие(СуммаОп);
КонецФункции

&НаКлиенте
Процедура Изъятие(Команда)
\tРез = ИзъятиеНаСервере(Сумма);
\tПоказатьСтатус(Рез);
КонецПроцедуры

&НаСервере
Функция ИзъятиеНаСервере(Знач СуммаОп)
\tВозврат ВызватьВнесениеИзъятие(-СуммаОп);
КонецФункции

#КонецОбласти

#Область СлужебныеПроцедурыИФункции

&НаКлиенте
Процедура ПоказатьСтатус(ТекстСтатуса)
\tСтрокаСтатуса = ТекстСтатуса;
КонецПроцедуры

&НаСервере
Функция ВызватьОперациюПРРО(Знач НомерЗадачи)
\tЕсли НЕ ЗначениеЗаполнено(КассовоеОборудование) Тогда
\t\tВозврат "Ошибка: кассовое оборудование не выбрано";
\tКонецЕсли;
\t
\tКО = КассовоеОборудование.ПолучитьОбъект();
\tПараметрыОбор = Новый Структура;
\tПараметрыОбор.Вставить("АдресСервера", КО.АдресСервера);
\tПараметрыОбор.Вставить("Токен", "");
\t
\tРез = "";
\tПопытка
\t\tЕсли НомерЗадачи = 0 Тогда
\t\t\tИтог = Вчсн_ДрайверПРРО.ОткрытьСмену(ПараметрыОбор);
\t\tИначеЕсли НомерЗадачи = 10 Тогда
\t\t\tИтог = Вчсн_ДрайверПРРО.XОтчет(ПараметрыОбор);
\t\tИначеЕсли НомерЗадачи = 11 Тогда
\t\t\tИтог = Вчсн_ДрайверПРРО.ЗакрытьСмену(ПараметрыОбор);
\t\tКонецЕсли;
\t\t
\t\tЕсли Итог.Успех Тогда
\t\t\tРез = "Выполнено успешно";
\t\tИначе
\t\t\tРез = "Ошибка: " + Итог.Ошибка;
\t\tКонецЕсли;
\tИсключение
\t\tРез = "Исключение: " + ОписаниеОшибки();
\tКонецПопытки;
\t
\tВозврат Рез;
КонецФункции

&НаСервере
Функция ВызватьВнесениеИзъятие(Знач Сумма)
\tЕсли НЕ ЗначениеЗаполнено(КассовоеОборудование) Тогда
\t\tВозврат "Ошибка: кассовое оборудование не выбрано";
\tКонецЕсли;
\t
\tКО = КассовоеОборудование.ПолучитьОбъект();
\tПараметрыОбор = Новый Структура;
\tПараметрыОбор.Вставить("АдресСервера", КО.АдресСервера);
\t
\tРез = "";
\tПопытка
\t\tИтог = Вчсн_ДрайверПРРО.ВнесениеВыемка(ПараметрыОбор, Сумма);
\t\tЕсли Итог.Успех Тогда
\t\t\tРез = "Выполнено: " + ?(Сумма > 0, "Внесение", "Изъятие");
\t\tИначе
\t\t\tРез = "Ошибка: " + Итог.Ошибка;
\t\tКонецЕсли;
\tИсключение
\t\tРез = "Исключение: " + ОписаниеОшибки();
\tКонецПопытки;
\t
\tВозврат Рез;
КонецФункции

#КонецОбласти
'''

# === Запись файлов ===
print("Создание файлов обработки Вчсн_КассаПанель...")
write_utf8(DP_DIR / "Вчсн_КассаПанель.xml", dp_xml)
write_bom(DP_DIR / "Ext" / "ObjectModule.bsl", obj_bsl)
write_utf8(DP_DIR / "Forms" / "Форма.xml", form_descriptor)
write_bom(DP_DIR / "Forms" / "Форма" / "Ext" / "Form.xml", form_xml)
write_bom(DP_DIR / "Forms" / "Форма" / "Ext" / "Form" / "Module.bsl", module_bsl)

print("\nВсе файлы созданы успешно!")
print(f"\nUUIDs:")
print(f"  DataProcessor: {DP_UUID}")
print(f"  Form:          {FORM_UUID}")

CV_DP = cv()
CV_FORM = cv()
CV_FORM_MOD = cv()
print(f"\nConfigVersions для CDI:")
print(f"  DataProcessor.Вчсн_КассаПанель:           {CV_DP}")
print(f"  DataProcessor.Вчсн_КассаПанель.Form.Форма: {CV_FORM}")
print(f"  DataProcessor.Вчсн_КассаПанель.Form.Форма/Ext/Form/Module: {CV_FORM_MOD}")
