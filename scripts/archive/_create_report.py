# -*- coding: utf-8 -*-
"""Create report СправочникНоменклатуры with all files"""
import pathlib

BASE = pathlib.Path(r"D:\Git\Public_Trade_Module")
KONF = BASE / "Конфигурация"
PROV = KONF / "Проверка"

# UUIDs
REPORT_UUID = "fe541e03-869c-4899-a712-32a22e4dfab4"
OBJ_TYPE_ID = "32aeee7b-cfb2-45d9-889d-4987cd9b2bdd"
OBJ_VALUE_ID = "d1514326-9d5c-42c1-ba77-d3180c478211"
MGR_TYPE_ID = "89922bd2-8af5-4a4b-8b62-5ae3960e3091"
MGR_VALUE_ID = "a18c3c40-85ff-4289-8a17-f2bbf0a5b41c"
FORM_UUID = "81722667-e306-4400-8407-ad097c01c5e1"
ATTR_SKLAD_UUID = "c5a7f123-d891-4e56-b234-a67890cdef12"
ATTR_TIPCEN_UUID = "d6b8e234-e902-4f67-c345-b78901def023"

BOM = '\ufeff'

REPORT_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
\t<Report uuid="{REPORT_UUID}">
\t\t<InternalInfo>
\t\t\t<xr:GeneratedType name="ReportObject.СправочникНоменклатуры" category="Object">
\t\t\t\t<xr:TypeId>{OBJ_TYPE_ID}</xr:TypeId>
\t\t\t\t<xr:ValueId>{OBJ_VALUE_ID}</xr:ValueId>
\t\t\t</xr:GeneratedType>
\t\t\t<xr:GeneratedType name="ReportManager.СправочникНоменклатуры" category="Manager">
\t\t\t\t<xr:TypeId>{MGR_TYPE_ID}</xr:TypeId>
\t\t\t\t<xr:ValueId>{MGR_VALUE_ID}</xr:ValueId>
\t\t\t</xr:GeneratedType>
\t\t</InternalInfo>
\t\t<Properties>
\t\t\t<Name>СправочникНоменклатуры</Name>
\t\t\t<Synonym>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Справочник номенклатуры</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Synonym>
\t\t\t<Comment/>
\t\t\t<UseStandardCommands>true</UseStandardCommands>
\t\t\t<DefaultForm>Report.СправочникНоменклатуры.Form.ФормаОтчета</DefaultForm>
\t\t\t<AuxiliaryForm/>
\t\t\t<MainDataCompositionSchema/>
\t\t\t<DefaultSettingsForm/>
\t\t\t<AuxiliarySettingsForm/>
\t\t\t<DefaultVariantForm/>
\t\t\t<VariantsStorage/>
\t\t\t<SettingsStorage/>
\t\t\t<IncludeHelpInContents>false</IncludeHelpInContents>
\t\t\t<ExtendedPresentation/>
\t\t\t<Explanation/>
\t\t</Properties>
\t\t<ChildObjects>
\t\t\t<Attribute uuid="{ATTR_SKLAD_UUID}">
\t\t\t\t<Properties>
\t\t\t\t\t<Name>Склад</Name>
\t\t\t\t\t<Synonym>
\t\t\t\t\t\t<v8:item>
\t\t\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t\t\t<v8:content>Склад</v8:content>
\t\t\t\t\t\t</v8:item>
\t\t\t\t\t</Synonym>
\t\t\t\t\t<Comment/>
\t\t\t\t\t<Type>
\t\t\t\t\t\t<v8:Type xmlns:d6p1="http://v8.1c.ru/8.1/data/enterprise/current-config">d6p1:CatalogRef.Склады</v8:Type>
\t\t\t\t\t</Type>
\t\t\t\t\t<MinValue xsi:type="xs:undefined"/>
\t\t\t\t\t<MaxValue xsi:type="xs:undefined"/>
\t\t\t\t\t<Indexing>DontIndex</Indexing>
\t\t\t\t</Properties>
\t\t\t</Attribute>
\t\t\t<Attribute uuid="{ATTR_TIPCEN_UUID}">
\t\t\t\t<Properties>
\t\t\t\t\t<Name>ТипЦен</Name>
\t\t\t\t\t<Synonym>
\t\t\t\t\t\t<v8:item>
\t\t\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t\t\t<v8:content>Тип цен</v8:content>
\t\t\t\t\t\t</v8:item>
\t\t\t\t\t</Synonym>
\t\t\t\t\t<Comment/>
\t\t\t\t\t<Type>
\t\t\t\t\t\t<v8:Type xmlns:d6p1="http://v8.1c.ru/8.1/data/enterprise/current-config">d6p1:CatalogRef.ТипыЦен</v8:Type>
\t\t\t\t\t</Type>
\t\t\t\t\t<MinValue xsi:type="xs:undefined"/>
\t\t\t\t\t<MaxValue xsi:type="xs:undefined"/>
\t\t\t\t\t<Indexing>DontIndex</Indexing>
\t\t\t\t</Properties>
\t\t\t</Attribute>
\t\t\t<Form>ФормаОтчета</Form>
\t\t</ChildObjects>
\t</Report>
</MetaDataObject>'''

OBJECT_MODULE = BOM + '''#Область ПрограммныйИнтерфейс

Процедура СформироватьОтчет(ТабДок) Экспорт
\t
\tТабДок.Очистить();
\t
\t// Условия виртуальных таблиц
\tУсловиеЦен = "";
\tЕсли ЗначениеЗаполнено(ТипЦен) Тогда
\t\tУсловиеЦен = ", ТипЦен = &ТипЦен";
\tКонецЕсли;
\t
\tУсловиеОстатков = "";
\tЕсли ЗначениеЗаполнено(Склад) Тогда
\t\tУсловиеОстатков = ", Склад = &Склад";
\tКонецЕсли;
\t
\t// Основной запрос
\tЗапрос = Новый Запрос;
\tЗапрос.Текст = 
\t"ВЫБРАТЬ
\t|\tНом.Ссылка КАК Номенклатура,
\t|\tНом.Артикул КАК Артикул,
\t|\tНом.Наименование КАК Наименование,
\t|\tНом.ЕдиницаИзмерения КАК ЕдиницаИзмерения,
\t|\tЕСТЬNULL(Цены.Цена, 0) КАК Цена,
\t|\tЕСТЬNULL(Остатки.КоличествоОстаток, 0) КАК Остаток
\t|ИЗ
\t|\tСправочник.Номенклатура КАК Ном
\t|\t\tЛЕВОЕ СОЕДИНЕНИЕ РегистрСведений.ЦеныНоменклатуры.СрезПоследних(" + УсловиеЦен + ") КАК Цены
\t|\t\tПО Ном.Ссылка = Цены.Номенклатура
\t|\t\tЛЕВОЕ СОЕДИНЕНИЕ РегистрНакопления.ОстаткиТоваров.Остатки(" + УсловиеОстатков + ") КАК Остатки
\t|\t\tПО Ном.Ссылка = Остатки.Номенклатура
\t|ГДЕ
\t|\tНЕ Ном.ЭтоГруппа
\t|\tИ НЕ Ном.ПометкаУдаления
\t|УПОРЯДОЧИТЬ ПО
\t|\tНом.Наименование";
\t
\tЕсли ЗначениеЗаполнено(ТипЦен) Тогда
\t\tЗапрос.УстановитьПараметр("ТипЦен", ТипЦен);
\tКонецЕсли;
\t
\tЕсли ЗначениеЗаполнено(Склад) Тогда
\t\tЗапрос.УстановитьПараметр("Склад", Склад);
\tКонецЕсли;
\t
\tРезультат = Запрос.Выполнить();
\tВыборка = Результат.Выбрать();
\t
\t// Штрихкоды — отдельный запрос
\tЗапросШК = Новый Запрос;
\tЗапросШК.Текст = 
\t"ВЫБРАТЬ
\t|\tШК.Номенклатура КАК Номенклатура,
\t|\tШК.Штрихкод КАК Штрихкод
\t|ИЗ
\t|\tРегистрСведений.Штрихкоды КАК ШК
\t|УПОРЯДОЧИТЬ ПО
\t|\tШК.Номенклатура, ШК.Штрихкод";
\t
\tРезультатШК = ЗапросШК.Выполнить();
\tВыборкаШК = РезультатШК.Выбрать();
\t
\t// Собираем штрихкоды в Соответствие
\tСоответствиеШК = Новый Соответствие;
\tПока ВыборкаШК.Следующий() Цикл
\t\tТекущиеШК = СоответствиеШК.Получить(ВыборкаШК.Номенклатура);
\t\tЕсли ТекущиеШК = Неопределено Тогда
\t\t\tСоответствиеШК.Вставить(ВыборкаШК.Номенклатура, ВыборкаШК.Штрихкод);
\t\tИначе
\t\t\tСоответствиеШК.Вставить(ВыборкаШК.Номенклатура, ТекущиеШК + ", " + ВыборкаШК.Штрихкод);
\t\tКонецЕсли;
\tКонецЦикла;
\t
\t// Заголовки
\tЗаголовки = Новый Массив;
\tЗаголовки.Добавить("Артикул");
\tЗаголовки.Добавить("Номенклатура");
\tЗаголовки.Добавить("Ед. изм.");
\tЗаголовки.Добавить("Цена");
\tЗаголовки.Добавить("Остаток");
\tЗаголовки.Добавить("Штрихкоды");
\t
\tДля К = 0 По Заголовки.ВГраница() Цикл
\t\tОбласть = ТабДок.Область(1, К + 1, 1, К + 1);
\t\tОбласть.Текст = Заголовки[К];
\t\tОбласть.ЖирныйШрифт = Истина;
\t\tОбласть.ГоризонтальноеПоложение = ГоризонтальноеПоложение.Центр;
\t\tОбласть.ЦветФона = Новый Цвет(220, 220, 220);
\tКонецЦикла;
\t
\t// Ширина колонок
\tТабДок.Область(, 1, , 1).ШиринаКолонки = 15;
\tТабДок.Область(, 2, , 2).ШиринаКолонки = 40;
\tТабДок.Область(, 3, , 3).ШиринаКолонки = 10;
\tТабДок.Область(, 4, , 4).ШиринаКолонки = 15;
\tТабДок.Область(, 5, , 5).ШиринаКолонки = 12;
\tТабДок.Область(, 6, , 6).ШиринаКолонки = 40;
\t
\t// Данные
\tНомерСтроки = 2;
\tПока Выборка.Следующий() Цикл
\t\t
\t\tТабДок.Область(НомерСтроки, 1, НомерСтроки, 1).Текст = Выборка.Артикул;
\t\tТабДок.Область(НомерСтроки, 2, НомерСтроки, 2).Текст = Выборка.Наименование;
\t\tТабДок.Область(НомерСтроки, 3, НомерСтроки, 3).Текст = Строка(Выборка.ЕдиницаИзмерения);
\t\tТабДок.Область(НомерСтроки, 4, НомерСтроки, 4).Текст = Формат(Выборка.Цена, "ЧДЦ=2; ЧН=0,00");
\t\tТабДок.Область(НомерСтроки, 5, НомерСтроки, 5).Текст = Формат(Выборка.Остаток, "ЧДЦ=3; ЧН=0");
\t\t
\t\tШтрихкодыСтрока = СоответствиеШК.Получить(Выборка.Номенклатура);
\t\tЕсли ШтрихкодыСтрока = Неопределено Тогда
\t\t\tШтрихкодыСтрока = "";
\t\tКонецЕсли;
\t\tТабДок.Область(НомерСтроки, 6, НомерСтроки, 6).Текст = ШтрихкодыСтрока;
\t\t
\t\tНомерСтроки = НомерСтроки + 1;
\t\t
\tКонецЦикла;
\t
\t// Зафиксировать строку заголовка
\tТабДок.ФиксацияСверху = 1;
\t
КонецПроцедуры

#КонецОбласти
'''

FORM_DESCRIPTOR = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
\t<Form uuid="{FORM_UUID}">
\t\t<Properties>
\t\t\t<Name>ФормаОтчета</Name>
\t\t\t<FormType>Managed</FormType>
\t\t\t<UsePurposes>
\t\t\t\t<xr:Item xmlns:xr="http://v8.1c.ru/8.3/xcf/readable">PlatformApplication</xr:Item>
\t\t\t\t<xr:Item xmlns:xr="http://v8.1c.ru/8.3/xcf/readable">MobilePlatformApplication</xr:Item>
\t\t\t</UsePurposes>
\t\t</Properties>
\t</Form>
</MetaDataObject>'''

FORM_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<Form xmlns="http://v8.1c.ru/8.3/xcf/logform" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
\t<Title>
\t\t<v8:item>
\t\t\t<v8:lang>ru</v8:lang>
\t\t\t<v8:content>Справочник номенклатуры</v8:content>
\t\t</v8:item>
\t</Title>
\t<AutoTitle>false</AutoTitle>
\t<AutoCommandBar name="ФормаКоманднаяПанель" id="-1">
\t\t<Autofill>true</Autofill>
\t</AutoCommandBar>
\t<ChildItems>
\t\t<UsualGroup name="ГруппаПараметры" id="1">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Параметры</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<Group>Horizontal</Group>
\t\t\t<Representation>None</Representation>
\t\t\t<ShowTitle>false</ShowTitle>
\t\t\t<ExtendedTooltip name="ГруппаПараметрыРасширеннаяПодсказка" id="2"/>
\t\t\t<ChildItems>
\t\t\t\t<InputField name="Склад" id="3">
\t\t\t\t\t<DataPath>Объект.Склад</DataPath>
\t\t\t\t\t<ContextMenu name="СкладКонтекстноеМеню" id="4"/>
\t\t\t\t\t<ExtendedTooltip name="СкладРасширеннаяПодсказка" id="5"/>
\t\t\t\t</InputField>
\t\t\t\t<InputField name="ТипЦен" id="6">
\t\t\t\t\t<DataPath>Объект.ТипЦен</DataPath>
\t\t\t\t\t<ContextMenu name="ТипЦенКонтекстноеМеню" id="7"/>
\t\t\t\t\t<ExtendedTooltip name="ТипЦенРасширеннаяПодсказка" id="8"/>
\t\t\t\t</InputField>
\t\t\t\t<Button name="Сформировать" id="9">
\t\t\t\t\t<Type>CommandBarButton</Type>
\t\t\t\t\t<CommandName>Форма.Команда.Сформировать</CommandName>
\t\t\t\t\t<Representation>PictureAndText</Representation>
\t\t\t\t\t<DefaultButton>true</DefaultButton>
\t\t\t\t\t<ExtendedTooltip name="СформироватьРасширеннаяПодсказка" id="10"/>
\t\t\t\t</Button>
\t\t\t</ChildItems>
\t\t</UsualGroup>
\t\t<SpreadsheetDocumentField name="ПолеРезультата" id="11">
\t\t\t<DataPath>РезультатОтчета</DataPath>
\t\t\t<Width>100</Width>
\t\t\t<Height>30</Height>
\t\t\t<HorizontalStretch>true</HorizontalStretch>
\t\t\t<VerticalStretch>true</VerticalStretch>
\t\t\t<Output>Auto</Output>
\t\t\t<ContextMenu name="ПолеРезультатаКонтекстноеМеню" id="12"/>
\t\t\t<ExtendedTooltip name="ПолеРезультатаРасширеннаяПодсказка" id="13"/>
\t\t</SpreadsheetDocumentField>
\t</ChildItems>
\t<Attributes>
\t\t<Attribute name="Объект" id="1">
\t\t\t<Type>
\t\t\t\t<v8:Type xmlns:d4p1="http://v8.1c.ru/8.1/data/enterprise/current-config">d4p1:ReportObject.СправочникНоменклатуры</v8:Type>
\t\t\t</Type>
\t\t\t<MainAttribute>true</MainAttribute>
\t\t\t<SavedData>true</SavedData>
\t\t</Attribute>
\t\t<Attribute name="РезультатОтчета" id="2">
\t\t\t<Type>
\t\t\t\t<v8:Type>v8:SpreadsheetDocument</v8:Type>
\t\t\t</Type>
\t\t</Attribute>
\t</Attributes>
\t<Commands>
\t\t<Command name="Сформировать" id="1">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Сформировать</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<ToolTip>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Сформировать отчет</v8:content>
\t\t\t\t</v8:item>
\t\t\t</ToolTip>
\t\t\t<Action>Сформировать</Action>
\t\t</Command>
\t</Commands>
</Form>'''

FORM_MODULE = BOM + '''#Область ОбработчикиКомандФормы

&НаКлиенте
Процедура Сформировать(Команда)
\t
\tСформироватьНаСервере();
\t
КонецПроцедуры

#КонецОбласти

#Область СлужебныеПроцедуры

&НаСервере
Процедура СформироватьНаСервере()
\t
\tОтчет = РеквизитФормыВЗначение("Объект");
\tОтчет.СформироватьОтчет(РезультатОтчета);
\t
КонецПроцедуры

#КонецОбласти
'''

def write_file(base, relpath, content, is_bsl=False):
    p = base / relpath
    p.parent.mkdir(parents=True, exist_ok=True)
    if is_bsl:
        p.write_text(content, encoding='utf-8-sig')
    else:
        p.write_text(content, encoding='utf-8')
    print(f"  + {relpath}")

for base_path in [KONF, PROV]:
    label = "Конфигурация" if base_path == KONF else "Проверка"
    print(f"\n=== {label} ===")
    write_file(base_path, "Reports/СправочникНоменклатуры.xml", REPORT_XML)
    write_file(base_path, "Reports/СправочникНоменклатуры/Ext/ObjectModule.bsl", OBJECT_MODULE, is_bsl=True)
    write_file(base_path, "Reports/СправочникНоменклатуры/Forms/ФормаОтчета.xml", FORM_DESCRIPTOR)
    write_file(base_path, "Reports/СправочникНоменклатуры/Forms/ФормаОтчета/Ext/Form.xml", FORM_XML)
    write_file(base_path, "Reports/СправочникНоменклатуры/Forms/ФормаОтчета/Ext/Form/Module.bsl", FORM_MODULE, is_bsl=True)

print("\nDone!")
