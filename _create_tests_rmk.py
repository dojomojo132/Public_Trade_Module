# -*- coding: utf-8 -*-
"""Создание обработки ТестыРМК в обеих папках конфигурации."""
import pathlib, shutil, re

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")
CONFIGS = [
    ROOT / "Конфигурация",
    ROOT / "Конфигурация" / "Проверка",
]

# ── UUIDs ──────────────────────────────────────────────────────────────────
MAIN_UUID  = "f7a8b9c0-d1e2-4f3a-5b6c-7d8e9f0a1b2c"
TYPE_OBJ   = "e6b7c8d9-e0f1-4a2b-3c4d-5e6f7a8b9c0d"
VAL_OBJ    = "d5c6d7e8-f9a0-4b1c-2d3e-4f5a6b7c8d9e"
TYPE_MGR   = "c4b5c6d7-e8f9-4a0b-1c2d-3e4f5a6b7c8d"
VAL_MGR    = "b3a4b5c6-d7e8-4f9a-0b1c-2d3e4f5a6b7c"
FORM_UUID  = "a2b3c4d5-e6f7-4a8b-9c0d-e1f2a3b4c5d6"

# ── XML / BSL contents ─────────────────────────────────────────────────────

DATAPROCESSOR_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
\t<DataProcessor uuid="{MAIN_UUID}">
\t\t<InternalInfo>
\t\t\t<xr:GeneratedType name="DataProcessorObject.ТестыРМК" category="Object">
\t\t\t\t<xr:TypeId>{TYPE_OBJ}</xr:TypeId>
\t\t\t\t<xr:ValueId>{VAL_OBJ}</xr:ValueId>
\t\t\t</xr:GeneratedType>
\t\t\t<xr:GeneratedType name="DataProcessorManager.ТестыРМК" category="Manager">
\t\t\t\t<xr:TypeId>{TYPE_MGR}</xr:TypeId>
\t\t\t\t<xr:ValueId>{VAL_MGR}</xr:ValueId>
\t\t\t</xr:GeneratedType>
\t\t</InternalInfo>
\t\t<Properties>
\t\t\t<Name>ТестыРМК</Name>
\t\t\t<Synonym>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Тесты РМК</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Synonym>
\t\t\t<Comment/>
\t\t\t<UseStandardCommands>true</UseStandardCommands>
\t\t\t<DefaultForm>DataProcessor.ТестыРМК.Form.Форма</DefaultForm>
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

FORMA_DESCRIPTOR_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
\t<Form uuid="{FORM_UUID}">
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
\t\t\t\t<v8:Value xsi:type="app:ApplicationUsePurpose">MobilePlatformApplication</v8:Value>
\t\t\t</UsePurposes>
\t\t\t<ExtendedPresentation/>
\t\t</Properties>
\t</Form>
</MetaDataObject>
'''

FORM_XML = f'''<?xml version="1.0" encoding="UTF-8"?>
<Form xmlns="http://v8.1c.ru/8.3/xcf/logform" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:dcscor="http://v8.1c.ru/8.1/data-composition-system/core" xmlns:dcssch="http://v8.1c.ru/8.1/data-composition-system/schema" xmlns:dcsset="http://v8.1c.ru/8.1/data-composition-system/settings" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
\t<AutoCommandBar name="ФормаКоманднаяПанель" id="-1"/>
\t<Events>
\t\t<Event name="OnCreateAtServer">ПриСозданииНаСервере</Event>
\t</Events>
\t<ChildItems>
\t\t<Button name="КнопкаЗапустить" id="1">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Запустить тесты</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<Type>UsualButton</Type>
\t\t\t<CommandName>Form.Command.ЗапуститьТесты</CommandName>
\t\t\t<ExtendedTooltip name="КнопкаЗапуститьРасширеннаяПодсказка" id="2"/>
\t\t</Button>
\t\t<InputField name="Результаты" id="3">
\t\t\t<DataPath>Результаты</DataPath>
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Результаты тестирования</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<MultiLine>true</MultiLine>
\t\t\t<HorizontalStretch>true</HorizontalStretch>
\t\t\t<VerticalStretch>true</VerticalStretch>
\t\t\t<ContextMenu name="РезультатыКонтекстноеМеню" id="4"/>
\t\t\t<ExtendedTooltip name="РезультатыРасширеннаяПодсказка" id="5"/>
\t\t</InputField>
\t</ChildItems>
\t<Attributes>
\t\t<Attribute name="Объект" id="100">
\t\t\t<Type>
\t\t\t\t<v8:Type>cfg:DataProcessorObject.ТестыРМК</v8:Type>
\t\t\t</Type>
\t\t\t<MainAttribute>true</MainAttribute>
\t\t</Attribute>
\t\t<Attribute name="Результаты" id="101">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Результаты</v8:content>
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
\t\t<Command name="ЗапуститьТесты" id="1">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Запустить тесты</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<Action>ЗапуститьТесты</Action>
\t\t</Command>
\t</Commands>
</Form>
'''

MODULE_BSL = r"""// Тесты РМК — standalone обработка тестирования без YAxUnit
// Версия: 1.0 — тесты КассовойСмены, ЧекаКММ, ВозвратаТовара

#Область ОбработчикиФормы

&НаСервере
Процедура ПриСозданииНаСервере(Отказ, СтандартнаяОбработка)
	Результаты = "Нажмите ""Запустить тесты"" для начала тестирования.";
КонецПроцедуры

#КонецОбласти

#Область ОбработчикиКоманд

&НаКлиенте
Процедура ЗапуститьТесты(Команда)
	Результаты = ЗапуститьТестыНаСервере();
КонецПроцедуры

#КонецОбласти

#Область СлужебныеПроцедурыИФункции

&НаСервереБезКонтекста
Функция ЗапуститьТестыНаСервере()

	Лог      = Новый Массив;
	Счётчик  = Новый Структура("Всего, Прошло, Упало", 0, 0, 0);

	Лог.Добавить("=== ТЕСТЫ РМК ===");
	Лог.Добавить("Запуск: " + Формат(ТекущаяДатаСеанса(), "ДФ=dd.MM.yyyy ЧЦ=2 ЧВ=2:"));
	Лог.Добавить("");

	Лог.Добавить("--- Тесты: Кассовая смена ---");
	ПровестиТестыКассовойСмены(Лог, Счётчик);

	Лог.Добавить("");
	Лог.Добавить("--- Тесты: Чек ККМ и Возврат ---");
	ПровестиТестыЧекаИВозврата(Лог, Счётчик);

	Лог.Добавить("");
	Лог.Добавить("==================");
	ПрефиксИтог = ?(Счётчик.Упало = 0, "УСПЕШНО", "ЕСТЬ ОШИБКИ");
	Лог.Добавить("ИТОГ [" + ПрефиксИтог + "]: Всего=" + Счётчик.Всего
		+ "  Прошло=" + Счётчик.Прошло + "  Упало=" + Счётчик.Упало);

	Возврат СтрСоединить(Лог, Символы.ПС);

КонецФункции

// ─── Вспомогательная функция утверждения ─────────────────────────────────

&НаСервереБезКонтекста
Процедура Утверждать(Условие, Описание, Лог, Счётчик)
	Счётчик.Всего = Счётчик.Всего + 1;
	Если Условие Тогда
		Счётчик.Прошло = Счётчик.Прошло + 1;
		Лог.Добавить("  OK: " + Описание);
	Иначе
		Счётчик.Упало = Счётчик.Упало + 1;
		Лог.Добавить("  FAILED: " + Описание);
	КонецЕсли;
КонецПроцедуры

// ─── Тесты Кассовой смены ─────────────────────────────────────────────────

&НаСервереБезКонтекста
Процедура ПровестиТестыКассовойСмены(Лог, Счётчик)

	НоваяСмена = Документы.КассоваяСмена.СоздатьДокумент();
	НоваяСмена.Дата         = ТекущаяДатаСеанса();
	НоваяСмена.ДатаНачала   = ТекущаяДатаСеанса();
	НоваяСмена.Статус       = Перечисления.СтатусыКассовойСмены.Открыта;

	// СМЕНА-1: запись документа
	Попытка
		НоваяСмена.Записать(РежимЗаписиДокумента.Запись);
		СменаСсылка = НоваяСмена.Ссылка;
		Утверждать(НЕ СменаСсылка.Пустая(),
			"СМЕНА-1: Создание документа КассоваяСмена", Лог, Счётчик);
	Исключение
		Утверждать(Ложь, "СМЕНА-1: Ошибка записи - " + ОписаниеОшибки(), Лог, Счётчик);
		Возврат;
	КонецПопытки;

	// СМЕНА-2: статус = Открыта
	Прочитана = СменаСсылка.ПолучитьОбъект();
	Утверждать(Прочитана.Статус = Перечисления.СтатусыКассовойСмены.Открыта,
		"СМЕНА-2: Статус после записи = Открыта", Лог, Счётчик);

	// СМЕНА-3: изменение статуса → Закрыта
	Прочитана.Статус       = Перечисления.СтатусыКассовойСмены.Закрыта;
	Прочитана.ДатаОкончания = ТекущаяДатаСеанса();
	Попытка
		Прочитана.Записать(РежимЗаписиДокумента.Запись);
		Утверждать(Прочитана.Статус = Перечисления.СтатусыКассовойСмены.Закрыта,
			"СМЕНА-3: Закрытие смены: Статус = Закрыта", Лог, Счётчик);
	Исключение
		Утверждать(Ложь, "СМЕНА-3: Ошибка закрытия - " + ОписаниеОшибки(), Лог, Счётчик);
	КонецПопытки;

	// Откат тестовых данных
	Попытка
		Прочитана.УстановитьПометкуУдаления(Истина);
	Исключение
	КонецПопытки;

КонецПроцедуры

// ─── Тесты Чека ККМ и Возврата ───────────────────────────────────────────

&НаСервереБезКонтекста
Процедура ПровестиТестыЧекаИВозврата(Лог, Счётчик)

	// Поиск необходимых справочников
	ЗапросКасса = Новый Запрос;
	ЗапросКасса.Текст = "ВЫБРАТЬ ПЕРВЫЕ 1
	|	Кассы.Ссылка КАК Ссылка
	|ИЗ Справочник.Кассы КАК Кассы
	|ГДЕ НЕ Кассы.ПометкаУдаления";
	РезКасса = ЗапросКасса.Выполнить();

	ЗапросТовар = Новый Запрос;
	ЗапросТовар.Текст = "ВЫБРАТЬ ПЕРВЫЕ 1
	|	Н.Ссылка КАК Ссылка
	|ИЗ Справочник.Номенклатура КАК Н
	|ГДЕ НЕ Н.ПометкаУдаления И НЕ Н.ЭтоГруппа";
	РезТовар = ЗапросТовар.Выполнить();

	ЗапросСклад = Новый Запрос;
	ЗапросСклад.Текст = "ВЫБРАТЬ ПЕРВЫЕ 1
	|	Склады.Ссылка КАК Ссылка
	|ИЗ Справочник.Склады КАК Склады
	|ГДЕ НЕ Склады.ПометкаУдаления";
	РезСклад = ЗапросСклад.Выполнить();

	Если РезКасса.Пустой() Тогда
		Лог.Добавить("  [ПРОПУСК] Нет ни одной кассы в базе — тесты чеков пропущены.");
		Возврат;
	КонецЕсли;
	Если РезТовар.Пустой() Тогда
		Лог.Добавить("  [ПРОПУСК] Нет номенклатуры в базе — тесты чеков пропущены.");
		Возврат;
	КонецЕсли;

	ВыбКасса  = РезКасса.Выгрузить()[0].Ссылка;
	ВыбТовар  = РезТовар.Выгрузить()[0].Ссылка;
	ВыбСклад  = ?(РезСклад.Пустой(), Справочники.Склады.ПустаяСсылка(), РезСклад.Выгрузить()[0].Ссылка);

	// ─── ЧЕК-1: создание документа ЧекККМ ────
	НовыйЧек = Документы.ЧекККМ.СоздатьДокумент();
	НовыйЧек.Дата           = ТекущаяДатаСеанса();
	НовыйЧек.Касса          = ВыбКасса;
	НовыйЧек.Склад          = ВыбСклад;
	НовыйЧек.Статус         = Перечисления.СтатусыЧекаККМ.НеФискальный;

	СтрТовар = НовыйЧек.Товары.Добавить();
	СтрТовар.Номенклатура = ВыбТовар;
	СтрТовар.Количество   = 2;
	СтрТовар.Цена         = 100;
	СтрТовар.Сумма        = СтрТовар.Количество * СтрТовар.Цена;

	СтрОплата = НовыйЧек.Оплата.Добавить();
	СтрОплата.ВидОплаты    = Перечисления.ВидыОплаты.Наличные;
	СтрОплата.КассаОплаты  = ВыбКасса;
	СтрОплата.Сумма        = СтрТовар.Сумма;

	НовыйЧек.СуммаДокумента = СтрТовар.Сумма;

	ЧекСсылка = Неопределено;
	Попытка
		НовыйЧек.Записать(РежимЗаписиДокумента.Запись);
		ЧекСсылка = НовыйЧек.Ссылка;
		Утверждать(НЕ ЧекСсылка.Пустая(),
			"ЧЕК-1: Создание документа ЧекККМ", Лог, Счётчик);
	Исключение
		Утверждать(Ложь, "ЧЕК-1: Ошибка - " + ОписаниеОшибки(), Лог, Счётчик);
		Возврат;
	КонецПопытки;

	// ─── ЧЕК-2: Сумма строки = 200 ────
	ПрочитанЧек = ЧекСсылка.ПолучитьОбъект();
	Утверждать(ПрочитанЧек.Товары[0].Сумма = 200,
		"ЧЕК-2: Сумма строки товара = 200 (факт: " + ПрочитанЧек.Товары[0].Сумма + ")", Лог, Счётчик);

	// ─── ЧЕК-3: СуммаДокумента = 200 ────
	Утверждать(ПрочитанЧек.СуммаДокумента = 200,
		"ЧЕК-3: СуммаДокумента = 200 (факт: " + ПрочитанЧек.СуммаДокумента + ")", Лог, Счётчик);

	// ─── ЧЕК-4: Статус = НеФискальный ────
	Утверждать(ПрочитанЧек.Статус = Перечисления.СтатусыЧекаККМ.НеФискальный,
		"ЧЕК-4: Статус = НеФискальный", Лог, Счётчик);

	// ─── ЧЕК-5: 1 строка в Товары ────
	Утверждать(ПрочитанЧек.Товары.Количество() = 1,
		"ЧЕК-5: Количество строк ТЧ Товары = 1", Лог, Счётчик);

	// ─── ЧЕК-6: 1 строка в Оплата ────
	Утверждать(ПрочитанЧек.Оплата.Количество() = 1,
		"ЧЕК-6: Количество строк ТЧ Оплата = 1", Лог, Счётчик);

	// ─── ВОЗВРАТ-1: создание ─────────────────
	НовыйВозврат = Документы.ВозвратТовараОтПокупателя.СоздатьДокумент();
	НовыйВозврат.Дата               = ТекущаяДатаСеанса();
	НовыйВозврат.ДокументОснование  = ЧекСсылка;
	НовыйВозврат.Склад              = ВыбСклад;
	НовыйВозврат.ФискальныйВозврат  = Ложь;

	Для Каждого СтрЧека Из ПрочитанЧек.Товары Цикл
		НоваяСтрВозврат = НовыйВозврат.Товары.Добавить();
		НоваяСтрВозврат.Номенклатура = СтрЧека.Номенклатура;
		НоваяСтрВозврат.Количество   = СтрЧека.Количество;
		НоваяСтрВозврат.Цена         = СтрЧека.Цена;
		НоваяСтрВозврат.Сумма        = СтрЧека.Сумма;
	КонецЦикла;

	Попытка
		НовыйВозврат.Записать(РежимЗаписиДокумента.Запись);
		Утверждать(НЕ НовыйВозврат.Ссылка.Пустая(),
			"ВОЗВРАТ-1: Создание документа ВозвратТовараОтПокупателя", Лог, Счётчик);
	Исключение
		Утверждать(Ложь, "ВОЗВРАТ-1: Ошибка - " + ОписаниеОшибки(), Лог, Счётчик);
	КонецПопытки;

	// ─── ВОЗВРАТ-2: ДокументОснование = чек ─
	Утверждать(НовыйВозврат.ДокументОснование = ЧекСсылка,
		"ВОЗВРАТ-2: ДокументОснование совпадает с чеком", Лог, Счётчик);

	// ─── ВОЗВРАТ-3: сумма возврата = сумма чека ─
	СуммаВозврата = 0;
	Для Каждого Стр Из НовыйВозврат.Товары Цикл
		СуммаВозврата = СуммаВозврата + Стр.Сумма;
	КонецЦикла;
	Утверждать(СуммаВозврата = ПрочитанЧек.СуммаДокумента,
		"ВОЗВРАТ-3: Сумма возврата = Сумме чека (" + ПрочитанЧек.СуммаДокумента + ")", Лог, Счётчик);

	// Откат тестовых данных
	Попытка
		НовыйВозврат.УстановитьПометкуУдаления(Истина);
	Исключение
	КонецПопытки;
	Попытка
		ПрочитанЧек.УстановитьПометкуУдаления(Истина);
	Исключение
	КонецПопытки;

КонецПроцедуры

#КонецОбласти
"""

# ── Функция записи файла ───────────────────────────────────────────────────

def write(path: pathlib.Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  OK  {path.relative_to(ROOT)}")

# ── Создание файлов в ОБЕИХ папках ────────────────────────────────────────

print("=== Создание файлов ТестыРМК ===")

for cfg in CONFIGS:
    dp_dir = cfg / "DataProcessors"
    write(dp_dir / "ТестыРМК.xml",                                                    DATAPROCESSOR_XML)
    write(dp_dir / "ТестыРМК" / "Forms" / "Форма.xml",                               FORMA_DESCRIPTOR_XML)
    write(dp_dir / "ТестыРМК" / "Forms" / "Форма" / "Ext" / "Form.xml",              FORM_XML)
    write(dp_dir / "ТестыРМК" / "Forms" / "Форма" / "Ext" / "Form" / "Module.bsl",   MODULE_BSL)

print()

# ── Обновление Configuration.xml ──────────────────────────────────────────

OLD_CONF = "\t\t\t<DataProcessor>ТестовоеЗаполнениеДанных</DataProcessor>"
NEW_CONF = OLD_CONF + "\n\t\t\t<DataProcessor>ТестыРМК</DataProcessor>"

print("=== Обновление Configuration.xml ===")
for cfg in CONFIGS:
    conf_file = cfg / "Configuration.xml"
    text = conf_file.read_text(encoding="utf-8")
    if "ТестыРМК" in text:
        print(f"  SKIP (уже есть): {conf_file.relative_to(ROOT)}")
        continue
    if OLD_CONF not in text:
        print(f"  WARN: якорная строка не найдена в {conf_file.relative_to(ROOT)}")
        continue
    text = text.replace(OLD_CONF, NEW_CONF, 1)
    conf_file.write_text(text, encoding="utf-8")
    print(f"  OK  {conf_file.relative_to(ROOT)}")

print()

# ── Обновление ConfigDumpInfo.xml ─────────────────────────────────────────

OLD_CDI = '\t\t<Metadata name="DataProcessor.ТестовоеЗаполнениеДанных.ObjectModule" id="4562ecee-34ca-43f6-a8ac-d5fd03eebcba.0" configVersion="0eaa043101e5584da3d1bc203d4dc1be00000000" />'

NEW_CDI = OLD_CDI + f"""
\t\t<Metadata name="DataProcessor.ТестыРМК" id="{MAIN_UUID}" configVersion="a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d600000000" />
\t\t<Metadata name="DataProcessor.ТестыРМК.Form.Форма" id="{FORM_UUID}" configVersion="b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e700000000" />
\t\t<Metadata name="DataProcessor.ТестыРМК.Form.Форма.Form" id="{FORM_UUID}.0" configVersion="c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f800000000" />
\t\t<Metadata name="DataProcessor.ТестыРМК.ObjectModule" id="{MAIN_UUID}.0" configVersion="d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a900000000" />"""

print("=== Обновление ConfigDumpInfo.xml ===")
for cfg in CONFIGS:
    cdi_file = cfg / "ConfigDumpInfo.xml"
    text = cdi_file.read_text(encoding="utf-8")
    if "DataProcessor.ТестыРМК" in text:
        print(f"  SKIP (уже есть): {cdi_file.relative_to(ROOT)}")
        continue
    if OLD_CDI not in text:
        print(f"  WARN: якорная строка не найдена в {cdi_file.relative_to(ROOT)}")
        continue
    text = text.replace(OLD_CDI, NEW_CDI, 1)
    cdi_file.write_text(text, encoding="utf-8")
    print(f"  OK  {cdi_file.relative_to(ROOT)}")

print()
print("=== ГОТОВО ===")
