# Справочник элементов управляемых форм 1C 8.3.27

> **Версия платформы:** 8.3.27  
> **Связанная документация:** [XML-структура конфигурации](xml-structure-8.3.27.md)

---

## Содержание

1. [Структура файла формы](#1-структура-файла-формы)
2. [Элементы форм](#2-элементы-форм)
3. [Расширенные элементы форм](#3-расширенные-элементы-форм)
4. [Реквизиты формы](#4-реквизиты-формы)
5. [Команды формы](#5-команды-формы)
6. [События](#6-события)
7. [Программное управление](#7-программное-управление)
8. [Типовые обработчики РМК](#8-типовые-обработчики-рмк)
9. [Асинхронная модель](#9-асинхронная-модель)
10. [Новое в 8.3.27](#10-новое-в-8327)

---

## 1. Структура файла формы

### 1.1 Заголовок и пространства имён

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Form xmlns="http://v8.1c.ru/8.3/xcf/logform" 
    xmlns:v8="http://v8.1c.ru/8.1/data/core" 
    xmlns:xs="http://www.w3.org/2001/XMLSchema" 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xr="http://v8.1c.ru/8.3/xcf/readable"
    xmlns:style="http://v8.1c.ru/8.1/data/ui/style"
    version="2.20">
```

### 1.2 Корневые свойства формы

```xml
<Form ...>
    <!-- Заголовок -->
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>Заголовок формы</v8:content>
        </v8:item>
    </Title>
    <AutoTitle>false</AutoTitle>
    
    <!-- Командная панель -->
    <CommandBarLocation>None</CommandBarLocation>
    <AutoCommandBar name="ФормаКоманднаяПанель" id="-1">
        <Autofill>false</Autofill>
    </AutoCommandBar>
    
    <!-- Свойства для документов -->
    <AutoTime>CurrentOrLast</AutoTime>
    <UsePostingMode>Auto</UsePostingMode>
    <RepostOnWrite>true</RepostOnWrite>
    
    <!-- События формы -->
    <Events>
        <Event name="OnCreateAtServer">ПриСозданииНаСервере</Event>
        <Event name="OnOpen">ПриОткрытии</Event>
        <Event name="BeforeClose">ПередЗакрытием</Event>
    </Events>
    
    <!-- Дочерние элементы -->
    <ChildItems>...</ChildItems>
    
    <!-- Реквизиты -->
    <Attributes>...</Attributes>
    
    <!-- Команды -->
    <Commands>...</Commands>
</Form>
```

### 1.3 Расположение командной панели (CommandBarLocation)

| Значение | Описание |
|----------|----------|
| `None` | Без командной панели |
| `Top` | Сверху |
| `Bottom` | Снизу |
| `Auto` | Автоматически |

---

## 2. Элементы форм

### 2.1 Поле ввода (InputField)

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
    <TitleLocation>Left</TitleLocation>
    <ContextMenu name="НаименованиеКонтекстноеМеню" id="2"/>
    <ExtendedTooltip name="НаименованиеРасширеннаяПодсказка" id="3"/>
    <Events>
        <Event name="OnChange">НаименованиеПриИзменении</Event>
        <Event name="StartChoice">НаименованиеНачалоВыбора</Event>
        <Event name="Clearing">НаименованиеОчистка</Event>
    </Events>
</InputField>
```

**Свойства InputField:**

| Свойство | Тип | Описание |
|----------|-----|----------|
| `DataPath` | String | Путь к данным (Объект.Реквизит) |
| `Width` | Number | Ширина в символах |
| `Height` | Number | Высота в строках |
| `AutoMaxWidth` | Boolean | Авто максимальная ширина |
| `HorizontalStretch` | Boolean | Горизонтальное растягивание |
| `VerticalStretch` | Boolean | Вертикальное растягивание |
| `EditMode` | Enum | Режим редактирования |
| `ReadOnly` | Boolean | Только чтение |
| `MultiLine` | Boolean | Многострочное поле |
| `PasswordMode` | Boolean | Режим пароля |
| `TitleLocation` | Enum | Расположение заголовка |

**Режимы редактирования (EditMode):**
- `Enter` — при входе в поле
- `EnterOnInput` — при вводе данных

**Расположение заголовка (TitleLocation):**
- `Left` — слева
- `Top` — сверху
- `Right` — справа
- `Bottom` — снизу
- `None` — без заголовка
- `Auto` — автоматически

**События InputField:**

| Событие | Описание |
|---------|----------|
| `OnChange` | При изменении значения |
| `StartChoice` | Начало выбора (кнопка выбора) |
| `Clearing` | Очистка значения |
| `Opening` | Открытие формы связанного объекта |
| `AutoComplete` | Автоподбор значения |
| `TextEditEnd` | Окончание редактирования текста |
| `ChoiceProcessing` | Обработка выбора |

### 2.2 Поле надписи (LabelField)

```xml
<LabelField name="ИтогоСумма" id="10">
    <DataPath>Объект.СуммаДокумента</DataPath>
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>ИТОГО:</v8:content>
        </v8:item>
    </Title>
    <TitleLocation>Left</TitleLocation>
    <Font ref="style:LargeTextFont" height="14" bold="true" kind="StyleItem"/>
    <TextColor>
        <v8:Color>Style.SpecialTextColor</v8:Color>
    </TextColor>
    <ContextMenu name="ИтогоСуммаКонтекстноеМеню" id="11"/>
    <ExtendedTooltip name="ИтогоСуммаРасширеннаяПодсказка" id="12"/>
</LabelField>
```

### 2.3 Декорация-надпись (LabelDecoration)

```xml
<LabelDecoration name="ДекорацияЗаголовок" id="20">
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>Информационное сообщение</v8:content>
        </v8:item>
    </Title>
    <Font ref="style:LargeTextFont" height="12" bold="true" kind="StyleItem"/>
    <TextColor>
        <v8:Color>web:Red</v8:Color>
    </TextColor>
    <BackColor>
        <v8:Color>web:LightYellow</v8:Color>
    </BackColor>
    <HorizontalAlign>Center</HorizontalAlign>
    <Hyperlink>true</Hyperlink>
</LabelDecoration>
```

### 2.4 Флажок (CheckBoxField)

```xml
<CheckBoxField name="ФискальныйВозврат" id="30">
    <DataPath>ФискальныйВозврат</DataPath>
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>Фискальный возврат (пробить чек)</v8:content>
        </v8:item>
    </Title>
    <TitleLocation>Right</TitleLocation>
    <CheckBoxType>Switcher</CheckBoxType>
    <ContextMenu name="ФискальныйВозвратКонтекстноеМеню" id="31"/>
    <ExtendedTooltip name="ФискальныйВозвратРасширеннаяПодсказка" id="32"/>
    <Events>
        <Event name="OnChange">ФискальныйВозвратПриИзменении</Event>
    </Events>
</CheckBoxField>
```

**Типы флажка (CheckBoxType):**
- `Standard` — стандартный флажок
- `Switcher` — переключатель (iOS-стиль)

### 2.5 Кнопка (Button)

```xml
<Button name="КнопкаОплатить" id="40">
    <Type>UsualButton</Type>
    <DefaultButton>true</DefaultButton>
    <Width>15</Width>
    <Height>3</Height>
    <CommandName>Form.Command.Оплатить</CommandName>
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>ОПЛАТИТЬ (F9)</v8:content>
        </v8:item>
    </Title>
    <Shortcut>F9</Shortcut>
    <Representation>PictureAndText</Representation>
    <Picture>
        <xr:Ref>StdPicture.OK</xr:Ref>
        <xr:LoadTransparent>true</xr:LoadTransparent>
    </Picture>
    <PictureLocation>Left</PictureLocation>
    <Font ref="style:LargeTextFont" height="12" bold="true" kind="StyleItem"/>
    <ExtendedTooltip name="КнопкаОплатитьРасширеннаяПодсказка" id="41"/>
</Button>
```

**Типы кнопки (Type):**
- `UsualButton` — обычная кнопка
- `CommandBarButton` — кнопка командной панели
- `Hyperlink` — гиперссылка

**Представление (Representation):**
- `Auto` — автоматически
- `Text` — только текст
- `Picture` — только картинка
- `PictureAndText` — картинка и текст

**Стандартные картинки (Picture):**
- `StdPicture.OK`
- `StdPicture.Cancel`
- `StdPicture.Write`
- `StdPicture.Refresh`
- `StdPicture.Find`
- `StdPicture.Delete`
- `StdPicture.Add`
- `StdPicture.Edit`
- `StdPicture.Print`

### 2.6 Таблица формы (Table)

```xml
<Table name="Товары" id="50">
    <Representation>List</Representation>
    <DataPath>Объект.Товары</DataPath>
    <RowFilter xsi:nil="true"/>
    
    <!-- Поведение -->
    <AutoInsertNewRow>true</AutoInsertNewRow>
    <EnableStartDrag>true</EnableStartDrag>
    <EnableDrag>true</EnableDrag>
    <ReadOnly>false</ReadOnly>
    <AutoAddIncomplete>false</AutoAddIncomplete>
    
    <!-- Размеры -->
    <Height>15</Height>
    <HorizontalStretch>true</HorizontalStretch>
    <VerticalStretch>true</VerticalStretch>
    
    <!-- Отображение дополнений -->
    <SearchStringLocation>None</SearchStringLocation>
    <ViewStatusLocation>None</ViewStatusLocation>
    <SearchControlLocation>None</SearchControlLocation>
    
    <!-- Служебные элементы -->
    <ContextMenu name="ТоварыКонтекстноеМеню" id="51"/>
    <AutoCommandBar name="ТоварыКоманднаяПанель" id="52">
        <Autofill>false</Autofill>
    </AutoCommandBar>
    <ExtendedTooltip name="ТоварыРасширеннаяПодсказка" id="53"/>
    
    <!-- Дополнения таблицы -->
    <SearchStringAddition name="ТоварыСтрокаПоиска" id="54">
        <AdditionSource>
            <Item>Товары</Item>
            <Type>SearchStringRepresentation</Type>
        </AdditionSource>
        <ContextMenu name="ТоварыСтрокаПоискаКонтекстноеМеню" id="55"/>
        <ExtendedTooltip name="ТоварыСтрокаПоискаРасширеннаяПодсказка" id="56"/>
    </SearchStringAddition>
    
    <ViewStatusAddition name="ТоварыСостояниеПросмотра" id="57">
        <AdditionSource>
            <Item>Товары</Item>
            <Type>ViewStatusRepresentation</Type>
        </AdditionSource>
    </ViewStatusAddition>
    
    <SearchControlAddition name="ТоварыУправлениеПоиском" id="60">
        <AdditionSource>
            <Item>Товары</Item>
            <Type>SearchControl</Type>
        </AdditionSource>
    </SearchControlAddition>
    
    <!-- События -->
    <Events>
        <Event name="Selection">ТоварыВыбор</Event>
        <Event name="OnActivateRow">ТоварыПриАктивизацииСтроки</Event>
        <Event name="OnActivateField">ТоварыПриАктивизацииПоля</Event>
        <Event name="OnChange">ТоварыПриИзменении</Event>
        <Event name="BeforeAddRow">ТоварыПередДобавлениемСтроки</Event>
        <Event name="AfterDeleteRow">ТоварыПослеУдаленияСтроки</Event>
        <Event name="OnStartEdit">ТоварыПриНачалеРедактирования</Event>
        <Event name="OnEndEdit">ТоварыПриОкончанииРедактирования</Event>
    </Events>
    
    <!-- Колонки -->
    <ChildItems>
        <LabelField name="ТоварыНомерСтроки" id="63">
            <DataPath>Объект.Товары.LineNumber</DataPath>
            <EditMode>EnterOnInput</EditMode>
        </LabelField>
        <InputField name="ТоварыНоменклатура" id="64">
            <DataPath>Объект.Товары.Номенклатура</DataPath>
            <EditMode>EnterOnInput</EditMode>
            <Events>
                <Event name="OnChange">ТоварыНоменклатураПриИзменении</Event>
            </Events>
        </InputField>
        <InputField name="ТоварыКоличество" id="65">
            <DataPath>Объект.Товары.Количество</DataPath>
            <Width>8</Width>
            <AutoMaxWidth>false</AutoMaxWidth>
            <HorizontalStretch>false</HorizontalStretch>
            <Format>ЧДЦ=3</Format>
        </InputField>
    </ChildItems>
</Table>
```

**События Table:**

| Событие | Описание |
|---------|----------|
| `Selection` | Выбор строки (двойной клик) |
| `OnActivateRow` | При активизации строки |
| `OnActivateField` | При активизации поля |
| `OnChange` | При изменении данных |
| `BeforeAddRow` | Перед добавлением строки |
| `BeforeDeleteRow` | Перед удалением строки |
| `AfterDeleteRow` | После удаления строки |
| `OnStartEdit` | При начале редактирования |
| `OnEndEdit` | При окончании редактирования |
| `BeforeRowChange` | Перед изменением строки |
| `Drag` | При перетаскивании |
| `DragStart` | При начале перетаскивания |
| `DragEnd` | При окончании перетаскивания |
| `DragCheck` | Проверка возможности перетаскивания |

### 2.7 Группа элементов (UsualGroup)

```xml
<UsualGroup name="ГруппаШапка" id="70">
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>Шапка документа</v8:content>
        </v8:item>
    </Title>
    <Group>Horizontal</Group>
    <Representation>None</Representation>
    <ShowTitle>false</ShowTitle>
    <Width>40</Width>
    <HorizontalStretch>true</HorizontalStretch>
    <VerticalStretch>false</VerticalStretch>
    <ExtendedTooltip name="ГруппаШапкаРасширеннаяПодсказка" id="71"/>
    <ChildItems>
        <!-- Дочерние элементы -->
    </ChildItems>
</UsualGroup>
```

**Типы группировки (Group):**

| Значение | Описание |
|----------|----------|
| `Horizontal` | Горизонтальная |
| `Vertical` | Вертикальная |
| `HorizontalIfPossible` | Горизонтальная если возможно |
| `AlwaysHorizontal` | Всегда горизонтальная |

**Представление группы (Representation):**

| Значение | Описание |
|----------|----------|
| `None` | Без оформления |
| `WeakSeparation` | Слабое разделение |
| `NormalSeparation` | Обычное разделение |
| `StrongSeparation` | Сильное разделение |

### 2.8 Страницы (Pages / Page)

```xml
<Pages name="Страницы" id="80">
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>Страницы</v8:content>
        </v8:item>
    </Title>
    <PagesRepresentation>TabsOnTop</PagesRepresentation>
    <ExtendedTooltip name="СтраницыРасширеннаяПодсказка" id="81"/>
    <ChildItems>
        <Page name="СтраницаТовары" id="82">
            <Title>
                <v8:item>
                    <v8:lang>ru</v8:lang>
                    <v8:content>Товары</v8:content>
                </v8:item>
            </Title>
            <ExtendedTooltip name="СтраницаТоварыРасширеннаяПодсказка" id="83"/>
            <ChildItems>
                <!-- Содержимое страницы -->
            </ChildItems>
        </Page>
        <Page name="СтраницаОплата" id="84">
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

**Представление страниц (PagesRepresentation):**
- `TabsOnTop` — вкладки сверху
- `TabsOnBottom` — вкладки снизу
- `TabsOnLeft` — вкладки слева
- `TabsOnRight` — вкладки справа
- `None` — без вкладок

---

## 3. Расширенные элементы форм

### 3.1 Поле табличного документа (SpreadsheetDocumentField)

Мощный элемент для отображения и редактирования табличных документов. Используется для отчётов, печатных форм и интерактивных документов.

```xml
<SpreadsheetDocumentField name="ТабличныйДокумент" id="90">
    <DataPath>ТабличныйДокумент</DataPath>
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>Результат</v8:content>
        </v8:item>
    </Title>
    <Width>80</Width>
    <Height>20</Height>
    <HorizontalStretch>true</HorizontalStretch>
    <VerticalStretch>true</VerticalStretch>
    <Output>Auto</Output>
    <Edit>true</Edit>
    <ShowGroups>true</ShowGroups>
    <ShowHeaders>true</ShowHeaders>
    <ShowGrid>true</ShowGrid>
    <Protection>false</Protection>
    <ContextMenu name="ТабличныйДокументКонтекстноеМеню" id="91"/>
    <ExtendedTooltip name="ТабличныйДокументРасширеннаяПодсказка" id="92"/>
    <Events>
        <Event name="Selection">ТабличныйДокументВыбор</Event>
        <Event name="OnActivateArea">ТабличныйДокументПриАктивизацииОбласти</Event>
    </Events>
</SpreadsheetDocumentField>
```

**Ключевые свойства:**

| Свойство | Тип | Описание |
|----------|-----|----------|
| `Output` | Enum | Режим вывода (Auto, Allow, Deny) |
| `Edit` | Boolean | Разрешить редактирование |
| `ShowGroups` | Boolean | Показывать группировки |
| `ShowHeaders` | Boolean | Показывать заголовки строк/колонок |
| `ShowGrid` | Boolean | Показывать сетку |
| `Protection` | Boolean | Защита от редактирования |
| `ViewScalingMode` | Enum | Режим масштабирования |

**Возможности табличного документа:**
- Группировка строк и колонок с иерархией
- Расшифровка (drill-down) при клике на ячейку
- Комментарии к ячейкам
- Разная ширина колонок для разных строк
- Экспорт в xlsx, docx, pdf, ods
- Ввод данных пользователем

### 3.2 Поле картинки (PictureField)

```xml
<PictureField name="Изображение" id="100">
    <DataPath>Изображение</DataPath>
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>Фото товара</v8:content>
        </v8:item>
    </Title>
    <Width>20</Width>
    <Height>15</Height>
    <PictureSize>Proportionally</PictureSize>
    <Hyperlink>false</Hyperlink>
    <Zoomable>true</Zoomable>
    <FileDragMode>AsFileRef</FileDragMode>
    <ContextMenu name="ИзображениеКонтекстноеМеню" id="101"/>
    <ExtendedTooltip name="ИзображениеРасширеннаяПодсказка" id="102"/>
    <Events>
        <Event name="Click">ИзображениеНажатие</Event>
    </Events>
</PictureField>
```

**Режимы размера картинки (PictureSize):**
- `AutoSize` — автоматический размер
- `Proportionally` — пропорционально
- `Stretch` — растянуть
- `Tile` — плитка
- `RealSize` — реальный размер

### 3.3 Поле диаграммы (ChartField)

```xml
<ChartField name="Диаграмма" id="110">
    <DataPath>Диаграмма</DataPath>
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>Динамика продаж</v8:content>
        </v8:item>
    </Title>
    <Width>60</Width>
    <Height>20</Height>
    <HorizontalStretch>true</HorizontalStretch>
    <VerticalStretch>true</VerticalStretch>
    <ContextMenu name="ДиаграммаКонтекстноеМеню" id="111"/>
    <ExtendedTooltip name="ДиаграммаРасширеннаяПодсказка" id="112"/>
    <Events>
        <Event name="Selection">ДиаграммаВыбор</Event>
    </Events>
</ChartField>
```

**Типы диаграмм:**
- График (Line)
- Гистограмма (Bar)
- Круговая (Pie)
- Изометрическая (3D)
- Биржевая (Stock)
- Диаграмма Ганта (GanttChart)
- Дендрограмма (Dendrogram)

### 3.4 Поле форматированного документа (FormattedDocumentField)

```xml
<FormattedDocumentField name="Описание" id="120">
    <DataPath>Описание</DataPath>
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>Описание товара</v8:content>
        </v8:item>
    </Title>
    <Width>60</Width>
    <Height>10</Height>
    <HorizontalStretch>true</HorizontalStretch>
    <Edit>true</Edit>
    <ContextMenu name="ОписаниеКонтекстноеМеню" id="121"/>
    <ExtendedTooltip name="ОписаниеРасширеннаяПодсказка" id="122"/>
</FormattedDocumentField>
```

**Возможности:**
- Форматирование текста (шрифты, цвета, выравнивание)
- Гиперссылки
- Изображения внутри текста

### 3.5 Поле HTML-документа (HTMLDocumentField)

```xml
<HTMLDocumentField name="HTML" id="130">
    <DataPath>HTML</DataPath>
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>Веб-контент</v8:content>
        </v8:item>
    </Title>
    <Width>80</Width>
    <Height>30</Height>
    <HorizontalStretch>true</HorizontalStretch>
    <VerticalStretch>true</VerticalStretch>
    <ContextMenu name="HTMLКонтекстноеМеню" id="131"/>
    <ExtendedTooltip name="HTMLРасширеннаяПодсказка" id="132"/>
    <Events>
        <Event name="DocumentComplete">HTMLДокументСформирован</Event>
        <Event name="OnClick">HTMLПриНажатии</Event>
    </Events>
</HTMLDocumentField>
```

### 3.6 Поле географической схемы (GeographicalSchemaField)

```xml
<GeographicalSchemaField name="Карта" id="140">
    <DataPath>Карта</DataPath>
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>География продаж</v8:content>
        </v8:item>
    </Title>
    <Width>80</Width>
    <Height>40</Height>
    <HorizontalStretch>true</HorizontalStretch>
    <VerticalStretch>true</VerticalStretch>
    <ContextMenu name="КартаКонтекстноеМеню" id="141"/>
    <ExtendedTooltip name="КартаРасширеннаяПодсказка" id="142"/>
    <Events>
        <Event name="Selection">КартаВыбор</Event>
    </Events>
</GeographicalSchemaField>
```

### 3.7 Поле графической схемы (GraphicalSchemaField)

```xml
<GraphicalSchemaField name="Схема" id="150">
    <DataPath>Схема</DataPath>
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>Организационная структура</v8:content>
        </v8:item>
    </Title>
    <Width>60</Width>
    <Height>30</Height>
    <HorizontalStretch>true</HorizontalStretch>
    <VerticalStretch>true</VerticalStretch>
    <Edit>false</Edit>
    <ContextMenu name="СхемаКонтекстноеМеню" id="151"/>
    <ExtendedTooltip name="СхемаРасширеннаяПодсказка" id="152"/>
</GraphicalSchemaField>
```

**Применение:**
- Организационные диаграммы
- Блок-схемы алгоритмов
- Схемы бизнес-процессов
- Карты помещений

### 3.8 Поле периода (PeriodField)

```xml
<PeriodField name="Период" id="160">
    <DataPath>Период</DataPath>
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>Период отчёта</v8:content>
        </v8:item>
    </Title>
    <EditMode>EnterOnInput</EditMode>
    <ContextMenu name="ПериодКонтекстноеМеню" id="161"/>
    <ExtendedTooltip name="ПериодРасширеннаяПодсказка" id="162"/>
    <Events>
        <Event name="OnChange">ПериодПриИзменении</Event>
    </Events>
</PeriodField>
```

### 3.9 Радио-кнопки (RadioButtonField)

```xml
<RadioButtonField name="ВидОплаты" id="170">
    <DataPath>ВидОплаты</DataPath>
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>Вид оплаты</v8:content>
        </v8:item>
    </Title>
    <RadioButtonType>Tumbler</RadioButtonType>
    <ColumnsCount>3</ColumnsCount>
    <ContextMenu name="ВидОплатыКонтекстноеМеню" id="171"/>
    <ExtendedTooltip name="ВидОплатыРасширеннаяПодсказка" id="172"/>
    <ChoiceList>
        <item>
            <Presentation>Наличные</Presentation>
            <Value xsi:type="xs:decimal">1</Value>
        </item>
        <item>
            <Presentation>Безналичные</Presentation>
            <Value xsi:type="xs:decimal">2</Value>
        </item>
    </ChoiceList>
    <Events>
        <Event name="OnChange">ВидОплатыПриИзменении</Event>
    </Events>
</RadioButtonField>
```

**Типы радио-кнопок (RadioButtonType):**
- `RadioButtons` — классические радио-кнопки
- `Tumbler` — переключатели (iOS-стиль)

### 3.10 Дерево значений (FormDataTree)

```xml
<Table name="ДеревоТоваров" id="180">
    <Representation>Tree</Representation>
    <DataPath>ДеревоТоваров</DataPath>
    <RowPictureDataPath>ДеревоТоваров.Картинка</RowPictureDataPath>
    <Height>20</Height>
    <HorizontalStretch>true</HorizontalStretch>
    <VerticalStretch>true</VerticalStretch>
    <InitialTreeView>ExpandAllLevels</InitialTreeView>
    <ContextMenu name="ДеревоТоваровКонтекстноеМеню" id="181"/>
    <ExtendedTooltip name="ДеревоТоваровРасширеннаяПодсказка" id="182"/>
    <Events>
        <Event name="Selection">ДеревоТоваровВыбор</Event>
        <Event name="OnActivateRow">ДеревоТоваровПриАктивизацииСтроки</Event>
    </Events>
    <ChildItems>
        <InputField name="ДеревоТоваровНаименование" id="183">
            <DataPath>ДеревоТоваров.Наименование</DataPath>
        </InputField>
    </ChildItems>
</Table>
```

**Начальный вид дерева (InitialTreeView):**
- `NoExpand` — свёрнуто
- `ExpandTopLevel` — развёрнут первый уровень
- `ExpandAllLevels` — развёрнуты все уровни

### 3.11 Декорация-картинка (PictureDecoration)

```xml
<PictureDecoration name="ДекорацияЛоготип" id="190">
    <Picture>
        <xr:Ref>CommonPicture.Логотип</xr:Ref>
    </Picture>
    <Width>10</Width>
    <Height>5</Height>
    <PictureSize>Proportionally</PictureSize>
    <Hyperlink>true</Hyperlink>
    <ExtendedTooltip name="ДекорацияЛоготипРасширеннаяПодсказка" id="191"/>
    <Events>
        <Event name="Click">ДекорацияЛоготипНажатие</Event>
    </Events>
</PictureDecoration>
```

### 3.12 Поле планировщика (Scheduler)

```xml
<SchedulerField name="Планировщик" id="200">
    <DataPath>Планировщик</DataPath>
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>Расписание</v8:content>
        </v8:item>
    </Title>
    <Width>80</Width>
    <Height>30</Height>
    <HorizontalStretch>true</HorizontalStretch>
    <VerticalStretch>true</VerticalStretch>
    <ContextMenu name="ПланировщикКонтекстноеМеню" id="201"/>
    <ExtendedTooltip name="ПланировщикРасширеннаяПодсказка" id="202"/>
</SchedulerField>
```

### 3.13 Диаграмма Ганта (GanttChartField)

```xml
<GanttChartField name="ДиаграммаГанта" id="210">
    <DataPath>ДиаграммаГанта</DataPath>
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>План проекта</v8:content>
        </v8:item>
    </Title>
    <Width>80</Width>
    <Height>25</Height>
    <HorizontalStretch>true</HorizontalStretch>
    <VerticalStretch>true</VerticalStretch>
    <ContextMenu name="ДиаграммаГантаКонтекстноеМеню" id="211"/>
    <ExtendedTooltip name="ДиаграммаГантаРасширеннаяПодсказка" id="212"/>
    <Events>
        <Event name="Selection">ДиаграммаГантаВыбор</Event>
        <Event name="OnActivateRow">ДиаграммаГантаПриАктивизацииСтроки</Event>
    </Events>
</GanttChartField>
```

### 3.14 Дендрограмма (DendrogramField)

```xml
<DendrogramField name="Дендрограмма" id="220">
    <DataPath>Дендрограмма</DataPath>
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>Кластерный анализ</v8:content>
        </v8:item>
    </Title>
    <Width>60</Width>
    <Height>30</Height>
    <HorizontalStretch>true</HorizontalStretch>
    <VerticalStretch>true</VerticalStretch>
    <ContextMenu name="ДендрограммаКонтекстноеМеню" id="221"/>
    <ExtendedTooltip name="ДендрограммаРасширеннаяПодсказка" id="222"/>
</DendrogramField>
```

---

## 4. Реквизиты формы

### 4.1 Основной реквизит (объект)

```xml
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
```

### 4.2 Реквизит-ссылка

```xml
<Attribute name="ВыбранныйСклад" id="2">
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>Склад</v8:content>
        </v8:item>
    </Title>
    <Type>
        <v8:Type>cfg:CatalogRef.Склады</v8:Type>
    </Type>
</Attribute>
```

### 4.3 Примитивные типы

```xml
<!-- Строка -->
<Attribute name="СтрокаПоиска" id="3">
    <Type>
        <v8:Type>xs:string</v8:Type>
        <v8:StringQualifiers>
            <v8:Length>100</v8:Length>
            <v8:AllowedLength>Variable</v8:AllowedLength>
        </v8:StringQualifiers>
    </Type>
</Attribute>

<!-- Число -->
<Attribute name="НомерСтраницы" id="4">
    <Type>
        <v8:Type>xs:decimal</v8:Type>
        <v8:NumberQualifiers>
            <v8:Digits>5</v8:Digits>
            <v8:FractionDigits>0</v8:FractionDigits>
            <v8:AllowedSign>Nonnegative</v8:AllowedSign>
        </v8:NumberQualifiers>
    </Type>
</Attribute>

<!-- Булево -->
<Attribute name="РежимВыбора" id="5">
    <Type>
        <v8:Type>xs:boolean</v8:Type>
    </Type>
</Attribute>

<!-- Дата -->
<Attribute name="ДатаНачала" id="6">
    <Type>
        <v8:Type>xs:dateTime</v8:Type>
        <v8:DateQualifiers>
            <v8:DateFractions>Date</v8:DateFractions>
        </v8:DateQualifiers>
    </Type>
</Attribute>
```

### 4.4 Таблица значений

```xml
<Attribute name="СписокТоваров" id="10">
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>Список товаров</v8:content>
        </v8:item>
    </Title>
    <Type>
        <v8:Type>ValueTable</v8:Type>
    </Type>
    <Columns>
        <Column name="Товар" id="1">
            <Title>
                <v8:item>
                    <v8:lang>ru</v8:lang>
                    <v8:content>Товар</v8:content>
                </v8:item>
            </Title>
            <Type>
                <v8:Type>cfg:CatalogRef.Номенклатура</v8:Type>
            </Type>
        </Column>
        <Column name="Количество" id="2">
            <Type>
                <v8:Type>xs:decimal</v8:Type>
                <v8:NumberQualifiers>
                    <v8:Digits>15</v8:Digits>
                    <v8:FractionDigits>3</v8:FractionDigits>
                    <v8:AllowedSign>Any</v8:AllowedSign>
                </v8:NumberQualifiers>
            </Type>
        </Column>
    </Columns>
</Attribute>
```

---

## 5. Команды формы

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
                <v8:content>Оплатить чек</v8:content>
            </v8:item>
        </ToolTip>
        <Action>Оплатить</Action>
        <Representation>Auto</Representation>
        <Picture>
            <xr:Ref>StdPicture.OK</xr:Ref>
        </Picture>
    </Command>
    
    <Command name="ОчиститьЧек" id="2">
        <Title>
            <v8:item>
                <v8:lang>ru</v8:lang>
                <v8:content>Очистить</v8:content>
            </v8:item>
        </Title>
        <Action>ОчиститьЧек</Action>
    </Command>
</Commands>
```

**Привязка команды к кнопке:**
```xml
<CommandName>Form.Command.Оплатить</CommandName>
```

**Стандартные команды:**
```xml
<CommandName>Form.StandardCommand.Close</CommandName>
<CommandName>Form.StandardCommand.WriteAndClose</CommandName>
<CommandName>Form.StandardCommand.Write</CommandName>
<CommandName>Form.StandardCommand.Post</CommandName>
<CommandName>Form.StandardCommand.PostAndClose</CommandName>
```

---

## 6. События

### 6.1 События формы

| Событие | Контекст | Описание |
|---------|----------|----------|
| `OnCreateAtServer` | Сервер | При создании формы на сервере |
| `OnReadAtServer` | Сервер | При чтении объекта на сервере |
| `OnOpen` | Клиент | При открытии формы |
| `BeforeClose` | Клиент | Перед закрытием формы |
| `OnClose` | Клиент | При закрытии формы |
| `BeforeWrite` | Клиент | Перед записью объекта |
| `BeforeWriteAtServer` | Сервер | Перед записью на сервере |
| `AfterWrite` | Клиент | После записи объекта |
| `AfterWriteAtServer` | Сервер | После записи на сервере |
| `OnReopen` | Клиент | При повторном открытии |
| `NotificationProcessing` | Клиент | Обработка оповещения |
| `ExternalEvent` | Клиент | Внешнее событие (сканер и т.п.) |
| `FillCheckProcessingAtServer` | Сервер | Проверка заполнения |

### 6.2 XML-структура событий

```xml
<Events>
    <Event name="OnCreateAtServer">ПриСозданииНаСервере</Event>
    <Event name="OnOpen">ПриОткрытии</Event>
    <Event name="BeforeClose">ПередЗакрытием</Event>
    <Event name="BeforeWriteAtServer">ПередЗаписьюНаСервере</Event>
    <Event name="NotificationProcessing">ОбработкаОповещения</Event>
</Events>
```

---

## 7. Программное управление

### 7.1 Видимость и доступность элементов

```bsl
&НаКлиенте
Процедура УстановитьВидимостьЭлементов()
    // Видимость
    Элементы.КнопкаОплатить.Видимость = СуммаДокумента > 0;
    
    // Только просмотр
    Элементы.Товары.ТолькоПросмотр = Статус = Перечисления.СтатусыЧекаККМ.Пробит;
    
    // Доступность
    Элементы.Склад.Доступность = НЕ Объект.Проведен;
    
    // Заголовок
    Элементы.КнопкаОплатить.Заголовок = "Оплатить: " + Формат(СуммаДокумента, "ЧДЦ=2");
КонецПроцедуры
```

### 6.2 Управление свойствами таблицы

```bsl
&НаКлиенте
Процедура НастроитьТаблицу()
    // Текущая строка
    Элементы.Товары.ТекущаяСтрока = ИдентификаторНужнойСтроки;
    
    // Текущий элемент
    Элементы.Товары.ТекущийЭлемент = Элементы.ТоварыКоличество;
    
    // Выделенные строки
    ВыделенныеСтроки = Элементы.Товары.ВыделенныеСтроки;
КонецПроцедуры
```

### 7.3 Динамическое создание элементов

```bsl
&НаСервере
Процедура СоздатьКнопкиТоваров(Группа)
    Для Каждого Товар Из БыстрыеТовары Цикл
        // Создание кнопки
        НоваяКнопка = Элементы.Добавить(
            "Кнопка_" + Товар.Код, 
            Тип("КнопкаФормы"), 
            Группа
        );
        НоваяКнопка.Заголовок = Товар.Наименование;
        НоваяКнопка.ИмяКоманды = "ДобавитьБыстрыйТовар";
        НоваяКнопка.Ширина = 15;
        НоваяКнопка.Высота = 3;
        
        // Привязка параметра
        НоваяКнопка.УстановитьДействие("Нажатие", "ОбработатьНажатиеКнопкиТовара");
    КонецЦикла;
КонецПроцедуры

&НаСервере
Процедура УдалитьКнопкиТоваров(Группа)
    МассивУдаляемых = Новый Массив;
    Для Каждого ЭлементГруппы Из Группа.ПодчиненныеЭлементы Цикл
        Если СтрНачинаетсяС(ЭлементГруппы.Имя, "Кнопка_") Тогда
            МассивУдаляемых.Добавить(ЭлементГруппы);
        КонецЕсли;
    КонецЦикла;
    
    Для Каждого Элемент Из МассивУдаляемых Цикл
        Элементы.Удалить(Элемент);
    КонецЦикла;
КонецПроцедуры
```

### 7.4 Работа с колонками таблицы

```bsl
&НаСервере
Процедура НастроитьКолонки()
    // Скрыть колонку
    Элементы.ТоварыАкцизнаяМарка.Видимость = ИспользоватьАкцизныеМарки;
    
    // Изменить ширину
    Элементы.ТоварыНоменклатура.Ширина = 40;
    
    // Формат вывода
    Элементы.ТоварыСумма.Формат = "ЧДЦ=2; ЧН=0,00";
КонецПроцедуры
```

---

## 8. Типовые обработчики РМК

### 8.1 Обработка сканирования штрихкода

```bsl
&НаКлиенте
Процедура ПолеПоискаТовараПриИзменении(Элемент)
    Штрихкод = СокрЛП(ПолеПоискаТовара);
    Если ПустаяСтрока(Штрихкод) Тогда
        Возврат;
    КонецЕсли;
    
    ДобавитьТоварПоШтрихкоду(Штрихкод);
    ПолеПоискаТовара = "";
КонецПроцедуры

&НаКлиенте
Асинх Процедура ДобавитьТоварПоШтрихкоду(Штрихкод)
    РезультатПоиска = НайтиТоварНаСервере(Штрихкод);
    
    Если РезультатПоиска.Количество() = 0 Тогда
        Ждать ПредупреждениеАсинх("Товар не найден: " + Штрихкод);
    ИначеЕсли РезультатПоиска.Количество() = 1 Тогда
        ДобавитьВКорзину(РезультатПоиска[0]);
    Иначе
        // Несколько товаров — показать выбор
        ВыбранныйТовар = Ждать ВыбратьИзСпискаАсинх(
            РезультатПоиска, 
            Элементы.ПолеПоискаТовара,
            "Выберите товар"
        );
        Если ВыбранныйТовар <> Неопределено Тогда
            ДобавитьВКорзину(ВыбранныйТовар.Значение);
        КонецЕсли;
    КонецЕсли;
КонецПроцедуры

&НаСервере
Функция НайтиТоварНаСервере(Штрихкод)
    Запрос = Новый Запрос;
    Запрос.Текст = 
    "ВЫБРАТЬ
    |    Штрихкоды.Номенклатура КАК Номенклатура,
    |    Штрихкоды.Номенклатура.Наименование КАК Наименование
    |ИЗ
    |    РегистрСведений.Штрихкоды КАК Штрихкоды
    |ГДЕ
    |    Штрихкоды.Штрихкод = &Штрихкод";
    Запрос.УстановитьПараметр("Штрихкод", Штрихкод);
    
    Результат = Новый СписокЗначений;
    Выборка = Запрос.Выполнить().Выбрать();
    Пока Выборка.Следующий() Цикл
        Результат.Добавить(Выборка.Номенклатура, Выборка.Наименование);
    КонецЦикла;
    
    Возврат Результат;
КонецФункции
```

### 7.2 Пересчёт суммы документа

```bsl
&НаКлиенте
Процедура ПересчитатьИтоги()
    ИтогоСумма = 0;
    ИтогоКоличество = 0;
    
    Для Каждого СтрокаТЧ Из Объект.Товары Цикл
        ИтогоСумма = ИтогоСумма + СтрокаТЧ.Сумма;
        ИтогоКоличество = ИтогоКоличество + СтрокаТЧ.Количество;
    КонецЦикла;
    
    Объект.СуммаДокумента = ИтогоСумма;
КонецПроцедуры

&НаКлиенте
Процедура ТоварыКоличествоПриИзменении(Элемент)
    ТекущаяСтрока = Элементы.Товары.ТекущиеДанные;
    Если ТекущаяСтрока = Неопределено Тогда
        Возврат;
    КонецЕсли;
    
    ТекущаяСтрока.Сумма = ТекущаяСтрока.Количество * ТекущаяСтрока.Цена;
    ПересчитатьИтоги();
КонецПроцедуры
```

---

## 9. Асинхронная модель

### 9.1 Асинхронные диалоги (ОБЯЗАТЕЛЬНО в 8.3.27)

```bsl
// ПРАВИЛЬНО — асинхронная модель
&НаКлиенте
Асинх Процедура УдалитьСтроку(Команда)
    Ответ = Ждать ВопросАсинх(
        "Удалить выбранную строку?",
        РежимДиалогаВопрос.ДаНет
    );
    
    Если Ответ = КодВозвратаДиалога.Да Тогда
        Элементы.Товары.ТекущиеДанные = Неопределено;
    КонецЕсли;
КонецПроцедуры

// ЗАПРЕЩЕНО — модальные вызовы
// Вопрос("Удалить?", РежимДиалогаВопрос.ДаНет)  // НЕЛЬЗЯ!
```

### 9.2 Асинхронное открытие форм

```bsl
&НаКлиенте
Асинх Процедура ВыбратьТовар(Команда)
    ПараметрыОткрытия = Новый Структура;
    ПараметрыОткрытия.Вставить("РежимВыбора", Истина);
    ПараметрыОткрытия.Вставить("МножественныйВыбор", Ложь);
    
    ВыбранныйТовар = Ждать ОткрытьФормуАсинх(
        "Справочник.Номенклатура.ФормаВыбора",
        ПараметрыОткрытия,
        ЭтотОбъект
    );
    
    Если ВыбранныйТовар <> Неопределено Тогда
        ДобавитьВКорзину(ВыбранныйТовар);
    КонецЕсли;
КонецПроцедуры
```

### 9.3 Асинхронный выбор файла

```bsl
&НаКлиенте
Асинх Процедура ВыбратьФайл(Команда)
    ДиалогВыбора = Новый ДиалогВыбораФайла(РежимДиалогаВыбораФайла.Открытие);
    ДиалогВыбора.Фильтр = "Файлы Excel (*.xlsx)|*.xlsx";
    
    ВыбранныеФайлы = Ждать ДиалогВыбора.ВыбратьАсинх();
    
    Если ВыбранныеФайлы <> Неопределено И ВыбранныеФайлы.Количество() > 0 Тогда
        ПутьКФайлу = ВыбранныеФайлы[0];
        ЗагрузитьДанныеИзФайла(ПутьКФайлу);
    КонецЕсли;
КонецПроцедуры
```

### 9.4 Асинхронные оповещения (обратная совместимость)

```bsl
// Вариант 1: Асинх/Ждать (рекомендуется)
&НаКлиенте
Асинх Процедура ПоказатьСообщение()
    Ждать ПредупреждениеАсинх("Операция выполнена успешно!");
КонецПроцедуры

// Вариант 2: ОписаниеОповещения (для обратной совместимости)
&НаКлиенте
Процедура ПоказатьВопрос()
    Оповещение = Новый ОписаниеОповещения("ПослеОтветаНаВопрос", ЭтотОбъект);
    ПоказатьВопрос(Оповещение, "Продолжить?", РежимДиалогаВопрос.ДаНет);
КонецПроцедуры

&НаКлиенте
Процедура ПослеОтветаНаВопрос(Результат, ДопПараметры) Экспорт
    Если Результат = КодВозвратаДиалога.Да Тогда
        // Обработка
    КонецЕсли;
КонецПроцедуры
```

---

## 10. Новое в 8.3.27

### 10.1 WebSocket-клиент

В версии 8.3.27 добавлена возможность создания WebSocket-клиентов напрямую из платформы без использования внешних компонент.

```bsl
&НаКлиенте
Асинх Процедура ПодключитьсяКВебСокету()
    КлиентВебСокета = Новый КлиентWebSocket;
    КлиентВебСокета.Подключиться("wss://example.com/socket");
    
    // Ожидание сообщений
    Пока КлиентВебСокета.Состояние = СостояниеКлиентаWebSocket.Открыт Цикл
        Сообщение = Ждать КлиентВебСокета.ПолучитьСообщениеАсинх();
        ОбработатьСообщение(Сообщение);
    КонецЦикла;
КонецПроцедуры
```

**Применение:**
- Интеграция с телефонией
- Электронные подписи
- Брокеры сообщений (RabbitMQ, ZeroMQ)
- Реалтайм-уведомления

### 10.2 Аутентификация по email

```bsl
// Новый способ аутентификации — подтверждение по email
// Настраивается в списке пользователей ИБ
// Пользователь вводит email → получает код → вводит код для входа
```

### 10.3 Асинхронные конструкторы внешних компонент

```bsl
&НаКлиенте
Асинх Процедура СоздатьВнешнююКомпоненту()
    // Для веб-клиента теперь рекомендуется использовать
    // асинхронные конструкторы внешних компонент
    Компонента = Ждать Новый("AddIn.МояКомпонента", Неопределено);
    Результат = Ждать Компонента.ВыполнитьОперациюАсинх();
КонецПроцедуры
```

### 10.4 Форматированная строка в СКД

Теперь форматированную строку можно использовать:
- В предопределённых шаблонах СКД
- В условном оформлении как текст
- В функциях языка 1С, возвращающих форматированную строку
- Как значение параметра ячейки табличного документа

```bsl
// Пример использования в СКД
ФорматированнаяСтрока = Новый ФорматированнаяСтрока(
    "Важно: ", Новый Шрифт(,, Истина),
    "Документ просрочен", Новый Шрифт, Новый Цвет(255, 0, 0)
);
```

### 10.5 Улучшения системы взаимодействия

- Видеозвонки в тонком клиенте на Linux и macOS
- Функция "Поднять руку" при видеозвонках
- Поиск по контекстным обсуждениям
- Интеграция с WhatsApp: можно инициировать разговор первым

### 10.6 Увеличение строк табличных частей

```xml
<!-- Теперь максимальное количество строк в табличных частях
     увеличено до ~1 000 000 000 (вместо ~100 000) -->
<TabularSection name="Товары">
    <RowNumberLength>9</RowNumberLength>  <!-- Новый атрибут -->
</TabularSection>
```

### 10.7 Совместимость

**Прекращена поддержка:**
- Windows XP, Windows Vista
- Windows Server 2003, Windows Server 2008
- Firefox версии < 68

**Добавлена поддержка:**
- PostgreSQL 16
- Android API Level 35 (Android 15)

---

## Приложение: Шаблоны элементов форм

### Шаблон кнопки командной панели

```xml
<Button name="ФормаКнопкаСохранить" id="100">
    <Type>CommandBarButton</Type>
    <Representation>PictureAndText</Representation>
    <CommandName>Form.Command.Сохранить</CommandName>
    <Picture>
        <xr:Ref>StdPicture.Write</xr:Ref>
        <xr:LoadTransparent>true</xr:LoadTransparent>
    </Picture>
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>Сохранить</v8:content>
        </v8:item>
    </Title>
    <ExtendedTooltip name="ФормаКнопкаСохранитьРасширеннаяПодсказка" id="101"/>
</Button>
```

### Шаблон поля со ссылкой на справочник

```xml
<InputField name="Номенклатура" id="200">
    <DataPath>Объект.Номенклатура</DataPath>
    <Title>
        <v8:item>
            <v8:lang>ru</v8:lang>
            <v8:content>Номенклатура</v8:content>
        </v8:item>
    </Title>
    <EditMode>EnterOnInput</EditMode>
    <ExtendedEditMultipleValues>true</ExtendedEditMultipleValues>
    <ContextMenu name="НоменклатураКонтекстноеМеню" id="201"/>
    <ExtendedTooltip name="НоменклатураРасширеннаяПодсказка" id="202"/>
    <Events>
        <Event name="OnChange">НоменклатураПриИзменении</Event>
        <Event name="StartChoice">НоменклатураНачалоВыбора</Event>
    </Events>
</InputField>
```

---

> **Документ создан:** 2026-01-24  
> **Версия:** 3.0 (дополнено из интернет-исследования)  
> **Платформа:** 1С:Предприятие 8.3.27  
> **Связанная документация:** [XML-структура конфигурации](xml-structure-8.3.27.md)

---

## Источники

- [1C Developer Network — Forms](https://1c-dn.com/1c_enterprise/forms/)
- [1C Developer Network — GUI Components](https://1c-dn.com/1c_enterprise/gui_components/)
- [1C Developer Network — Spreadsheet Document](https://1c-dn.com/1c_enterprise/spreadsheet_document/)
- [1C Developer Network — Charts](https://1c-dn.com/1c_enterprise/charts/)
- [1C Developer Network — New Features 8.3.27](https://1c-dn.com/1c_enterprise/new_features_in_version_8_3_27/)