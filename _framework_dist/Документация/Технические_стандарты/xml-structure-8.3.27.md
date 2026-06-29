# Справочник XML-структуры конфигурации 1С:Предприятие 8.3.27

> **Версия платформы:** 8.3.27  
> **Назначение:** Детальная документация по XML-структуре объектов конфигурации для ИИ-агентов

---

## Содержание

1. [Общая структура XML](#1-общая-структура-xml)
2. [Пространства имён](#2-пространства-имён)
3. [Объекты метаданных](#3-объекты-метаданных)
4. [Формы (Forms)](#4-формы-forms)
5. [Реквизиты и типы данных](#5-реквизиты-и-типы-данных)
6. [Табличные части](#6-табличные-части)
7. [Схемы компоновки данных](#7-схемы-компоновки-данных)
8. [Правила именования](#8-правила-именования)

---

## 1. Общая структура XML

### Заголовок файла
```xml
<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" 
    xmlns:v8="http://v8.1c.ru/8.1/data/core" 
    xmlns:xs="http://www.w3.org/2001/XMLSchema" 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
    version="2.20">
```

### Версия формата
- `version="2.20"` — текущая версия формата для 8.3.27

---

## 2. Пространства имён

### Основные пространства имён

| Префикс | URI | Назначение |
|---------|-----|------------|
| (default) | `http://v8.1c.ru/8.3/MDClasses` | Объекты метаданных |
| `v8` | `http://v8.1c.ru/8.1/data/core` | Базовые типы данных |
| `xs` | `http://www.w3.org/2001/XMLSchema` | XML Schema типы |
| `xsi` | `http://www.w3.org/2001/XMLSchema-instance` | XML Schema instance |
| `xr` | `http://v8.1c.ru/8.3/xcf/readable` | Читаемый формат |
| `cfg` | `http://v8.1c.ru/8.1/data/enterprise/current-config` | Ссылки на объекты конфигурации |
| `xen` | `http://v8.1c.ru/8.3/xcf/enums` | Перечисления платформы |
| `xpr` | `http://v8.1c.ru/8.3/xcf/predef` | Предопределённые данные |

### Пространства имён для форм

| Префикс | URI | Назначение |
|---------|-----|------------|
| (default) | `http://v8.1c.ru/8.3/xcf/logform` | Управляемые формы |
| `lf` | `http://v8.1c.ru/8.2/managed-application/logform` | Логические формы |
| `app` | `http://v8.1c.ru/8.2/managed-application/core` | Ядро приложения |
| `style` | `http://v8.1c.ru/8.1/data/ui/style` | Стили UI |
| `v8ui` | `http://v8.1c.ru/8.1/data/ui` | Интерфейс пользователя |
| `web` | `http://v8.1c.ru/8.1/data/ui/colors/web` | Web-цвета |
| `win` | `http://v8.1c.ru/8.1/data/ui/colors/windows` | Windows-цвета |
| `sys` | `http://v8.1c.ru/8.1/data/ui/fonts/system` | Системные шрифты |

### Пространства имён для СКД

| Префикс | URI | Назначение |
|---------|-----|------------|
| (default) | `http://v8.1c.ru/8.1/data-composition-system/schema` | Схема СКД |
| `dcscor` | `http://v8.1c.ru/8.1/data-composition-system/core` | Ядро СКД |
| `dcscom` | `http://v8.1c.ru/8.1/data-composition-system/common` | Общие элементы СКД |
| `dcsset` | `http://v8.1c.ru/8.1/data-composition-system/settings` | Настройки СКД |

---

## 3. Объекты метаданных

### 3.1 Конфигурация (Configuration)

```xml
<Configuration uuid="7d9eb95e-104f-4595-9eaa-ae812dd59b3c">
    <Properties>
        <Name>Конфигурация</Name>
        <ConfigurationExtensionCompatibilityMode>Version8_3_27</ConfigurationExtensionCompatibilityMode>
        <DefaultRunMode>ManagedApplication</DefaultRunMode>
        <ScriptVariant>Russian</ScriptVariant>
        <UsePurposes>
            <v8:Value xsi:type="app:ApplicationUsePurpose">PlatformApplication</v8:Value>
        </UsePurposes>
    </Properties>
</Configuration>
```

**Ключевые свойства:**
- `ConfigurationExtensionCompatibilityMode` — режим совместимости (Version8_3_27)
- `DefaultRunMode` — режим запуска (ManagedApplication | OrdinaryApplication)
- `ScriptVariant` — вариант языка (Russian | English)

### 3.2 Справочник (Catalog)

```xml
<Catalog uuid="379863f4-aa81-4140-89a8-df74d8755af8">
    <InternalInfo>
        <xr:GeneratedType name="CatalogObject.Номенклатура" category="Object">
            <xr:TypeId>aaa346c5-cddb-4c71-87e7-987541a76e36</xr:TypeId>
            <xr:ValueId>2e42619d-4f58-4fb0-841a-760b736c67da</xr:ValueId>
        </xr:GeneratedType>
        <xr:GeneratedType name="CatalogRef.Номенклатура" category="Ref"/>
        <xr:GeneratedType name="CatalogSelection.Номенклатура" category="Selection"/>
        <xr:GeneratedType name="CatalogList.Номенклатура" category="List"/>
        <xr:GeneratedType name="CatalogManager.Номенклатура" category="Manager"/>
    </InternalInfo>
    <Properties>
        <Name>Номенклатура</Name>
        <Synonym>
            <v8:item>
                <v8:lang>ru</v8:lang>
                <v8:content>Номенклатура</v8:content>
            </v8:item>
        </Synonym>
        <Hierarchical>true</Hierarchical>
        <HierarchyType>HierarchyFoldersAndItems</HierarchyType>
        <CodeLength>9</CodeLength>
        <DescriptionLength>25</DescriptionLength>
        <CodeType>String</CodeType>
        <Autonumbering>true</Autonumbering>
        <DefaultPresentation>AsDescription</DefaultPresentation>
        <InputByString>
            <xr:Field>Catalog.Номенклатура.StandardAttribute.Description</xr:Field>
            <xr:Field>Catalog.Номенклатура.StandardAttribute.Code</xr:Field>
        </InputByString>
    </Properties>
    <ChildObjects>
        <!-- Реквизиты, табличные части, формы -->
    </ChildObjects>
</Catalog>
```

**Типы иерархии:**
- `HierarchyFoldersAndItems` — группы и элементы
- `HierarchyOfItems` — только элементы

**Категории GeneratedType:**
- `Object` — объект справочника
- `Ref` — ссылка
- `Selection` — выборка
- `List` — список
- `Manager` — менеджер

### 3.3 Документ (Document)

```xml
<Document uuid="0ca9be55-ff6c-48bd-83d9-b14c29a066fd">
    <InternalInfo>
        <xr:GeneratedType name="DocumentObject.ЧекККМ" category="Object"/>
        <xr:GeneratedType name="DocumentRef.ЧекККМ" category="Ref"/>
        <xr:GeneratedType name="DocumentSelection.ЧекККМ" category="Selection"/>
        <xr:GeneratedType name="DocumentList.ЧекККМ" category="List"/>
        <xr:GeneratedType name="DocumentManager.ЧекККМ" category="Manager"/>
    </InternalInfo>
    <Properties>
        <Name>ЧекККМ</Name>
        <NumberType>String</NumberType>
        <NumberLength>9</NumberLength>
        <NumberPeriodicity>Nonperiodical</NumberPeriodicity>
        <CheckUnique>true</CheckUnique>
        <Autonumbering>true</Autonumbering>
        <Posting>Allow</Posting>
        <RealTimePosting>Allow</RealTimePosting>
        <RegisterRecordsDeletion>AutoDeleteOnUnpost</RegisterRecordsDeletion>
        <RegisterRecordsWritingOnPost>WriteSelected</RegisterRecordsWritingOnPost>
        <DefaultObjectForm>Document.ЧекККМ.Form.ФормаДокумента</DefaultObjectForm>
        <RegisterRecords>
            <xr:Item xsi:type="xr:MDObjectRef">AccumulationRegister.ОстаткиТоваров</xr:Item>
            <xr:Item xsi:type="xr:MDObjectRef">AccumulationRegister.Продажи</xr:Item>
        </RegisterRecords>
    </Properties>
</Document>
```

**Периодичность номера:**
- `Nonperiodical` — непериодический
- `Year` — в пределах года
- `Quarter` — в пределах квартала
- `Month` — в пределах месяца
- `Day` — в пределах дня

**Режим проведения:**
- `Allow` — разрешено
- `Deny` — запрещено

### 3.4 Регистр накопления (AccumulationRegister)

```xml
<AccumulationRegister uuid="023781c5-18c5-4e54-8614-249ca19ba2f6">
    <InternalInfo>
        <xr:GeneratedType name="AccumulationRegisterRecord.ОстаткиТоваров" category="Record"/>
        <xr:GeneratedType name="AccumulationRegisterManager.ОстаткиТоваров" category="Manager"/>
        <xr:GeneratedType name="AccumulationRegisterSelection.ОстаткиТоваров" category="Selection"/>
        <xr:GeneratedType name="AccumulationRegisterList.ОстаткиТоваров" category="List"/>
        <xr:GeneratedType name="AccumulationRegisterRecordSet.ОстаткиТоваров" category="RecordSet"/>
        <xr:GeneratedType name="AccumulationRegisterRecordKey.ОстаткиТоваров" category="RecordKey"/>
    </InternalInfo>
    <Properties>
        <Name>ОстаткиТоваров</Name>
        <RegisterType>Balance</RegisterType>
        <EnableTotalsSplitting>true</EnableTotalsSplitting>
    </Properties>
    <ChildObjects>
        <Resource uuid="...">
            <Properties>
                <Name>Количество</Name>
                <Type>
                    <v8:Type>xs:decimal</v8:Type>
                    <v8:NumberQualifiers>
                        <v8:Digits>15</v8:Digits>
                        <v8:FractionDigits>4</v8:FractionDigits>
                        <v8:AllowedSign>Any</v8:AllowedSign>
                    </v8:NumberQualifiers>
                </Type>
            </Properties>
        </Resource>
        <Dimension uuid="...">
            <Properties>
                <Name>Склад</Name>
                <Type>
                    <v8:Type>cfg:CatalogRef.Склады</v8:Type>
                </Type>
                <UseInTotals>true</UseInTotals>
            </Properties>
        </Dimension>
    </ChildObjects>
</AccumulationRegister>
```

**Тип регистра:**
- `Balance` — регистр остатков
- `Turnovers` — регистр оборотов

### 3.5 Регистр сведений (InformationRegister)

```xml
<InformationRegister uuid="09063687-bd2b-4df1-90b3-7b1d127e29f2">
    <Properties>
        <Name>ЦеныНоменклатуры</Name>
        <InformationRegisterPeriodicity>Second</InformationRegisterPeriodicity>
        <WriteMode>RecorderSubordinate</WriteMode>
        <MainFilterOnPeriod>false</MainFilterOnPeriod>
        <EnableTotalsSliceFirst>false</EnableTotalsSliceFirst>
        <EnableTotalsSliceLast>false</EnableTotalsSliceLast>
    </Properties>
    <ChildObjects>
        <Resource>...</Resource>
        <Dimension>
            <Properties>
                <Master>false</Master>
                <MainFilter>true</MainFilter>
            </Properties>
        </Dimension>
    </ChildObjects>
</InformationRegister>
```

**Периодичность:**
- `Nonperiodical` — непериодический
- `Year` | `Quarter` | `Month` | `Day` | `Second` — периодический

**Режим записи:**
- `Independent` — независимый
- `RecorderSubordinate` — подчинён регистратору

### 3.6 Перечисление (Enum)

```xml
<Enum uuid="88886a4e-be50-4ade-9113-363f3f5513db">
    <Properties>
        <Name>ВидыОплаты</Name>
        <QuickChoice>true</QuickChoice>
        <ChoiceMode>BothWays</ChoiceMode>
    </Properties>
    <ChildObjects>
        <EnumValue uuid="a0f4ad7e-578c-4bfe-b778-22bce6010e39">
            <Properties>
                <Name>Наличные</Name>
                <Synonym>
                    <v8:item>
                        <v8:lang>ru</v8:lang>
                        <v8:content>Наличные</v8:content>
                    </v8:item>
                </Synonym>
            </Properties>
        </EnumValue>
        <EnumValue uuid="39cc7a0c-3300-4ea6-8c4b-2406d2f0a7eb">
            <Properties>
                <Name>Безналичные</Name>
            </Properties>
        </EnumValue>
    </ChildObjects>
</Enum>
```

### 3.7 Константа (Constant)

```xml
<Constant uuid="5fc3f014-9300-4d93-8a58-487bbb7aa7f0">
    <Properties>
        <Name>ОсновнойСклад</Name>
        <Type>
            <v8:Type>cfg:CatalogRef.Склады</v8:Type>
        </Type>
        <UseStandardCommands>true</UseStandardCommands>
    </Properties>
</Constant>
```

### 3.8 Общий модуль (CommonModule)

```xml
<CommonModule uuid="03750bfa-7126-4cf0-bb90-13f5eabfa4f6">
    <Properties>
        <Name>ОбщегоНазначения</Name>
        <Global>false</Global>
        <ClientManagedApplication>false</ClientManagedApplication>
        <Server>true</Server>
        <ExternalConnection>false</ExternalConnection>
        <ClientOrdinaryApplication>false</ClientOrdinaryApplication>
        <ServerCall>true</ServerCall>
        <Privileged>false</Privileged>
        <ReturnValuesReuse>DontUse</ReturnValuesReuse>
    </Properties>
</CommonModule>
```

**Флаги контекста выполнения:**
- `Server` — на сервере
- `ClientManagedApplication` — на клиенте управляемого приложения
- `ServerCall` — вызов с сервера
- `Privileged` — привилегированный режим
- `Global` — глобальный модуль

**Повторное использование:**
- `DontUse` — не использовать
- `DuringCall` — во время вызова
- `DuringSession` — во время сеанса

### 3.9 Обработка (DataProcessor)

```xml
<DataProcessor uuid="1876b53a-c567-4e3a-9e12-123456789abc">
    <Properties>
        <Name>РабочееМестоКассира</Name>
        <DefaultForm>DataProcessor.РабочееМестоКассира.Form.Форма</DefaultForm>
        <UseStandardCommands>true</UseStandardCommands>
    </Properties>
    <ChildObjects>
        <Attribute>...</Attribute>
        <TabularSection>...</TabularSection>
        <Form>...</Form>
    </ChildObjects>
</DataProcessor>
```

### 3.10 Подсистема (Subsystem)

```xml
<Subsystem uuid="ce36a904-07a9-4005-9340-3b72dfc2e405">
    <Properties>
        <Name>Торговля</Name>
        <IncludeHelpInContents>true</IncludeHelpInContents>
        <IncludeInCommandInterface>true</IncludeInCommandInterface>
        <Content>
            <xr:Item xsi:type="xr:MDObjectRef">DataProcessor.РабочееМестоКассира</xr:Item>
            <xr:Item xsi:type="xr:MDObjectRef">Document.ЧекККМ</xr:Item>
            <xr:Item xsi:type="xr:MDObjectRef">Catalog.Номенклатура</xr:Item>
        </Content>
    </Properties>
</Subsystem>
```

### 3.11 Роль (Role)

```xml
<Role uuid="709a7ae8-259d-4bd5-9df2-d99294330b75">
    <Properties>
        <Name>Администратор</Name>
        <Synonym>
            <v8:item>
                <v8:lang>ru</v8:lang>
                <v8:content>Администратор</v8:content>
            </v8:item>
        </Synonym>
    </Properties>
</Role>
```

---

## 4. Формы (Forms)

### 4.1 Структура файла формы

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Form xmlns="http://v8.1c.ru/8.3/xcf/logform" version="2.20">
    <!-- Свойства формы -->
    <AutoTitle>false</AutoTitle>
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>Заголовок формы</v8:content>
        </v8:item>
    </Title>
    
    <!-- Специфичные свойства для документов -->
    <AutoTime>CurrentOrLast</AutoTime>
    <UsePostingMode>Auto</UsePostingMode>
    <RepostOnWrite>true</RepostOnWrite>
    
    <!-- Командная панель формы -->
    <AutoCommandBar name="ФормаКоманднаяПанель" id="-1">
        <Autofill>false</Autofill>
        <ChildItems>...</ChildItems>
    </AutoCommandBar>
    
    <!-- События формы -->
    <Events>
        <Event name="OnOpen">ПриОткрытии</Event>
        <Event name="OnCreateAtServer">ПриСозданииНаСервере</Event>
        <Event name="BeforeClose">ПередЗакрытием</Event>
        <Event name="BeforeWriteAtServer">ПередЗаписьюНаСервере</Event>
    </Events>
    
    <!-- Элементы формы -->
    <ChildItems>...</ChildItems>
    
    <!-- Реквизиты формы -->
    <Attributes>...</Attributes>
    
    <!-- Команды формы -->
    <Commands>...</Commands>
</Form>
```

### 4.2 Элементы формы

#### 4.2.1 Поле ввода (InputField)

```xml
<InputField name="Наименование" id="1">
    <DataPath>Объект.Наименование</DataPath>
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>Наименование товара</v8:content>
        </v8:item>
    </Title>
    <Width>30</Width>
    <AutoMaxWidth>false</AutoMaxWidth>
    <HorizontalStretch>false</HorizontalStretch>
    <EditMode>EnterOnInput</EditMode>
    <ReadOnly>false</ReadOnly>
    <ExtendedEditMultipleValues>true</ExtendedEditMultipleValues>
    <ContextMenu name="НаименованиеКонтекстноеМеню" id="2"/>
    <ExtendedTooltip name="НаименованиеРасширеннаяПодсказка" id="3"/>
    <Events>
        <Event name="OnChange">НаименованиеПриИзменении</Event>
        <Event name="StartChoice">НаименованиеНачалоВыбора</Event>
    </Events>
</InputField>
```

**Свойства InputField:**
- `DataPath` — путь к данным (Объект.Реквизит)
- `Width` — ширина в символах
- `AutoMaxWidth` — автоширина
- `HorizontalStretch` — растягивание
- `EditMode` — режим редактирования
- `ReadOnly` — только чтение

**Режимы редактирования (EditMode):**
- `Enter` — при входе
- `EnterOnInput` — при вводе

**События InputField:**
- `OnChange` — при изменении
- `StartChoice` — начало выбора
- `Clearing` — очистка
- `Opening` — открытие
- `AutoComplete` — автозаполнение
- `TextEditEnd` — окончание ввода текста

#### 4.2.2 Поле надписи (LabelField)

```xml
<LabelField name="ИтогСумма" id="2">
    <DataPath>Объект.ТЧ.TotalСумма</DataPath>
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>К ОПЛАТЕ:</v8:content>
        </v8:item>
    </Title>
    <TitleLocation>None</TitleLocation>
    <Font ref="style:LargeTextFont" height="14" bold="true" kind="StyleItem"/>
    <ContextMenu name="ИтогСуммаКонтекстноеМеню" id="3"/>
    <ExtendedTooltip name="ИтогСуммаРасширеннаяПодсказка" id="4"/>
</LabelField>
```

#### 4.2.3 Декорация-надпись (LabelDecoration)

```xml
<LabelDecoration name="ДекорацияЗаголовок" id="2">
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>Выберите способ возврата товара:</v8:content>
        </v8:item>
    </Title>
    <Font ref="style:LargeTextFont" height="12" bold="true" kind="StyleItem"/>
</LabelDecoration>
```

#### 4.2.4 Флажок (CheckBoxField)

```xml
<CheckBoxField name="ФискальныйВозврат" id="3">
    <DataPath>ФискальныйВозврат</DataPath>
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>Фискальный возврат</v8:content>
        </v8:item>
    </Title>
    <TitleLocation>Right</TitleLocation>
    <CheckBoxType>Switcher</CheckBoxType>
    <Events>
        <Event name="OnChange">ФискальныйВозвратПриИзменении</Event>
    </Events>
</CheckBoxField>
```

**Типы флажка:**
- `Standard` — стандартный
- `Switcher` — переключатель

#### 4.2.5 Кнопка (Button)

```xml
<Button name="КнопкаОплатить" id="14">
    <Type>UsualButton</Type>
    <DefaultButton>true</DefaultButton>
    <Width>15</Width>
    <Height>3</Height>
    <CommandName>Form.Command.Оплатить</CommandName>
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>ОПЛАТИТЬ</v8:content>
        </v8:item>
    </Title>
    <Representation>PictureAndText</Representation>
    <Picture>
        <xr:Ref>StdPicture.Write</xr:Ref>
        <xr:LoadTransparent>true</xr:LoadTransparent>
    </Picture>
    <ExtendedTooltip name="КнопкаОплатитьРасширеннаяПодсказка" id="15"/>
</Button>
```

**Типы кнопки:**
- `UsualButton` — обычная кнопка
- `CommandBarButton` — кнопка командной панели
- `Hyperlink` — гиперссылка

**Представление:**
- `Text` — текст
- `Picture` — картинка
- `PictureAndText` — картинка и текст
- `Auto` — авто

#### 4.2.6 Таблица формы (Table)

```xml
<Table name="Товары" id="29">
    <Representation>List</Representation>
    <DataPath>Объект.Товары</DataPath>
    <RowFilter xsi:nil="true"/>
    <AutoInsertNewRow>true</AutoInsertNewRow>
    <EnableStartDrag>true</EnableStartDrag>
    <EnableDrag>true</EnableDrag>
    <ReadOnly>false</ReadOnly>
    <Height>15</Height>
    <HorizontalStretch>true</HorizontalStretch>
    <VerticalStretch>true</VerticalStretch>
    <AutoAddIncomplete>false</AutoAddIncomplete>
    <SearchStringLocation>None</SearchStringLocation>
    <ViewStatusLocation>None</ViewStatusLocation>
    <SearchControlLocation>None</SearchControlLocation>
    
    <ContextMenu name="ТоварыКонтекстноеМеню" id="30"/>
    <AutoCommandBar name="ТоварыКоманднаяПанель" id="31">
        <Autofill>false</Autofill>
    </AutoCommandBar>
    <ExtendedTooltip name="ТоварыРасширеннаяПодсказка" id="32"/>
    
    <!-- Дополнения таблицы -->
    <SearchStringAddition name="ТоварыСтрокаПоиска" id="33">
        <AdditionSource>
            <Item>Товары</Item>
            <Type>SearchStringRepresentation</Type>
        </AdditionSource>
    </SearchStringAddition>
    <ViewStatusAddition name="ТоварыСостояниеПросмотра" id="36">
        <AdditionSource>
            <Item>Товары</Item>
            <Type>ViewStatusRepresentation</Type>
        </AdditionSource>
    </ViewStatusAddition>
    <SearchControlAddition name="ТоварыУправлениеПоиском" id="39">
        <AdditionSource>
            <Item>Товары</Item>
            <Type>SearchControl</Type>
        </AdditionSource>
    </SearchControlAddition>
    
    <Events>
        <Event name="Selection">ТоварыВыбор</Event>
        <Event name="OnActivateRow">ТоварыПриАктивизацииСтроки</Event>
        <Event name="OnChange">ТоварыПриИзменении</Event>
        <Event name="AfterDeleteRow">ТоварыПослеУдаленияСтроки</Event>
    </Events>
    
    <ChildItems>
        <!-- Колонки таблицы -->
        <LabelField name="ТоварыНомерСтроки" id="42">
            <DataPath>Объект.Товары.LineNumber</DataPath>
        </LabelField>
        <InputField name="ТоварыНоменклатура" id="45">
            <DataPath>Объект.Товары.Номенклатура</DataPath>
            <Events>
                <Event name="OnChange">ТоварыНоменклатураПриИзменении</Event>
            </Events>
        </InputField>
    </ChildItems>
</Table>
```

**События Table:**
- `Selection` — выбор строки
- `OnActivateRow` — при активизации строки
- `OnActivateField` — при активизации поля
- `OnChange` — при изменении
- `BeforeAddRow` — перед добавлением строки
- `AfterDeleteRow` — после удаления строки
- `BeforeDeleteRow` — перед удалением строки
- `OnStartEdit` — при начале редактирования
- `OnEndEdit` — при окончании редактирования

#### 4.2.7 Группа элементов (UsualGroup)

```xml
<UsualGroup name="ГруппаШапка" id="1">
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>Шапка</v8:content>
        </v8:item>
    </Title>
    <Group>Horizontal</Group>
    <Representation>None</Representation>
    <ShowTitle>false</ShowTitle>
    <Width>40</Width>
    <ExtendedTooltip name="ГруппаШапкаРасширеннаяПодсказка" id="23"/>
    <ChildItems>
        <!-- Дочерние элементы -->
    </ChildItems>
</UsualGroup>
```

**Типы группировки (Group):**
- `Horizontal` — горизонтальная
- `Vertical` — вертикальная
- `HorizontalIfPossible` — горизонтальная если возможно
- `AlwaysHorizontal` — всегда горизонтальная

**Представление (Representation):**
- `None` — без оформления
- `WeakSeparation` — слабое разделение
- `NormalSeparation` — обычное разделение
- `StrongSeparation` — сильное разделение

#### 4.2.8 Страницы (Pages / Page)

```xml
<Pages name="Страницы" id="25">
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>Страницы</v8:content>
        </v8:item>
    </Title>
    <ExtendedTooltip name="СтраницыРасширеннаяПодсказка" id="26"/>
    <ChildItems>
        <Page name="ГруппаТовары" id="27">
            <Title>
                <v8:item>
                    <v8:lang>ru</v8:lang>
                    <v8:content>Товары</v8:content>
                </v8:item>
            </Title>
            <ExtendedTooltip name="ГруппаТоварыРасширеннаяПодсказка" id="28"/>
            <ChildItems>
                <!-- Содержимое страницы -->
            </ChildItems>
        </Page>
        <Page name="ГруппаОплата" id="66">
            <Title>
                <v8:item>
                    <v8:lang>ru</v8:lang>
                    <v8:content>Оплата</v8:content>
                </v8:item>
            </Title>
        </Page>
    </ChildItems>
</Pages>
```

### 4.3 Реквизиты формы (Attributes)

```xml
<Attributes>
    <!-- Основной реквизит (объект) -->
    <Attribute name="Объект" id="1">
        <Type>
            <v8:Type>cfg:DocumentObject.ЧекККМ</v8:Type>
        </Type>
        <MainAttribute>true</MainAttribute>
        <SavedData>true</SavedData>
        <UseAlways>
            <Field>Объект.RegisterRecords</Field>
        </UseAlways>
    </Attribute>
    
    <!-- Реквизит типа ссылка -->
    <Attribute name="ОсновнойСклад" id="2">
        <Type>
            <v8:Type>cfg:CatalogRef.Склады</v8:Type>
        </Type>
    </Attribute>
    
    <!-- Реквизит примитивного типа -->
    <Attribute name="НомерСтраницы" id="3">
        <Title>
            <v8:item>
                <v8:lang>ru</v8:lang>
                <v8:content>Страница</v8:content>
            </v8:item>
        </Title>
        <Type>
            <v8:Type>xs:decimal</v8:Type>
            <v8:NumberQualifiers>
                <v8:Digits>5</v8:Digits>
                <v8:FractionDigits>0</v8:FractionDigits>
                <v8:AllowedSign>Any</v8:AllowedSign>
            </v8:NumberQualifiers>
        </Type>
    </Attribute>
    
    <!-- Таблица значений -->
    <Attribute name="СписокЧеков" id="1">
        <Title>
            <v8:item>
                <v8:lang>ru</v8:lang>
                <v8:content>Список чеков</v8:content>
            </v8:item>
        </Title>
        <Type>
            <v8:Type>ValueTable</v8:Type>
        </Type>
        <Columns>
            <Column name="Чек" id="1">
                <Type>
                    <v8:Type>DocumentRef.ЧекККМ</v8:Type>
                </Type>
            </Column>
            <Column name="Сумма" id="4">
                <Type>
                    <v8:Type>xs:decimal</v8:Type>
                    <v8:NumberQualifiers>
                        <v8:Digits>15</v8:Digits>
                        <v8:FractionDigits>2</v8:FractionDigits>
                        <v8:AllowedSign>Nonnegative</v8:AllowedSign>
                    </v8:NumberQualifiers>
                </Type>
            </Column>
        </Columns>
    </Attribute>
</Attributes>
```

### 4.4 Команды формы (Commands)

```xml
<Commands>
    <Command name="Оплатить" id="1">
        <Title>
            <v8:item>
                <v8:lang>ru</v8:lang>
                <v8:content>Оплатить</v8:content>
            </v8:item>
        </Title>
        <ToolTip>
            <v8:item>
                <v8:lang>ru</v8:lang>
                <v8:content>Оплатить покупку</v8:content>
            </v8:item>
        </ToolTip>
        <Action>Оплатить</Action>
    </Command>
</Commands>
```

### 4.5 События формы

**Полный список событий формы:**

| Событие | Описание | Контекст |
|---------|----------|----------|
| `OnCreateAtServer` | При создании на сервере | Сервер |
| `OnOpen` | При открытии | Клиент |
| `BeforeClose` | Перед закрытием | Клиент |
| `OnClose` | При закрытии | Клиент |
| `BeforeWrite` | Перед записью | Клиент |
| `BeforeWriteAtServer` | Перед записью на сервере | Сервер |
| `AfterWrite` | После записи | Клиент |
| `AfterWriteAtServer` | После записи на сервере | Сервер |
| `OnReadAtServer` | При чтении на сервере | Сервер |
| `NotificationProcessing` | Обработка оповещения | Клиент |
| `ExternalEvent` | Внешнее событие | Клиент |

---

## 5. Реквизиты и типы данных

### 5.1 Структура реквизита

```xml
<Attribute uuid="c1b8660a-a7e5-4bb2-a662-638a5237b0e1">
    <Properties>
        <Name>Артикул</Name>
        <Synonym>
            <v8:item>
                <v8:lang>ru</v8:lang>
                <v8:content>Артикул</v8:content>
            </v8:item>
        </Synonym>
        <Comment/>
        <Type>...</Type>
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
        <FillValue xsi:type="xs:string"/>
        <FillChecking>DontCheck</FillChecking>
        <ChoiceFoldersAndItems>Items</ChoiceFoldersAndItems>
        <ChoiceParameterLinks/>
        <ChoiceParameters/>
        <QuickChoice>Auto</QuickChoice>
        <CreateOnInput>Auto</CreateOnInput>
        <ChoiceForm/>
        <LinkByType/>
        <ChoiceHistoryOnInput>Auto</ChoiceHistoryOnInput>
        <Use>ForItem</Use>
        <Indexing>DontIndex</Indexing>
        <FullTextSearch>Use</FullTextSearch>
        <DataHistory>Use</DataHistory>
    </Properties>
</Attribute>
```

### 5.2 Типы данных

#### Строка
```xml
<Type>
    <v8:Type>xs:string</v8:Type>
    <v8:StringQualifiers>
        <v8:Length>100</v8:Length>
        <v8:AllowedLength>Variable</v8:AllowedLength>
    </v8:StringQualifiers>
</Type>
```

#### Число
```xml
<Type>
    <v8:Type>xs:decimal</v8:Type>
    <v8:NumberQualifiers>
        <v8:Digits>15</v8:Digits>
        <v8:FractionDigits>2</v8:FractionDigits>
        <v8:AllowedSign>Any</v8:AllowedSign>
    </v8:NumberQualifiers>
</Type>
```

**AllowedSign:**
- `Any` — любой знак
- `Nonnegative` — неотрицательный

#### Дата
```xml
<Type>
    <v8:Type>xs:dateTime</v8:Type>
    <v8:DateQualifiers>
        <v8:DateFractions>DateTime</v8:DateFractions>
    </v8:DateQualifiers>
</Type>
```

**DateFractions:**
- `Date` — только дата
- `Time` — только время
- `DateTime` — дата и время

#### Булево
```xml
<Type>
    <v8:Type>xs:boolean</v8:Type>
</Type>
```

#### Ссылка на справочник
```xml
<Type>
    <v8:Type>cfg:CatalogRef.Номенклатура</v8:Type>
</Type>
```

#### Ссылка на документ
```xml
<Type>
    <v8:Type>cfg:DocumentRef.ЧекККМ</v8:Type>
</Type>
```

#### Ссылка на перечисление
```xml
<Type>
    <v8:Type>cfg:EnumRef.ВидыОплаты</v8:Type>
</Type>
```

#### Составной тип
```xml
<Type>
    <v8:Type>cfg:CatalogRef.Номенклатура</v8:Type>
    <v8:Type>cfg:CatalogRef.Услуги</v8:Type>
</Type>
```

### 5.3 Проверка заполнения (FillChecking)

- `DontCheck` — не проверять
- `ShowError` — показать ошибку
- `ShowWarning` — показать предупреждение

### 5.4 Индексирование (Indexing)

- `DontIndex` — не индексировать
- `Index` — индексировать
- `IndexWithAdditionalOrder` — индексировать с доп. упорядочиванием

---

## 6. Табличные части

### 6.1 Структура табличной части

```xml
<TabularSection uuid="940d5070-1c93-4b4c-9c3f-6c2df54f8845">
    <InternalInfo>
        <xr:GeneratedType name="DocumentTabularSection.ЧекККМ.Товары" category="TabularSection">
            <xr:TypeId>...</xr:TypeId>
            <xr:ValueId>...</xr:ValueId>
        </xr:GeneratedType>
        <xr:GeneratedType name="DocumentTabularSectionRow.ЧекККМ.Товары" category="TabularSectionRow">
            <xr:TypeId>...</xr:TypeId>
            <xr:ValueId>...</xr:ValueId>
        </xr:GeneratedType>
    </InternalInfo>
    <Properties>
        <Name>Товары</Name>
        <Synonym>
            <v8:item>
                <v8:lang>ru</v8:lang>
                <v8:content>Товары</v8:content>
            </v8:item>
        </Synonym>
        <ToolTip/>
        <FillChecking>DontCheck</FillChecking>
        <StandardAttributes>
            <StandardAttribute name="LineNumber">
                <Synonym>
                    <v8:item>
                        <v8:lang>ru</v8:lang>
                        <v8:content>Номер строки</v8:content>
                    </v8:item>
                </Synonym>
            </StandardAttribute>
        </StandardAttributes>
    </Properties>
    <ChildObjects>
        <Attribute uuid="...">
            <Properties>
                <Name>Номенклатура</Name>
                <Type>
                    <v8:Type>cfg:CatalogRef.Номенклатура</v8:Type>
                </Type>
            </Properties>
        </Attribute>
        <Attribute uuid="...">
            <Properties>
                <Name>Количество</Name>
                <Type>
                    <v8:Type>xs:decimal</v8:Type>
                    <v8:NumberQualifiers>
                        <v8:Digits>15</v8:Digits>
                        <v8:FractionDigits>3</v8:FractionDigits>
                        <v8:AllowedSign>Any</v8:AllowedSign>
                    </v8:NumberQualifiers>
                </Type>
            </Properties>
        </Attribute>
    </ChildObjects>
</TabularSection>
```

---

## 7. Схемы компоновки данных

### 7.1 Структура СКД

```xml
<DataCompositionSchema xmlns="http://v8.1c.ru/8.1/data-composition-system/schema">
    <!-- Источник данных -->
    <dataSource>
        <name>ИсточникДанных1</name>
        <dataSourceType>Local</dataSourceType>
    </dataSource>
    
    <!-- Набор данных -->
    <dataSet xsi:type="DataSetQuery">
        <name>НаборДанных1</name>
        <field xsi:type="DataSetFieldField">
            <dataPath>Номенклатура</dataPath>
            <field>Номенклатура</field>
            <role>
                <dcscom:dimension>true</dcscom:dimension>
            </role>
        </field>
        <field xsi:type="DataSetFieldField">
            <dataPath>КоличествоКонечныйОстаток</dataPath>
            <field>КоличествоКонечныйОстаток</field>
            <role>
                <dcscom:balance>true</dcscom:balance>
                <dcscom:balanceGroupName>Количество</dcscom:balanceGroupName>
                <dcscom:balanceType>ClosingBalance</dcscom:balanceType>
            </role>
        </field>
        <dataSource>ИсточникДанных1</dataSource>
        <query>ВЫБРАТЬ ... ИЗ ...</query>
    </dataSet>
    
    <!-- Параметры -->
    <parameter>
        <name>НачалоПериода</name>
        <title xsi:type="v8:LocalStringType">
            <v8:item>
                <v8:lang>ru</v8:lang>
                <v8:content>Начало периода</v8:content>
            </v8:item>
        </title>
        <valueType>
            <v8:Type>xs:dateTime</v8:Type>
        </valueType>
    </parameter>
    
    <!-- Вариант настроек -->
    <settingsVariant>
        <dcsset:name>Основной</dcsset:name>
        <dcsset:settings>
            <dcsset:selection>
                <dcsset:item xsi:type="dcsset:SelectedItemField">
                    <dcsset:field>Номенклатура</dcsset:field>
                </dcsset:item>
            </dcsset:selection>
        </dcsset:settings>
    </settingsVariant>
</DataCompositionSchema>
```

### 7.2 Роли полей СКД

```xml
<!-- Измерение -->
<role>
    <dcscom:dimension>true</dcscom:dimension>
</role>

<!-- Ресурс -->
<role>
    <dcscom:account>true</dcscom:account>
</role>

<!-- Остаток -->
<role>
    <dcscom:balance>true</dcscom:balance>
    <dcscom:balanceGroupName>Количество</dcscom:balanceGroupName>
    <dcscom:balanceType>OpeningBalance</dcscom:balanceType>
</role>
```

**Типы остатков:**
- `OpeningBalance` — начальный остаток
- `ClosingBalance` — конечный остаток

---

## 8. Правила именования

### 8.1 Общие правила

1. **Имена на русском** в CamelCase: `НоменклатураПриИзменении`
2. **UUID** — уникальный идентификатор для каждого объекта
3. **id** — уникальный числовой идентификатор внутри формы

### 8.2 Правила именования элементов форм

| Объект | Префикс имени элемента | Пример |
|--------|------------------------|--------|
| Поле ввода | — | `Наименование` |
| Колонка таблицы | ИмяТаблицы + ИмяКолонки | `ТоварыНоменклатура` |
| Контекстное меню | Имя + "КонтекстноеМеню" | `НаименованиеКонтекстноеМеню` |
| Расширенная подсказка | Имя + "РасширеннаяПодсказка" | `НаименованиеРасширеннаяПодсказка` |
| Командная панель | Имя + "КоманднаяПанель" | `ТоварыКоманднаяПанель` |
| Строка поиска | Имя + "СтрокаПоиска" | `ТоварыСтрокаПоиска` |

### 8.3 Ссылки на объекты

```xml
<!-- Ссылка на форму -->
<DefaultObjectForm>Document.ЧекККМ.Form.ФормаДокумента</DefaultObjectForm>

<!-- Ссылка на команду -->
<CommandName>Form.Command.Оплатить</CommandName>
<CommandName>Form.StandardCommand.Close</CommandName>

<!-- Ссылка на стандартную картинку -->
<Picture>
    <xr:Ref>StdPicture.Write</xr:Ref>
</Picture>

<!-- Ссылка на стиль шрифта -->
<Font ref="style:LargeTextFont" height="14" bold="true" kind="StyleItem"/>

<!-- Ссылка на объект метаданных -->
<xr:Item xsi:type="xr:MDObjectRef">AccumulationRegister.ОстаткиТоваров</xr:Item>
```

---

## Приложение A: Шаблоны XML

### A.1 Минимальный справочник

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" 
    xmlns:v8="http://v8.1c.ru/8.1/data/core" 
    xmlns:xs="http://www.w3.org/2001/XMLSchema" 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xr="http://v8.1c.ru/8.3/xcf/readable"
    version="2.20">
    <Catalog uuid="НОВЫЙ-UUID">
        <Properties>
            <Name>НовыйСправочник</Name>
            <Synonym>
                <v8:item>
                    <v8:lang>ru</v8:lang>
                    <v8:content>Новый справочник</v8:content>
                </v8:item>
            </Synonym>
            <CodeLength>9</CodeLength>
            <DescriptionLength>50</DescriptionLength>
            <CodeType>String</CodeType>
            <Autonumbering>true</Autonumbering>
        </Properties>
        <ChildObjects/>
    </Catalog>
</MetaDataObject>
```

### A.2 Минимальный документ

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" 
    xmlns:v8="http://v8.1c.ru/8.1/data/core" 
    xmlns:xs="http://www.w3.org/2001/XMLSchema" 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xr="http://v8.1c.ru/8.3/xcf/readable"
    version="2.20">
    <Document uuid="НОВЫЙ-UUID">
        <Properties>
            <Name>НовыйДокумент</Name>
            <Synonym>
                <v8:item>
                    <v8:lang>ru</v8:lang>
                    <v8:content>Новый документ</v8:content>
                </v8:item>
            </Synonym>
            <NumberType>String</NumberType>
            <NumberLength>9</NumberLength>
            <Autonumbering>true</Autonumbering>
            <Posting>Allow</Posting>
        </Properties>
        <ChildObjects/>
    </Document>
</MetaDataObject>
```

### A.3 Минимальная форма

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Form xmlns="http://v8.1c.ru/8.3/xcf/logform"
    xmlns:v8="http://v8.1c.ru/8.1/data/core"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    version="2.20">
    <AutoCommandBar name="ФормаКоманднаяПанель" id="-1"/>
    <ChildItems>
        <InputField name="Наименование" id="1">
            <DataPath>Объект.Наименование</DataPath>
        </InputField>
    </ChildItems>
    <Attributes>
        <Attribute name="Объект" id="1">
            <Type>
                <v8:Type>cfg:CatalogObject.НовыйСправочник</v8:Type>
            </Type>
            <MainAttribute>true</MainAttribute>
        </Attribute>
    </Attributes>
</Form>
```

---

> **Документ создан:** 2026-01-24  
> **Версия:** 1.0  
> **Платформа:** 1С:Предприятие 8.3.27
