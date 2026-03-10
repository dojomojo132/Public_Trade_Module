---
name: 1c-form-generator
description: "Generate 1C:Enterprise managed forms (Form.xml, descriptor, Module.bsl). Use when creating new forms for catalogs, documents, or data processors. Covers form structure, element IDs, BOM encoding, required children, and dual-folder synchronization."
---

# Генерация управляемых форм 1С

## Когда использовать

- Создание новой формы для справочника, документа, обработки
- Добавление элементов на существующую форму
- Исправление структуры Form.xml (id, дочерние элементы, кодировка)

## Генератор форм (рекомендуемый способ)

```powershell
# Типы: catalog-element | catalog-group | catalog-list | document | dataprocessor
python scripts/_generate_form.py --type catalog-element --object Номенклатура --form ФормаЭлемента
python scripts/_generate_form.py --type document --object РасходТовара --form ФормаДокумента
python scripts/_generate_form.py --type dataprocessor --object УправлениеСканером --form Форма

# Проверить наличие шаблонов:
python scripts/_generate_form.py --check
```

Генератор создаёт 3 файла в ОБОИХ путях (`Конфигурация/` и `Конфигурация/Проверка/`) и гарантирует корректный BOM + CRLF.

## Структура файлов формы

```
<Тип>/<Объект>/
  Forms/
    <ИмяФормы>.xml                    ← Дескриптор формы (ссылка)
    <ИмяФормы>/
      Ext/
        Form.xml                       ← XML формы (элементы, реквизиты, команды)
        Form/
          Module.bsl                   ← Модуль формы (BSL обработчики)
```

## Дескриптор формы (Forms/ИмяФормы.xml)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses"
    xmlns:xr="http://v8.1c.ru/8.3/xcf/readable"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    version="2.20">
	<Form uuid="{{UUID_ФОРМЫ}}" owner="{{UUID_ВЛАДЕЛЬЦА}}">
		<Properties>
			<Name>ИмяФормы</Name>
		</Properties>
	</Form>
</MetaDataObject>
```

## Правила ID элементов формы

| Элемент | Правило ID |
|---------|-----------|
| `AutoCommandBar` формы | ВСЕГДА `id="-1"` |
| Остальные элементы | Последовательная нумерация с `1` |
| `ContextMenu` | `id=N+1` от родителя |
| `ExtendedTooltip` | `id=N+2` от родителя |

**Для Table (самый сложный элемент):**

```
Товары (Table)           id=9
  ContextMenu            id=10
  AutoCommandBar         id=11
  ExtendedTooltip        id=12
  SearchStringAddition   id=13
  ViewStatusAddition     id=14
  SearchControlAddition  id=15
  ТоварыНоменклатура     id=16
    ContextMenu          id=17
    ExtendedTooltip      id=18
```

## Обязательные дочерние элементы

КАЖДЫЙ элемент формы ОБЯЗАН иметь:

- `<ContextMenu name="ИмяЭлементаКонтекстноеМеню" id="X"/>`
- `<ExtendedTooltip name="ИмяЭлементаРасширеннаяПодсказка" id="Y"/>`

Оба с уникальными id в последовательности.

## Кодировка файлов формы

| Файл | BOM | Перевод строк |
|------|-----|--------------|
| Form.xml | UTF-8 BOM (`EF BB BF`) | CRLF |
| Module.bsl | UTF-8 BOM (`EF BB BF`) | CRLF |
| Дескриптор .xml | UTF-8 (без BOM допустимо) | CRLF |

Генератор `_generate_form.py` гарантирует правильную кодировку. При ручном создании — обязательно проверить BOM.

## Чеклист после создания формы

1. **Родительский объект** — добавить `<Form>ИмяФормы</Form>` в `<ChildObjects>`
2. **DefaultObjectForm** — заполнить если это основная форма
3. **ConfigDumpInfo.xml** — добавить `<Metadata name="Тип.Объект.Form.ИмяФормы" id="UUID"/>`
4. **Двойная структура** — файлы в ОБОИХ каталогах (генератор делает автоматически)
5. **get_errors** — проверить Form.xml и Module.bsl

## Основные элементы формы

| Элемент | Назначение | Ключевое свойство |
|---------|-----------|-------------------|
| `InputField` | Ввод данных | `DataPath="Объект.Реквизит"` |
| `LabelField` | Отображение | Только для просмотра |
| `CheckBoxField` | Флажок | `CheckBoxType`: Standard/Switcher |
| `Button` | Кнопка/команда | `CommandName` — имя команды |
| `Table` | Табличная часть | `DataPath="Объект.ТабличнаяЧасть"` |
| `UsualGroup` | Группа элементов | `Group`: Horizontal/Vertical |
| `Pages`/`Page` | Вкладки | `PagesRepresentation`: TabsOnTop/... |
| `LabelDecoration` | Декоративный текст | Нет привязки к данным |

## Типовые события формы

```xml
<Events>
    <Event name="OnCreateAtServer">ПриСозданииНаСервере</Event>
    <Event name="OnOpen">ПриОткрытии</Event>
    <Event name="BeforeWrite">ПередЗаписью</Event>
    <Event name="AfterWrite">ПослеЗаписи</Event>
</Events>
```

## Ссылки на ресурсы

- Бинарные шаблоны форм: `Документация/Шаблоны/binary/`
- Генератор: `scripts/_generate_form.py`
- Стандарты элементов: `Документация/Технические_стандарты/form-elements.md`
