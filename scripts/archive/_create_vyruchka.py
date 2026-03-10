"""
Создание обработки ВыручкаЗаСмену — все файлы в обеих папках.
BOM + CRLF для Form.xml как требуется платформой 1С.
"""
import os

BASE = r"D:\Git\Public_Trade_Module\Конфигурация"
FOLDERS = [BASE, os.path.join(BASE, "Проверка")]

# === UUIDs (v4 format: xxxxxxxx-xxxx-4xxx-[89ab]xxx-xxxxxxxxxxxx) ===
DP_UUID      = "f3a1b2c4-d5e6-4f7a-8b9c-0d1e2f3a4b5c"
OBJ_TYPE_ID  = "a4b5c6d7-e8f9-4a0b-9c2d-3e4f5a6b7c8d"
OBJ_VALUE_ID = "b5c6d7e8-f9a0-4b1c-ad3e-4f5a6b7c8d9e"
MGR_TYPE_ID  = "c6d7e8f9-a0b1-4c2d-be4f-5a6b7c8d9e0f"
MGR_VALUE_ID = "d7e8f9a0-b1c2-4d3e-8f5a-6b7c8d9e0f10"
FORM_UUID    = "e8f9a0b1-c2d3-4e4f-9a6b-7c8d9e0f1a2b"

# === XML namespace header (MetaDataObject) ===
MDO_HEADER = '<?xml version="1.0" encoding="UTF-8"?>\r\n<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">'

# === Form XML namespace header ===
FORM_HEADER = '<?xml version="1.0" encoding="UTF-8"?>\r\n<Form xmlns="http://v8.1c.ru/8.3/xcf/logform" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:dcscor="http://v8.1c.ru/8.1/data-composition-system/core" xmlns:dcssch="http://v8.1c.ru/8.1/data-composition-system/schema" xmlns:dcsset="http://v8.1c.ru/8.1/data-composition-system/settings" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">'


def write_file(path, content, bom=False):
    """Write file with CRLF line endings, optionally with BOM."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Ensure CRLF
    text = content.replace('\r\n', '\n').replace('\n', '\r\n')
    data = text.encode('utf-8')
    if bom:
        data = b'\xef\xbb\xbf' + data
    with open(path, 'wb') as f:
        f.write(data)
    print(f"  Created: {os.path.relpath(path, BASE)}")


# ── 1. DataProcessors/ВыручкаЗаСмену.xml ────────────────────────────
DP_XML = f"""{MDO_HEADER}
\t<DataProcessor uuid="{DP_UUID}">
\t\t<InternalInfo>
\t\t\t<xr:GeneratedType name="DataProcessorObject.ВыручкаЗаСмену" category="Object">
\t\t\t\t<xr:TypeId>{OBJ_TYPE_ID}</xr:TypeId>
\t\t\t\t<xr:ValueId>{OBJ_VALUE_ID}</xr:ValueId>
\t\t\t</xr:GeneratedType>
\t\t\t<xr:GeneratedType name="DataProcessorManager.ВыручкаЗаСмену" category="Manager">
\t\t\t\t<xr:TypeId>{MGR_TYPE_ID}</xr:TypeId>
\t\t\t\t<xr:ValueId>{MGR_VALUE_ID}</xr:ValueId>
\t\t\t</xr:GeneratedType>
\t\t</InternalInfo>
\t\t<Properties>
\t\t\t<Name>ВыручкаЗаСмену</Name>
\t\t\t<Synonym>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Выручка за смену</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Synonym>
\t\t\t<Comment>Показывает суммы продаж по кассам за текущую открытую смену</Comment>
\t\t\t<UseStandardCommands>true</UseStandardCommands>
\t\t\t<DefaultForm>DataProcessor.ВыручкаЗаСмену.Form.Форма</DefaultForm>
\t\t\t<AuxiliaryForm/>
\t\t\t<IncludeHelpInContents>false</IncludeHelpInContents>
\t\t\t<ExtendedPresentation/>
\t\t\t<Explanation/>
\t\t</Properties>
\t\t<ChildObjects>
\t\t\t<Form>Форма</Form>
\t\t</ChildObjects>
\t</DataProcessor>
</MetaDataObject>"""

# ── 2. Forms/Форма.xml (form descriptor) ─────────────────────────────
FORM_DESC_XML = f"""{MDO_HEADER}
\t<Form uuid="{FORM_UUID}">
\t\t<Properties>
\t\t\t<Name>Форма</Name>
\t\t\t<Synonym>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Выручка за смену</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Synonym>
\t\t\t<Comment/>
\t\t\t<FormType>Managed</FormType>
\t\t\t<IncludeHelpInContents>false</IncludeHelpInContents>
\t\t\t<UsePurposes>
\t\t\t\t<v8:Value xsi:type="app:ApplicationUsePurpose">PlatformApplication</v8:Value>
\t\t\t\t<v8:Value xsi:type="app:ApplicationUsePurpose">MobilePlatformApplication</v8:Value>
\t\t\t</UsePurposes>
\t\t\t<ExtendedPresentation/>
\t\t</Properties>
\t</Form>
</MetaDataObject>"""

# ── 3. Form.xml (managed form definition — needs BOM) ────────────────
FORM_XML = f"""{FORM_HEADER}
\t<AutoCommandBar name="ФормаКоманднаяПанель" id="-1">
\t\t<Autofill>true</Autofill>
\t\t<ChildItems>
\t\t\t<Button name="КнопкаПоказать" id="1">
\t\t\t\t<Type>CommandBarButton</Type>
\t\t\t\t<Representation>PictureAndText</Representation>
\t\t\t\t<CommandName>Form.Command.Показать</CommandName>
\t\t\t\t<Title>
\t\t\t\t\t<v8:item>
\t\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t\t<v8:content>Показать</v8:content>
\t\t\t\t\t</v8:item>
\t\t\t\t</Title>
\t\t\t\t<ExtendedTooltip name="КнопкаПоказатьРасширеннаяПодсказка" id="2"/>
\t\t\t</Button>
\t\t</ChildItems>
\t</AutoCommandBar>
\t<ChildItems>
\t\t<Label name="НадписьПусто" id="3">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Нет данных. Нажмите "Показать" для загрузки.</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<ToolTip>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Нет данных</v8:content>
\t\t\t\t</v8:item>
\t\t\t</ToolTip>
\t\t\t<Visible>true</Visible>
\t\t\t<ExtendedTooltip name="НадписьПустоРасширеннаяПодсказка" id="4"/>
\t\t</Label>
\t\t<Group name="ГруппаЗаголовокРезультата" id="5">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Заголовок результата</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<ToolTip>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Заголовок результата</v8:content>
\t\t\t\t</v8:item>
\t\t\t</ToolTip>
\t\t\t<Visible>false</Visible>
\t\t\t<Type>UsualGroup</Type>
\t\t\t<Grouping>HorizontalIfPossible</Grouping>
\t\t\t<ShowTitle>false</ShowTitle>
\t\t\t<ExtendedTooltip name="ГруппаЗаголовокРезультатаРасширеннаяПодсказка" id="6"/>
\t\t\t<ChildItems>
\t\t\t\t<Label name="НадписьЗаголовокКасса" id="7">
\t\t\t\t\t<Title>
\t\t\t\t\t\t<v8:item>
\t\t\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t\t\t<v8:content>Касса</v8:content>
\t\t\t\t\t\t</v8:item>
\t\t\t\t\t</Title>
\t\t\t\t\t<ExtendedTooltip name="НадписьЗаголовокКассаРасширеннаяПодсказка" id="8"/>
\t\t\t\t\t<Font styleName="NormalTextFont" kind="FontSize" size="12"/>
\t\t\t\t</Label>
\t\t\t\t<Label name="НадписьЗаголовокСумма" id="9">
\t\t\t\t\t<Title>
\t\t\t\t\t\t<v8:item>
\t\t\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t\t\t<v8:content>Выручка</v8:content>
\t\t\t\t\t\t</v8:item>
\t\t\t\t\t</Title>
\t\t\t\t\t<ExtendedTooltip name="НадписьЗаголовокСуммаРасширеннаяПодсказка" id="10"/>
\t\t\t\t\t<Font styleName="NormalTextFont" kind="FontSize" size="12"/>
\t\t\t\t</Label>
\t\t\t</ChildItems>
\t\t</Group>
\t\t<Group name="ГруппаРезультат" id="11">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Результат</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<ToolTip>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Результат</v8:content>
\t\t\t\t</v8:item>
\t\t\t</ToolTip>
\t\t\t<Visible>false</Visible>
\t\t\t<Type>UsualGroup</Type>
\t\t\t<Grouping>Vertical</Grouping>
\t\t\t<ShowTitle>false</ShowTitle>
\t\t\t<ExtendedTooltip name="ГруппаРезультатРасширеннаяПодсказка" id="12"/>
\t\t</Group>
\t\t<Label name="НадписьИтого" id="13">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>ИТОГО:</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<ToolTip>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Итого</v8:content>
\t\t\t\t</v8:item>
\t\t\t</ToolTip>
\t\t\t<Visible>false</Visible>
\t\t\t<ExtendedTooltip name="НадписьИтогоРасширеннаяПодсказка" id="14"/>
\t\t\t<Font styleName="NormalTextFont" kind="FontSize" size="16"/>
\t\t</Label>
\t</ChildItems>
\t<CommandList>
\t\t<Command name="Показать" id="15">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Показать</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<ToolTip>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Показать выручку за смену</v8:content>
\t\t\t\t</v8:item>
\t\t\t</ToolTip>
\t\t\t<Action>Показать</Action>
\t\t</Command>
\t</CommandList>
</Form>"""

# ── 4. Module.bsl ────────────────────────────────────────────────────
MODULE_BSL = """#Область ОбработчикиКомандФормы

&НаКлиенте
Процедура Показать(Команда)
    ПоказатьНаСервере();
КонецПроцедуры

#КонецОбласти

#Область СлужебныеПроцедурыИФункции

&НаСервере
Процедура ПоказатьНаСервере()

    ОчиститьДинамическиеЭлементы();

    Запрос = Новый Запрос;
    Запрос.Текст = 
    "ВЫБРАТЬ
    |   ПродажиОбороты.Касса КАК Касса,
    |   ПродажиОбороты.Касса.Наименование КАК КассаНаименование,
    |   СУММА(ПродажиОбороты.СуммаОборот) КАК СуммаВыручки,
    |   СУММА(ПродажиОбороты.КоличествоОборот) КАК КоличествоТоваров
    |ИЗ
    |   РегистрНакопления.Продажи.Обороты(, , ,
    |       КассоваяСмена В
    |           (ВЫБРАТЬ
    |               КассовыеСмены.Ссылка
    |           ИЗ
    |               Документ.КассоваяСмена КАК КассовыеСмены
    |           ГДЕ
    |               КассовыеСмены.Статус = &СтатусОткрыта)) КАК ПродажиОбороты
    |
    |СГРУППИРОВАТЬ ПО
    |   ПродажиОбороты.Касса,
    |   ПродажиОбороты.Касса.Наименование
    |
    |УПОРЯДОЧИТЬ ПО
    |   КассаНаименование";

    Запрос.УстановитьПараметр("СтатусОткрыта", 
        Перечисления.СтатусыКассовойСмены.Открыта);

    Результат = Запрос.Выполнить();
    
    Если Результат.Пустой() Тогда
        Элементы.НадписьПусто.Видимость = Истина;
        Элементы.ГруппаЗаголовокРезультата.Видимость = Ложь;
        Элементы.ГруппаРезультат.Видимость = Ложь;
        Элементы.НадписьИтого.Видимость = Ложь;
        Возврат;
    КонецЕсли;
    
    Элементы.НадписьПусто.Видимость = Ложь;
    Элементы.ГруппаЗаголовокРезультата.Видимость = Истина;
    Элементы.ГруппаРезультат.Видимость = Истина;
    Элементы.НадписьИтого.Видимость = Истина;
    
    Счётчик = 0;
    ИтогоСумма = 0;
    
    Выборка = Результат.Выбрать();
    Пока Выборка.Следующий() Цикл
        
        Счётчик = Счётчик + 1;
        ИтогоСумма = ИтогоСумма + Выборка.СуммаВыручки;
        
        ИмяГруппы = "ГруппаКасса_" + Формат(Счётчик, "ЧГ=");
        Группа = Элементы.Добавить(ИмяГруппы, Тип("ГруппаФормы"), Элементы.ГруппаРезультат);
        Группа.Вид = ВидГруппыФормы.ОбычнаяГруппа;
        Группа.Группировка = ГруппировкаПодчиненныхЭлементовФормы.ГоризонтальнаяЕслиВозможно;
        Группа.ОтображатьЗаголовок = Ложь;
        
        ИмяНадписиКассы = "НадписьКасса_" + Формат(Счётчик, "ЧГ=");
        НадписьКассы = Элементы.Добавить(ИмяНадписиКассы, Тип("ДекорацияФормы"), Группа);
        НадписьКассы.Вид = ВидДекорацииФормы.Надпись;
        НадписьКассы.Заголовок = Выборка.КассаНаименование + ":";
        НадписьКассы.Шрифт = Новый Шрифт(, , Истина);
        
        ИмяНадписиСуммы = "НадписьСумма_" + Формат(Счётчик, "ЧГ=");
        НадписьСуммы = Элементы.Добавить(ИмяНадписиСуммы, Тип("ДекорацияФормы"), Группа);
        НадписьСуммы.Вид = ВидДекорацииФормы.Надпись;
        НадписьСуммы.Заголовок = Формат(Выборка.СуммаВыручки, "ЧДЦ=2; ЧРГ=' '; ЧГ=") + " грн.";
        НадписьСуммы.Шрифт = Новый Шрифт(, 14);
        НадписьСуммы.ЦветТекста = WebЦвета.DarkGreen;
        
    КонецЦикла;
    
    Элементы.НадписьИтого.Заголовок = "ИТОГО: " 
        + Формат(ИтогоСумма, "ЧДЦ=2; ЧРГ=' '; ЧГ=") + " грн.";

КонецПроцедуры

&НаСервере
Процедура ОчиститьДинамическиеЭлементы()
    
    МассивУдаляемых = Новый Массив;
    
    Для Каждого Элемент Из Элементы.ГруппаРезультат.ПодчиненныеЭлементы Цикл
        МассивУдаляемых.Добавить(Элемент);
    КонецЦикла;
    
    Для Каждого Элемент Из МассивУдаляемых Цикл
        Элементы.Удалить(Элемент);
    КонецЦикла;
    
КонецПроцедуры

#КонецОбласти
"""

# ═══════════════════════════════════════════════════════════════════════
# Создание файлов
# ═══════════════════════════════════════════════════════════════════════

for folder in FOLDERS:
    label = "Основная" if folder == BASE else "Проверка"
    print(f"\n=== Папка: {label} ===")
    
    dp_dir = os.path.join(folder, "DataProcessors")
    
    # 1. DataProcessors/ВыручкаЗаСмену.xml
    write_file(os.path.join(dp_dir, "ВыручкаЗаСмену.xml"), DP_XML)
    
    # 2. Forms/Форма.xml (form descriptor)
    write_file(
        os.path.join(dp_dir, "ВыручкаЗаСмену", "Forms", "Форма.xml"),
        FORM_DESC_XML
    )
    
    # 3. Form.xml (managed form definition — BOM!)
    write_file(
        os.path.join(dp_dir, "ВыручкаЗаСмену", "Forms", "Форма", "Ext", "Form.xml"),
        FORM_XML,
        bom=True
    )
    
    # 4. Module.bsl
    write_file(
        os.path.join(dp_dir, "ВыручкаЗаСмену", "Forms", "Форма", "Ext", "Form", "Module.bsl"),
        MODULE_BSL
    )

print("\n✅ Все файлы обработки ВыручкаЗаСмену созданы успешно!")
print(f"\nUUIDs:")
print(f"  DataProcessor: {DP_UUID}")
print(f"  Form:          {FORM_UUID}")
