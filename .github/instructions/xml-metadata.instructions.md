---
name: 'XML Metadata Standards'
description: 'Правила создания XML-объектов метаданных 1С и multi-file чеклист'
applyTo: 'Конфигурация/**/*.xml'
---

# Правила XML-объектов метаданных 1С

## Обязательный порядок создания XML

1. **Взять шаблон** из `Документация/Шаблоны/` (template-catalog.xml, template-document.xml и т.д.)
2. **Скопировать заголовок целиком** (ВСЕ xmlns) — НЕ сокращать!
3. **Заменить плейсхолдеры** `{{...}}` реальными значениями
4. **UUID** — формат `xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx` (lowercase hex)
5. **id элементов формы** — последовательная нумерация с 1, AutoCommandBar формы = -1
6. **Проверить** через `get_errors`

## Частые ошибки XML

| ❌ ОШИБКА | ✅ ПРАВИЛЬНО |
|-----------|-------------|
| Неполный набор xmlns | Копировать ВЕСЬ заголовок из шаблона `Документация/Шаблоны/` |
| `version="2.0"` | `version="2.20"` |
| Отсутствие InternalInfo/GeneratedType | Обязательно для справочников, документов, регистров |
| UUID не в формате | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` (lowercase hex) |
| Пропущенные дочерние элементы | ContextMenu, ExtendedTooltip для каждого элемента формы |
| Не обновлён Configuration.xml | Добавить `<ТипОбъекта>Имя</ТипОбъекта>` в `<ChildObjects>` |
| Не обновлён ConfigDumpInfo.xml | Добавить `<Metadata name="Тип.Имя" id="UUID">` |
| Дублирующиеся id элементов формы | Каждый id уникален внутри Form.xml |
| `FillFromFillingValue`/`FillValue` у обработки | НЕ существует для DataProcessor.Attribute! Только для Document/Catalog |

## Multi-file чеклист: НОВЫЙ объект метаданных

**Все шаги обязательны. Пропуск любого → ошибка загрузки конфигурации.**

| # | Файл | Действие | Пример |
|---|------|----------|--------|
| 1 | `<Тип>/<Имя>.xml` | Создать из шаблона | `Documents/Заказ.xml` |
| 2 | `Configuration.xml` | Добавить `<Тип>Имя</Тип>` в `<ChildObjects>` | `<Document>Заказ</Document>` |
| 3 | `ConfigDumpInfo.xml` | Добавить `<Metadata name="Тип.Имя" id="UUID">` | см. формат ниже |
| 4 | `<Тип>/<Имя>/Ext/ObjectModule.bsl` | Модуль если нужна логика | Обработка проведения |
| 5 | `Subsystems/<Подсистема>.xml` | Добавить в `<Content>` | `<xr:Item>Document.Заказ</xr:Item>` |

## Multi-file чеклист: ФОРМА объекта

| # | Файл | Действие |
|---|------|----------|
| 1 | `<Тип>/<Имя>.xml` | Добавить `<Form>ИмяФормы</Form>` в `<ChildObjects>` |
| 2 | `<Тип>/<Имя>.xml` | Заполнить `<DefaultObjectForm>` если основная форма |
| 3 | `Forms/<ИмяФормы>.xml` | Создать описатель формы (uuid + owner) |
| 4 | `Forms/<ИмяФормы>/Ext/Form.xml` | XML формы из шаблона |
| 5 | `Forms/<ИмяФормы>/Ext/Form/Module.bsl` | Модуль формы |
| 6 | `ConfigDumpInfo.xml` | Добавить запись для формы |

## Multi-file чеклист: РЕКВИЗИТ

| # | Файл | Действие |
|---|------|----------|
| 1 | `<Тип>/<Имя>.xml` | Добавить `<Attribute uuid="...">` в `<ChildObjects>` |
| 2 | `ConfigDumpInfo.xml` | Добавить `<Metadata name="Тип.Имя.Attribute.Реквизит" id="UUID"/>` |
| 3 | Формы (если есть) | Добавить `<InputField>` с `<DataPath>Объект.Реквизит</DataPath>` |

## Формат ConfigDumpInfo.xml

```xml
<Metadata name="Document.НовыйДокумент" id="UUID-ОБЪЕКТА" configVersion="СЛУЧАЙНАЯ-HEX-СТРОКА32-00000000">
    <Metadata name="Document.НовыйДокумент.Attribute.Склад" id="UUID-РЕКВИЗИТА"/>
    <Metadata name="Document.НовыйДокумент.TabularSection.Товары" id="UUID-ТЧ"/>
    <Metadata name="Document.НовыйДокумент.TabularSection.Товары.Attribute.Номенклатура" id="UUID-КОЛОНКИ"/>
    <Metadata name="Document.НовыйДокумент.Form.ФормаДокумента" id="UUID-ФОРМЫ"/>
</Metadata>
```

**configVersion:** 32 hex-символа + `00000000`.

## Маппинг типов → папок

| Тип в Configuration.xml | Папка на диске |
|------------------------|----------------|
| `<Catalog>Имя</Catalog>` | `Catalogs/Имя.xml` + `Catalogs/Имя/` |
| `<Document>Имя</Document>` | `Documents/Имя.xml` + `Documents/Имя/` |
| `<Enum>Имя</Enum>` | `Enums/Имя.xml` |
| `<Report>Имя</Report>` | `Reports/Имя.xml` + `Reports/Имя/` |
| `<DataProcessor>Имя</DataProcessor>` | `DataProcessors/Имя.xml` + `DataProcessors/Имя/` |
| `<CommonModule>Имя</CommonModule>` | `CommonModules/Имя.xml` + `CommonModules/Имя/Ext/Module.bsl` |
| `<AccumulationRegister>Имя</AccumulationRegister>` | `AccumulationRegisters/Имя.xml` |
| `<InformationRegister>Имя</InformationRegister>` | `InformationRegisters/Имя.xml` |
| `<Constant>Имя</Constant>` | `Constants/Имя.xml` |
| `<Subsystem>Имя</Subsystem>` | `Subsystems/Имя.xml` |

## Структура объекта с формой

```
Documents/
  НовыйДокумент.xml
  НовыйДокумент/
    Ext/
      ObjectModule.bsl
    Forms/
      ФормаДокумента.xml           ← описатель (uuid + owner)
      ФормаДокумента/
        Ext/
          Form.xml                  ← XML формы
          Form/
            Module.bsl              ← BSL-обработчики
```
