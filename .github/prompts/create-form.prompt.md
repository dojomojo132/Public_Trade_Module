---
description: 'Создание формы для объекта метаданных 1С: описатель → Form.xml → Module.bsl → CDI → валидация'
mode: agent
tools:
  - mcp_mcp_1c_torgov/*
---

# Создание формы для объекта метаданных

## Входные данные
- Объект-владелец: {{ТИП}}.{{ИМЯ}} (например Document.ЧекККМ, Catalog.Номенклатура)
- Имя формы: {{ИМЯ_ФОРМЫ}} (например ФормаДокумента, ФормаЭлемента)
- Тип формы: документ / справочник / обработка

## Алгоритм (выполнить ВСЕ шаги)

### Шаг 1: Проверка владельца
1. Прочитать XML объекта-владельца
2. Запомнить UUID владельца
3. Запомнить ВСЕ реквизиты и табличные части
4. Проверить что формы ещё нет

### Шаг 2: Обновить XML владельца
1. Добавить `<Form>{{ИМЯ_ФОРМЫ}}</Form>` в `<ChildObjects>`
2. Если основная форма — заполнить `<DefaultObjectForm>`

### Шаг 3: Описатель формы
Файл: `{{ПАПКА}}/{{ИМЯ}}/Forms/{{ИМЯ_ФОРМЫ}}.xml`
```xml
<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses"
    xmlns:xr="http://v8.1c.ru/8.3/xcf/readable"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    version="2.20">
	<Form uuid="{{UUID_ФОРМЫ}}" owner="{{UUID_ВЛАДЕЛЬЦА}}">
		<Properties>
			<Name>{{ИМЯ_ФОРМЫ}}</Name>
		</Properties>
	</Form>
</MetaDataObject>
```

### Шаг 4: Form.xml
Файл: `{{ПАПКА}}/{{ИМЯ}}/Forms/{{ИМЯ_ФОРМЫ}}/Ext/Form.xml`

1. Взять шаблон из `Документация/Шаблоны/template-form-*.xml`
2. Правила id и обязательные дочерние элементы: [form-elements instructions](../instructions/form-elements.instructions.md)
3. Для каждого реквизита — `<InputField>` с `<DataPath>Объект.ИмяРеквизита</DataPath>`
4. Для каждой ТЧ — `<Table>` с колонками

### Шаг 5: Module.bsl
Файл: `{{ПАПКА}}/{{ИМЯ}}/Forms/{{ИМЯ_ФОРМЫ}}/Ext/Form/Module.bsl`
```bsl
#Область ОбработчикиСобытийФормы

&НаСервере
Процедура ПриСозданииНаСервере(Отказ, СтандартнаяОбработка)

КонецПроцедуры

#КонецОбласти

#Область ОбработчикиКомандФормы

#КонецОбласти

#Область СлужебныеПроцедурыИФункции

#КонецОбласти
```

### Шаг 6: ConfigDumpInfo.xml
Следовать [чеклисту формы](../instructions/xml-metadata.instructions.md) — секция "Multi-file чеклист: ФОРМА объекта".

### Шаг 7: Валидация
1. `get_errors` на Form.xml и Module.bsl
2. `validate-config.ps1` → 0 ошибок
3. Проверить: все id уникальны, ContextMenu/ExtendedTooltip на месте
