---
name: 1c-xml-editor
description: "Edit existing 1C:Enterprise 8.3.27 metadata XML files: add attributes/tabular sections to objects, add controls to existing forms, register templates/commands, sync ConfigDumpInfo.xml, manage subsystem content. Use when the user has already created the empty skeleton (object + empty form) in Configurator and the agent needs to fill the content. Does NOT create new metadata objects from scratch — that is always done by the user in Configurator."
---

# Редактирование существующих XML конфигурации 1С

> **Принцип:** Пользователь создаёт **скелет** в Конфигураторе (пустой объект + пустая форма + Dump → автоматически появляется регистрация в `Configuration.xml` и `ConfigDumpInfo.xml`). Агент заполняет **содержимое** (реквизиты, ТЧ, элементы формы, макеты, команды, подсистемы).

## Когда использовать

| Задача | Применить? |
|--------|-----------|
| Добавить реквизит в существующий справочник/документ | ✅ |
| Добавить табличную часть в существующий объект | ✅ |
| Добавить элементы (поля, таблицы, кнопки) в существующий пустой Form.xml | ✅ |
| Добавить макет (Template) в отчёт/обработку/документ | ✅ |
| Добавить команду объекта (Command) | ✅ |
| Включить объект в подсистему (`<xr:Item>` в Subsystems Content) | ✅ |
| Синхронизировать `ConfigDumpInfo.xml` после добавления реквизитов/ТЧ/форм | ✅ |
| **Создать новый объект** (Catalog/Document/Register/Report/DataProcessor) с нуля | ❌ → пользователь в Конфигураторе |
| **Удалить** объект | ❌ → пользователь в Конфигураторе |
| Изменить тип/имя объекта | ❌ → пользователь в Конфигураторе |
| Создать **новую** форму с нуля | ❌ → пользователь в Конфигураторе |

## ОБЯЗАТЕЛЬНЫЙ pre-flight

ПЕРЕД любой правкой XML:

1. **MCP** → `mcp_1c_get_metadata_structure` — текущая структура объекта в ИБ
2. **MCP** → `mcp_1c_get_form_structure` (для форм) — текущие элементы и их ID
3. **Прочитать** целевой XML-файл → понять текущее состояние
4. **Прочитать** соответствующий шаблон в `Документация/Шаблоны/` → формат блоков

## ОБЯЗАТЕЛЬНЫЙ post-flight

ПОСЛЕ каждой правки XML:

1. `get_errors` на изменённый файл
2. `get_errors` на `Конфигурация/ConfigDumpInfo.xml` (если синхронизировался)
3. Запуск `mcp_dev-mcp_dev_validate` → 0 ошибок
4. Передать управление агенту `closer` (деплой выполняется через `mcp_dev-mcp_dev_deploy`)

---

## 1. Добавление реквизита в объект

**Файл:** `Конфигурация/<Тип>/<Имя>.xml`

Реквизит вставляется в `<ChildObjects>`, после существующих `<Attribute>` (или первым, если их нет), но **до** `<TabularSection>` и `<Form>`.

**Шаблон:**
```xml
<Attribute uuid="GENERATE-UUID-V4">
    <Properties>
        <Name>ИмяРеквизита</Name>
        <Synonym>
            <v8:item>
                <v8:lang>ru</v8:lang>
                <v8:content>Синоним реквизита</v8:content>
            </v8:item>
        </Synonym>
        <Comment/>
        <Type>
            <v8:Type>v8:String</v8:Type>
            <v8:StringQualifiers>
                <v8:Length>50</v8:Length>
                <v8:AllowedLength>Variable</v8:AllowedLength>
            </v8:StringQualifiers>
        </Type>
        <PasswordMode>false</PasswordMode>
        <Format/>
        <EditFormat/>
        <ToolTip/>
        <MarkNegatives>false</MarkNegatives>
        <Mask/>
        <MultiLine>false</MultiLine>
        <ExtendedEdit>false</ExtendedEdit>
        <MinValue xsi:nil="true"/>
        <MaxValue xsi:nil="true"/>
        <FillFromFillingValue>false</FillFromFillingValue>
        <FillValue xsi:type="xs:decimal">0</FillValue>
        <FillChecking>DontCheck</FillChecking>
        <ChoiceFoldersAndItems>Items</ChoiceFoldersAndItems>
        <QuickChoice>DontUse</QuickChoice>
        <CreateOnInput>Use</CreateOnInput>
        <ChoiceForm/>
        <LinkByType/>
        <ChoiceHistoryOnInput>Auto</ChoiceHistoryOnInput>
        <Indexing>DontIndex</Indexing>
        <FullTextSearch>Use</FullTextSearch>
        <Use>ForItemAndGroup</Use>
        <DataHistory>Use</DataHistory>
    </Properties>
</Attribute>
```

**Типы реквизитов:**

| Назначение | `<v8:Type>` | Дополнительно |
|------------|-------------|---------------|
| Строка | `v8:String` | `<v8:StringQualifiers>` с `Length` |
| Число | `v8:Number` | `<v8:NumberQualifiers>` с `Digits`, `FractionDigits`, `AllowedSign` |
| Дата | `v8:Date` | `<v8:DateQualifiers>` с `DateFractions` (Date/DateTime/Time) |
| Булево | `v8:Boolean` | — |
| Ссылка на справочник | `cfg:CatalogRef.ИмяСправочника` | — |
| Ссылка на документ | `cfg:DocumentRef.ИмяДокумента` | — |
| Ссылка на перечисление | `cfg:EnumRef.ИмяПеречисления` | — |
| Составной тип | несколько `<v8:Type>` подряд | `<v8:TypeSet>` для общих типов |

**`FillFromFillingValue`:** удалить блок целиком для `DataProcessor.Attribute` — у обработок этого свойства нет.

После правки → синхронизировать `ConfigDumpInfo.xml` (см. раздел 5).

---

## 2. Добавление табличной части (TabularSection)

Вставляется в `<ChildObjects>` **после** всех `<Attribute>`, **до** `<Form>` и `<Template>`.

**Шаблон:**
```xml
<TabularSection uuid="GENERATE-UUID-V4">
    <Properties>
        <Name>ИмяТЧ</Name>
        <Synonym>
            <v8:item><v8:lang>ru</v8:lang><v8:content>Синоним</v8:content></v8:item>
        </Synonym>
        <Comment/>
        <ToolTip/>
        <FillChecking>DontCheck</FillChecking>
        <StandardAttributes>
            <StandardAttribute>
                <name>LineNumber</name>
                <FillChecking>DontCheck</FillChecking>
            </StandardAttribute>
        </StandardAttributes>
        <Use>ForItemAndGroup</Use>
        <DataHistory>Use</DataHistory>
    </Properties>
    <ChildObjects>
        <Attribute uuid="GENERATE-UUID-V4">
            <Properties>
                <Name>Номенклатура</Name>
                <Synonym><v8:item><v8:lang>ru</v8:lang><v8:content>Номенклатура</v8:content></v8:item></Synonym>
                <Type><v8:Type>cfg:CatalogRef.Номенклатура</v8:Type></Type>
                <!-- остальные обязательные свойства как у обычного реквизита -->
            </Properties>
        </Attribute>
        <!-- другие реквизиты ТЧ -->
    </ChildObjects>
</TabularSection>
```

После правки → синхронизировать `ConfigDumpInfo.xml`.

---

## 3. Добавление элемента в существующий Form.xml

**Файл:** `Конфигурация/<Тип>/<Объект>/Forms/<Форма>/Ext/Form.xml`

> ⚠️ **Кодировка обязательна:** UTF-8 BOM (`EF BB BF`) + CRLF. Любая правка ДОЛЖНА сохранить BOM.

### Правила ID

- `AutoCommandBar` формы → ВСЕГДА `id="-1"`
- Новые элементы получают **следующие свободные ID** в порядке возрастания
- Перед добавлением: прочитать Form.xml → найти максимальный текущий `id` (кроме -1) → новые ID начинаются с max+1
- Каждый id уникален в пределах Form.xml

### Обязательные дочерние элементы

КАЖДЫЙ функциональный элемент ОБЯЗАН содержать:
- `<ContextMenu name="ИмяКонтекстноеМеню" id="N+1"/>`
- `<ExtendedTooltip name="ИмяРасширеннаяПодсказка" id="N+2"/>`

### Цепочки ID для разных элементов

| Элемент | Дочерние |
|---------|----------|
| `InputField` (id=N) | ContextMenu (N+1), ExtendedTooltip (N+2) |
| `Table` (id=N) | ContextMenu (N+1), AutoCommandBar (N+2), ExtendedTooltip (N+3), SearchStringAddition (N+4), ViewStatusAddition (N+5), SearchControlAddition (N+6), затем колонки |
| `Button` (id=N) | ExtendedTooltip (N+1) |
| `UsualGroup` (id=N) | ContextMenu (N+1), ExtendedTooltip (N+2), затем дочерние элементы |
| `Pages` (id=N) | ContextMenu (N+1), ExtendedTooltip (N+2), затем `Page` |

### Пример: добавить InputField на форму

```xml
<ChildItems>
    <!-- существующие элементы, последний с id=8 -->
    <InputField id="9">
        <name>Склад</name>
        <Title><v8:item><v8:lang>ru</v8:lang><v8:content>Склад</v8:content></v8:item></Title>
        <ContextMenu name="СкладКонтекстноеМеню" id="10"/>
        <ExtendedTooltip name="СкладРасширеннаяПодсказка" id="11"/>
        <DataPath xmlns:d2p1="http://v8.1c.ru/8.1/data-composition-system/dataset/field">Объект.Склад</DataPath>
    </InputField>
</ChildItems>
```

### Пример: добавить Table (ТЧ) на форму

```xml
<Table id="9">
    <name>Товары</name>
    <Title><v8:item><v8:lang>ru</v8:lang><v8:content>Товары</v8:content></v8:item></Title>
    <ContextMenu name="ТоварыКонтекстноеМеню" id="10"/>
    <AutoCommandBar name="ТоварыКоманднаяПанель" id="11">
        <HorizontalAlign>Left</HorizontalAlign>
        <Visible>true</Visible>
        <Autofill>true</Autofill>
    </AutoCommandBar>
    <ExtendedTooltip name="ТоварыРасширеннаяПодсказка" id="12"/>
    <SearchStringAddition name="ТоварыСтрокаПоиска" id="13">
        <Source>SearchStringAuto</Source>
    </SearchStringAddition>
    <ViewStatusAddition name="ТоварыСостояниеПросмотра" id="14">
        <Source>ViewStatusAuto</Source>
    </ViewStatusAddition>
    <SearchControlAddition name="ТоварыУправлениеПоиском" id="15">
        <Source>SearchControlAuto</Source>
    </SearchControlAddition>
    <DataPath xmlns:d2p1="...">Объект.Товары</DataPath>
    <ChangeRowSet>true</ChangeRowSet>
    <ChangeRowOrder>true</ChangeRowOrder>
    <Representation>Lines</Representation>
    <!-- далее ChildItems с колонками: каждая InputField (id=N), ContextMenu (N+1), ExtendedTooltip (N+2) -->
</Table>
```

### Альтернатива: генератор формы (только если форма ПОЛНОСТЬЮ пуста)

Если пользователь создал совсем пустую форму без структуры ChildItems — можно использовать генератор для базовой раскладки:
```bash
python scripts/_generate_form.py --type document --object РасходТовара --form ФормаДокумента
```
Потом дозаполнять через скил.

### Чеклист после правки Form.xml

- [ ] BOM сохранён (UTF-8 BOM `EF BB BF`)
- [ ] CRLF, не LF
- [ ] Все ID уникальны
- [ ] У каждого функционального элемента есть `ContextMenu` + `ExtendedTooltip`
- [ ] `DataPath` ссылается на существующий реквизит/ТЧ
- [ ] `get_errors` → 0
- [ ] `ConfigDumpInfo.xml` синхронизирован (новые элементы формы НЕ требуют записи в CDI — там фиксируется только сама форма; но если меняется UUID элемента — это отдельный случай)

---

## 4. Добавление макета (Template) и команды (Command)

### Макет (Template)

**Файлы:**
- Дескриптор: `Конфигурация/<Тип>/<Объект>/Templates/<ИмяМакета>.xml`
- Содержимое: `Конфигурация/<Тип>/<Объект>/Templates/<ИмяМакета>/Ext/Template.xml`

**Регистрация в объекте:** добавить в `<ChildObjects>` объекта **после** `<TabularSection>`, **до** `<Form>`:
```xml
<Template uuid="GENERATE-UUID-V4">
    <Properties>
        <Name>ИмяМакета</Name>
        <Synonym><v8:item><v8:lang>ru</v8:lang><v8:content>Макет</v8:content></v8:item></Synonym>
        <Comment/>
        <TemplateType>SpreadsheetDocument</TemplateType>
    </Properties>
</Template>
```

`TemplateType`: `SpreadsheetDocument`, `DataCompositionSchema`, `TextDocument`, `BinaryData`, `ActiveDocument`, `HTMLDocument`, `Geographical`.

### Команда (Command)

Добавляется в `<ChildObjects>` объекта **после** форм:
```xml
<Command uuid="GENERATE-UUID-V4">
    <Properties>
        <Name>ИмяКоманды</Name>
        <Synonym><v8:item><v8:lang>ru</v8:lang><v8:content>Название</v8:content></v8:item></Synonym>
        <Group>FormCommandBarImportant</Group>
        <CommandParameterType>
            <v8:Type>cfg:CatalogRef.ИмяОбъекта</v8:Type>
        </CommandParameterType>
        <Representation>Auto</Representation>
        <ModifiesData>false</ModifiesData>
    </Properties>
</Command>
```

И создать модуль команды: `Конфигурация/<Тип>/<Объект>/Commands/<ИмяКоманды>/Ext/CommandModule.bsl`

После добавления → синхронизировать `ConfigDumpInfo.xml`.

---

## 5. Синхронизация ConfigDumpInfo.xml

**Файл:** `Конфигурация/ConfigDumpInfo.xml`

После добавления реквизита/ТЧ/формы/макета/команды найти узел объекта:
```xml
<Metadata name="Catalog.ИмяСправочника" id="UUID-СПРАВОЧНИКА" configVersion="...">
```

Внутри добавить запись о новом элементе с тем же UUID, что в XML объекта:

| Что добавили | Запись в CDI |
|--------------|--------------|
| Реквизит | `<Metadata name="Catalog.Имя.Attribute.Реквизит" id="UUID-РЕКВИЗИТА"/>` |
| ТЧ | `<Metadata name="Catalog.Имя.TabularSection.ИмяТЧ" id="UUID-ТЧ">` + вложенные `Attribute` |
| Реквизит ТЧ | `<Metadata name="Catalog.Имя.TabularSection.ИмяТЧ.Attribute.Реквизит" id="UUID"/>` |
| Форма | `<Metadata name="Catalog.Имя.Form.ИмяФормы" id="UUID-ФОРМЫ"/>` |
| Макет | `<Metadata name="Catalog.Имя.Template.ИмяМакета" id="UUID-МАКЕТА"/>` |
| Команда | `<Metadata name="Catalog.Имя.Command.ИмяКоманды" id="UUID-КОМАНДЫ"/>` |

`configVersion` объекта **не** меняется при добавлении дочерних элементов — он формируется конфигуратором при Dump.

⚠️ Если пользователь сделал свежий Dump после создания скелета — записи могут уже быть. Проверить ПЕРЕД добавлением.

---

## 6. Включение объекта в подсистему

**Файл:** `Конфигурация/Subsystems/<Подсистема>/Ext/Subsystem.xml`

Добавить строку в блок `<Content>`:
```xml
<Content xmlns:xr="http://v8.1c.ru/8.3/xcf/readable">
    <xr:Item>Catalog.Номенклатура</xr:Item>
    <xr:Item>Document.РасходТовара</xr:Item>
    <!-- новая запись: -->
    <xr:Item>Catalog.НовыйСправочник</xr:Item>
</Content>
```

Формат имени: `<ТипВЕдинственномЧисле>.<Имя>`. Маппинг типов → раздел «Маппинг» в `xml-1c.instructions.md`.

⚠️ В `ConfigDumpInfo.xml` **не нужно** добавлять запись о включении в подсистему — там фиксируется только сама подсистема.

---

## 7. Генерация UUID

UUID v4: `xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx` (lowercase hex, `y` ∈ {8,9,a,b}).

Получение:
```python
import uuid
print(str(uuid.uuid4()))
```

Или через Python-скрипт:
```bash
python -c "import uuid; print(uuid.uuid4())"
```

---

## 8. Шаблоны xmlns (краткая сводка)

Для **объекта** (Catalog/Document/Register/Report/DataProcessor) — полный набор xmlns обязателен. Брать из `Документация/Шаблоны/`. Подробности → `xml-1c.instructions.md`, секция «Эталонный заголовок».

`version="2.20"` — всегда. НИКОГДА `"2.0"`.

---

## 9. Финальный чеклист правки XML

- [ ] MCP проверка структуры выполнена ПЕРЕД правкой
- [ ] BOM/CRLF сохранены (для Form.xml/Module.bsl)
- [ ] Сгенерированы корректные UUID v4
- [ ] Объект XML обновлён (реквизит/ТЧ/форма/макет/команда вставлен в правильный порядок ChildObjects)
- [ ] `ConfigDumpInfo.xml` синхронизирован
- [ ] Подсистема обновлена (если применимо)
- [ ] `get_errors` → 0
- [ ] `mcp_dev-mcp_dev_validate` → 0 ошибок
- [ ] Передано `closer` для деплоя через `mcp_dev-mcp_dev_deploy`

---

## 10. Ограничения скила

- ❌ Создание объекта метаданных с нуля — пользователь в Конфигураторе
- ❌ Создание формы с нуля — пользователь в Конфигураторе (если совсем нет файла)
- ❌ Удаление/переименование объектов — пользователь в Конфигураторе
- ❌ Изменение типа объекта — пользователь в Конфигураторе
- ❌ Деплой — задача `closer` через `mcp_dev-mcp_dev_deploy`
- ❌ BSL-код — задача `1c-coder` / `1c-form-builder`
