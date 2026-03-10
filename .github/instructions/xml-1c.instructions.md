---
description: "Use when creating, editing, or reviewing XML files of 1C:Enterprise 8.3.27 configuration. Covers namespace headers, version requirements, metadata structure, Configuration.xml, ConfigDumpInfo.xml, UUID format, and dual-folder synchronization."
applyTo: "**/*.xml"
---

# Стандарты XML конфигурации 1С:Предприятие 8.3.27

## Эталонный заголовок MetaDataObject

ВСЕГДА копировать ПОЛНЫЙ набор xmlns из шаблонов `Документация/Шаблоны/`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses"
    xmlns:app="http://v8.1c.ru/8.2/managed-application/core"
    xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config"
    xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi"
    xmlns:ent="http://v8.1c.ru/8.1/data/enterprise"
    xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform"
    xmlns:style="http://v8.1c.ru/8.1/data/ui/style"
    xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system"
    xmlns:v8="http://v8.1c.ru/8.1/data/core"
    xmlns:v8ui="http://v8.1c.ru/8.1/data/ui"
    xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web"
    xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows"
    xmlns:xen="http://v8.1c.ru/8.3/xcf/enums"
    xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef"
    xmlns:xr="http://v8.1c.ru/8.3/xcf/readable"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    version="2.20">
```

## Критические правила

| Правило | Детали |
|---------|--------|
| `version` | ВСЕГДА `"2.20"` — НИКОГДА `"2.0"` |
| xmlns | ВСЕ пространства имён ОБЯЗАТЕЛЬНЫ — неполный набор = ошибка загрузки |
| UUID | Формат `xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx` (lowercase hex, RFC 4122 v4) |
| `InternalInfo/GeneratedType` | Обязательно для справочников, документов, регистров |
| Шаблоны | ВСЕГДА брать из `Документация/Шаблоны/` — НЕ писать с нуля |

## Multi-file чеклист (при создании нового объекта)

При создании ЛЮБОГО нового объекта метаданных — обновить ВСЕ:

1. **Объект** — `<Тип>/<Имя>.xml` (из шаблона)
2. **Configuration.xml** — `<Тип>Имя</Тип>` в `<ChildObjects>`
3. **ConfigDumpInfo.xml** — `<Metadata name="Тип.Имя" id="UUID" configVersion="...">`
4. **Подсистема** — `<xr:Item>Тип.Имя</xr:Item>` в `<Content>`
5. **Модули** — ObjectModule.bsl, ManagerModule.bsl если нужна логика

Пропуск ЛЮБОГО шага = ошибка загрузки конфигурации.

## ConfigDumpInfo.xml

```xml
<Metadata name="Document.НовыйДокумент" id="UUID" configVersion="RANDOM-HEX-32-CHARS00000000">
    <Metadata name="Document.НовыйДокумент.Attribute.Склад" id="UUID"/>
    <Metadata name="Document.НовыйДокумент.TabularSection.Товары" id="UUID">
        <Metadata name="Document.НовыйДокумент.TabularSection.Товары.Attribute.Номенклатура" id="UUID"/>
    </Metadata>
    <Metadata name="Document.НовыйДокумент.Form.ФормаДокумента" id="UUID"/>
</Metadata>
```

`configVersion` = 32 случайных hex-символа + `00000000` (8 нулей).

## Маппинг типов → папок

| Тип | Папка | Configuration.xml |
|-----|-------|-------------------|
| Справочник | `Catalogs/Имя.xml` | `<Catalog>Имя</Catalog>` |
| Документ | `Documents/Имя.xml` | `<Document>Имя</Document>` |
| Перечисление | `Enums/Имя.xml` | `<Enum>Имя</Enum>` |
| Отчёт | `Reports/Имя.xml` | `<Report>Имя</Report>` |
| Обработка | `DataProcessors/Имя.xml` | `<DataProcessor>Имя</DataProcessor>` |
| Общий модуль | `CommonModules/Имя.xml` | `<CommonModule>Имя</CommonModule>` |
| Регистр накопления | `AccumulationRegisters/Имя.xml` | `<AccumulationRegister>Имя</AccumulationRegister>` |
| Регистр сведений | `InformationRegisters/Имя.xml` | `<InformationRegister>Имя</InformationRegister>` |

## Двойная структура каталогов

В проекте PTM конфигурация хранится в двух каталогах:
- `Конфигурация/` — основная рабочая копия
- `Конфигурация/Проверка/` — зеркало для загрузки

При изменении файлов — синхронизировать оба каталога через `python scripts/_smart_sync.py`.

## Формы

Форма состоит из 3 файлов — создавать через генератор:
```
python scripts/_generate_form.py --type <тип> --object <Объект> --form <ИмяФормы>
```

Ручное создание Form.xml требует BOM (EF BB BF) + CRLF. Генератор гарантирует корректную кодировку.

## Типичные ошибки (НЕ допускать)

| ❌ Ошибка | ✅ Правильно |
|-----------|-------------|
| Неполный набор xmlns | Копировать ВЕСЬ заголовок из шаблона |
| `version="2.0"` | `version="2.20"` |
| Отсутствие InternalInfo/GeneratedType | Обязательно для справочников, документов, регистров |
| Не обновлён Configuration.xml | `<ТипОбъекта>Имя</ТипОбъекта>` в `<ChildObjects>` |
| Не обновлён ConfigDumpInfo.xml | `<Metadata name="Тип.Имя" id="UUID">` |
| Дублирующиеся id элементов формы | Каждый id УНИКАЛЕН внутри Form.xml |
| `FillFromFillingValue` у обработки | НЕ существует для DataProcessor.Attribute |

## Источник истины

ИБ (информационная база) через MCP — единственный источник истины по структуре метаданных. XML-файлы на диске могут отставать от ИБ. ПЕРЕД изменениями:

1. `deploy-config.ps1 -Action Dump` — синхронизация ИБ → файлы
2. MCP → `get_metadata_structure` — проверить структуру объекта
3. Только после этого — вносить изменения

## Обязательная проверка

После ЛЮБОГО изменения XML — вызвать `get_errors` и запустить `validate-config.ps1`.
