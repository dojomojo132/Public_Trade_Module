# -*- coding: utf-8 -*-
"""Fix Form.xml and Module.bsl: proper BOM handling"""
import pathlib

BOM = b'\xef\xbb\xbf'

FORM_XML = '''<?xml version="1.0" encoding="UTF-8"?>
<Form xmlns="http://v8.1c.ru/8.3/xcf/logform" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:dcscor="http://v8.1c.ru/8.1/data-composition-system/core" xmlns:dcssch="http://v8.1c.ru/8.1/data-composition-system/schema" xmlns:dcsset="http://v8.1c.ru/8.1/data-composition-system/settings" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
\t<WindowOpeningMode>LockOwnerWindow</WindowOpeningMode>
\t<UseForFoldersAndItems>Folders</UseForFoldersAndItems>
\t<AutoCommandBar name="ФормаКоманднаяПанель" id="-1"/>
\t<ChildItems>
\t\t<InputField name="Наименование" id="1">
\t\t\t<DataPath>Объект.Description</DataPath>
\t\t\t<EditMode>EnterOnInput</EditMode>
\t\t\t<Width>2</Width>
\t\t\t<ExtendedEditMultipleValues>true</ExtendedEditMultipleValues>
\t\t\t<ContextMenu name="НаименованиеКонтекстноеМеню" id="2"/>
\t\t\t<ExtendedTooltip name="НаименованиеРасширеннаяПодсказка" id="3"/>
\t\t</InputField>
\t\t<InputField name="ПроцентНаценки" id="4">
\t\t\t<DataPath>Объект.ПроцентНаценки</DataPath>
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>% наценки</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<EditMode>EnterOnInput</EditMode>
\t\t\t<ExtendedEditMultipleValues>true</ExtendedEditMultipleValues>
\t\t\t<ContextMenu name="ПроцентНаценкиКонтекстноеМеню" id="5"/>
\t\t\t<ExtendedTooltip name="ПроцентНаценкиРасширеннаяПодсказка" id="6"/>
\t\t</InputField>
\t\t<InputField name="Родитель" id="7">
\t\t\t<DataPath>Объект.Parent</DataPath>
\t\t\t<Visible>false</Visible>
\t\t\t<EditMode>EnterOnInput</EditMode>
\t\t\t<ExtendedEditMultipleValues>true</ExtendedEditMultipleValues>
\t\t\t<ContextMenu name="РодительКонтекстноеМеню" id="8"/>
\t\t\t<ExtendedTooltip name="РодительРасширеннаяПодсказка" id="9"/>
\t\t</InputField>
\t\t<Button name="КнопкаУстановитьНаценку" id="10">
\t\t\t<Type>UsualButton</Type>
\t\t\t<CommandName>Form.Command.УстановитьНаценкуДочерним</CommandName>
\t\t\t<ExtendedTooltip name="КнопкаУстановитьНаценкуРасширеннаяПодсказка" id="11"/>
\t\t</Button>
\t</ChildItems>
\t<Attributes>
\t\t<Attribute name="Объект" id="1">
\t\t\t<Type>
\t\t\t\t<v8:Type>cfg:CatalogObject.Номенклатура</v8:Type>
\t\t\t</Type>
\t\t\t<MainAttribute>true</MainAttribute>
\t\t\t<SavedData>true</SavedData>
\t\t</Attribute>
\t</Attributes>
\t<Commands>
\t\t<Command name="УстановитьНаценкуДочерним" id="1">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Установить наценку</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<ToolTip>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Установить данный процент наценки для всех дочерних элементов группы</v8:content>
\t\t\t\t</v8:item>
\t\t\t</ToolTip>
\t\t\t<Action>УстановитьНаценкуДочернимКлиент</Action>
\t\t</Command>
\t</Commands>
</Form>
'''

MODULE_BSL = '''
#Область ОбработчикиКомандФормы

&НаКлиенте
Асинх Процедура УстановитьНаценкуДочернимКлиент(Команда)
\t
\tПроцент = Объект.ПроцентНаценки;
\t
\tЕсли НЕ ЗначениеЗаполнено(Процент) Тогда
\t\tЖдать ПредупреждениеАсинх("Укажите процент наценки!");
\t\tВозврат;
\tКонецЕсли;
\t
\tТекстВопроса = "Установить наценку " + Формат(Процент, "ЧД=10; ЧЦ=2; ЧГ=") + "% для всех дочерних элементов?";
\t
\tОтвет = Ждать ВопросАсинх(ТекстВопроса, РежимДиалогаВопрос.ДаНет);
\tЕсли Ответ <> КодВозвратаДиалога.Да Тогда
\t\tВозврат;
\tКонецЕсли;
\t
\tКоличество = УстановитьНаценкуДочернимНаСервере();
\t
\tЖдать ПредупреждениеАсинх("Наценка " + Формат(Процент, "ЧД=10; ЧЦ=2; ЧГ=") + "% установлена для " + Количество + " элементов.");
\t
КонецПроцедуры

#КонецОбласти

#Область СлужебныеПроцедуры

&НаСервере
Функция УстановитьНаценкуДочернимНаСервере()
\t
\tСсылкаГруппы = Объект.Ref;
\tПроцент = Объект.ПроцентНаценки;
\t
\tЗапрос = Новый Запрос;
\tЗапрос.Текст =
\t\t"ВЫБРАТЬ
\t\t|Спр.Ссылка КАК Ссылка
\t\t|ИЗ
\t\t|Справочник.Номенклатура КАК Спр
\t\t|ГДЕ
\t\t|Спр.Родитель В ИЕРАРХИИ(&Группа)
\t\t|И НЕ Спр.ЭтоГруппа
\t\t|И НЕ Спр.ПометкаУдаления";
\tЗапрос.УстановитьПараметр("Группа", СсылкаГруппы);
\t
\tРезультат = Запрос.Выполнить();
\tВыборка = Результат.Выбрать();
\t
\tКоличествоОбновленных = 0;
\t
\tНачатьТранзакцию();
\tПопытка
\t\tПока Выборка.Следующий() Цикл
\t\t\tОбъектНом = Выборка.Ссылка.ПолучитьОбъект();
\t\t\tОбъектНом.ПроцентНаценки = Процент;
\t\t\tОбъектНом.Записать();
\t\t\tКоличествоОбновленных = КоличествоОбновленных + 1;
\t\tКонецЦикла;
\t\tЗафиксироватьТранзакцию();
\tИсключение
\t\tОтменитьТранзакцию();
\t\tВызватьИсключение;
\tКонецПопытки;
\t
\tВозврат Формат(КоличествоОбновленных, "ЧГ=");
\t
КонецФункции

#КонецОбласти
'''

paths = [
    pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Catalogs\Номенклатура\Forms\ФормаГруппы"),
    pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Catalogs\Номенклатура\Forms\ФормаГруппы"),
]

for p in paths:
    form_xml_path = p / "Ext" / "Form.xml"
    module_path = p / "Ext" / "Form" / "Module.bsl"
    
    form_xml_path.parent.mkdir(parents=True, exist_ok=True)
    module_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write Form.xml: BOM + UTF-8 content with CRLF
    content_bytes = FORM_XML.encode('utf-8')
    content_bytes = content_bytes.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
    form_xml_path.write_bytes(BOM + content_bytes)
    
    # Verify
    check = form_xml_path.read_bytes()
    print(f"Form.xml: {form_xml_path.relative_to(p.parent.parent.parent.parent.parent)}")
    print(f"  Size: {len(check)} bytes, BOM: {check[:3] == BOM}, First 5: {' '.join(f'{b:02x}' for b in check[:5])}")
    
    # Write Module.bsl: BOM + UTF-8 content with CRLF
    mod_bytes = MODULE_BSL.encode('utf-8')
    mod_bytes = mod_bytes.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
    module_path.write_bytes(BOM + mod_bytes)
    
    check2 = module_path.read_bytes()
    print(f"Module.bsl: Size: {len(check2)} bytes, BOM: {check2[:3] == BOM}")
    print()

print("Done!")
