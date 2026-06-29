---
description: "Use when creating, editing, or reviewing XML files of 1C:Enterprise 8.3.27 configuration. Covers namespace headers, version requirements, metadata structure, Configuration.xml, ConfigDumpInfo.xml, UUID format, and file encoding."
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

## Разграничение ролей: Скелет ↔ Содержимое

> ⚠️ **ВАЖНО (новый подход):**
>
> **Пользователь** (в Конфигураторе 1С) создаёт **скелет**:
> - Пустой объект метаданных (Catalog/Document/Register/Report/DataProcessor)
> - Пустую форму
> - Делает Dump → автоматически регистрируется в `Configuration.xml` и `ConfigDumpInfo.xml`
>
> **Агент** заполняет **содержимое** существующих XML:
> - Реквизиты, ТЧ, элементы форм, макеты, команды, включение в подсистемы — через `1c-xml-editor` (skill)
> - BSL-модули — через `1c-coder` / `1c-form-builder`
>
> **Запрещено агенту:**
> - Создавать новый объект метаданных с нуля
> - Редактировать `<ChildObjects>` корня `Configuration.xml`
> - Создавать форму с нуля если её файла нет
> - Удалять/переименовывать объекты
>
> Исключение: оркестратор явно передал флаг `xml_fallback=true` (полное создание через XML — редкий аварийный режим).

## Multi-file чеклист

### Случай A: Пользователь создал скелет (стандартный workflow)

После Dump'а файлы автоматически содержат регистрацию объекта. Агент только:

1. **XML объекта** — добавляет `<Attribute>`, `<TabularSection>`, `<Template>`, `<Command>` в `<ChildObjects>`
2. **Form.xml** — заполняет `<ChildItems>` существующей пустой формы
3. **ConfigDumpInfo.xml** — добавляет дочерние `<Metadata>` для новых реквизитов/ТЧ/макетов/команд (UUID те же, что в XML объекта)
4. **Подсистема** — `<xr:Item>Тип.Имя</xr:Item>` в `<Content>` (если нужно)
5. **Модули** — ObjectModule.bsl, ManagerModule.bsl, Module.bsl формы

Полный workflow → skill `1c-xml-editor`.

### Случай B: `xml_fallback=true` (создание с нуля)

Обновить ВСЕ:

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

## Рабочая папка конфигурации

Конфигурация хранится в одном каталоге:
- `Конфигурация/` — рабочая копия, из неё выполняется деплой в ИБ

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

Для разведки задачи первым источником является `context-mcp`: `context_resolve` → `context_get`.
В XML/BSL/документацию идём только если нужной информации нет в выданном контексте или нужна
актуальная проверка перед правкой.

ИБ (информационная база) через 1С MCP — единственный источник истины по структуре метаданных.
XML-файлы на диске могут отставать от ИБ. ПЕРЕД изменениями:

1. `context-mcp` → получить `context_id`, целевой объект, структуру, пути и gaps.
2. `mcp_dev-mcp_dev_dump` — синхронизация ИБ → файлы.
3. 1С MCP → `get_metadata_structure` — актуально проверить структуру объекта, если этого нет в context-mcp или требуется верификация.
4. Только после этого — вносить изменения.

## Обязательная проверка

После ЛЮБОГО изменения XML — вызвать `get_errors` и запустить `mcp_dev-mcp_dev_validate`.
