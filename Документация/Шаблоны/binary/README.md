# Бинарные шаблоны форм 1С

Канонические XML-шаблоны, извлечённые из реального дампа конфигурации 1С 8.3.27.
Гарантируют корректную структуру, xmlns и формат при генерации новых форм.

## Шаблоны

| Файл | Тип | Описание |
|------|-----|----------|
| `descriptor.xml` | Универсальный | Дескриптор формы (MetaDataObject). xmlns: `http://v8.1c.ru/8.3/MDClasses` |
| `catalog-element.xml` | Form.xml | Форма элемента справочника. `UseForFoldersAndItems=Items`, `CatalogObject` |
| `catalog-group.xml` | Form.xml | Форма группы справочника. `UseForFoldersAndItems=Folders`, `CatalogObject` |
| `catalog-list.xml` | Form.xml | Форма списка справочника. `DynamicList`, `MainTable` |
| `document.xml` | Form.xml | Форма документа. `AutoTime`, `UsePostingMode`, `RegisterRecords` |
| `dataprocessor.xml` | Form.xml | Форма обработки. `DataProcessorObject` |
| `module-form.bsl` | BSL | Пустой модуль формы с областями |

## Плейсхолдеры

| Плейсхолдер | Где используется | Значение |
|-------------|-----------------|----------|
| `{{FORM_UUID}}` | descriptor.xml | UUID формы (v4, lowercase) |
| `{{FORM_NAME}}` | descriptor.xml | Имя формы (ФормаДокумента, ФормаЭлемента) |
| `{{FORM_SYNONYM}}` | descriptor.xml | Синоним (Форма документа) |
| `{{OBJECT_NAME}}` | Все Form.xml | Имя объекта-владельца (Номенклатура, ПриходТовара) |
| `{{META_TYPE}}` | catalog-list.xml | Тип метаданных (Catalog, Document) |

## Различия xmlns

**Дескриптор** (descriptor.xml):
```
xmlns="http://v8.1c.ru/8.3/MDClasses"
+ cmi, xen, xpr (только в дескрипторе!)
```

**Form.xml** (все остальные):
```
xmlns="http://v8.1c.ru/8.3/xcf/logform"
+ dcscor, dcssch, dcsset (только в Form.xml!)
```

## Генератор

```bash
python scripts/_generate_form.py --type catalog-element --object Номенклатура --form ФормаЭлемента
```

Подробная справка: `python scripts/_generate_form.py --help`

## Важно

- Генератор записывает файлы с **BOM (ef bb bf) + CRLF** — это обязательно для 1С
- Файлы создаются в **обоих** путях: `Конфигурация/Проверка/` и `Конфигурация/`
- После генерации нужно обновить `Configuration.xml`, `ConfigDumpInfo.xml` и родительский `.xml`
