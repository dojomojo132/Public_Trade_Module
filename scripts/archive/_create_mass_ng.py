# -*- coding: utf-8 -*-
"""Создание обработки Анл_МассоваяУстановкаНалоговыхГрупп в PTM_Analytics"""
import os

BASE = r"D:\Git\Public_Trade_Module\Конфигурация_PTM_Analytics"
DP_DIR = os.path.join(BASE, "DataProcessors")
DP_NAME = "Анл_МассоваяУстановкаНалоговыхГрупп"

# UUIDs
DP_UUID = "0dbb551f-fac4-42f0-aa76-41bf5af6d345"
OBJ_TYPE_ID = "1ec24092-0ccd-4a0c-b010-590d855dfc13"
OBJ_VALUE_ID = "9aaf643b-bdda-48ab-8b19-9106b544e545"
MGR_TYPE_ID = "7c7c0a7a-e661-4458-bd8f-0b773a4bbfc4"
MGR_VALUE_ID = "3c7934b1-619f-42b8-ac19-da5361a3298f"
ATTR_NG_UUID = "7d99d9ce-6b1f-4257-8e61-d11f597262fb"
TS_TOVARY_UUID = "63f4a120-f55a-4092-aee7-45dd3a021beb"
TS_ATTR_OTMETKA = "0c07e95f-3cf6-46bf-9329-168a913d2fe5"
TS_ATTR_NOM = "f9653328-242b-4833-909c-e6db7083c538"
TS_ATTR_NAIM = "5d23738c-de76-4199-b754-bea283def9ef"
TS_ATTR_CUR_NG = "a8242180-4586-4253-b70f-056ee4bfaae1"
FORM_UUID = "4de0495f-566d-4e3a-9657-e1f43a6e394a"

NS_HEADER = ('xmlns="http://v8.1c.ru/8.3/MDClasses" '
    'xmlns:app="http://v8.1c.ru/8.2/managed-application/core" '
    'xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" '
    'xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" '
    'xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" '
    'xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" '
    'xmlns:style="http://v8.1c.ru/8.1/data/ui/style" '
    'xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" '
    'xmlns:v8="http://v8.1c.ru/8.1/data/core" '
    'xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" '
    'xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" '
    'xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" '
    'xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" '
    'xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" '
    'xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" '
    'xmlns:xs="http://www.w3.org/2001/XMLSchema" '
    'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
    'version="2.20"')


def write_bom(path, content, crlf=True):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if crlf:
        content = content.replace('\n', '\r\n')
    with open(path, 'w', encoding='utf-8-sig', newline='') as f:
        f.write(content)
    print(f"  OK: {os.path.relpath(path, BASE)}")


# === 1. DataProcessor descriptor ===
dp_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject {NS_HEADER}>
\t<DataProcessor uuid="{DP_UUID}">
\t\t<InternalInfo>
\t\t\t<xr:GeneratedType name="DataProcessorObject.{DP_NAME}" category="Object">
\t\t\t\t<xr:TypeId>{OBJ_TYPE_ID}</xr:TypeId>
\t\t\t\t<xr:ValueId>{OBJ_VALUE_ID}</xr:ValueId>
\t\t\t</xr:GeneratedType>
\t\t\t<xr:GeneratedType name="DataProcessorManager.{DP_NAME}" category="Manager">
\t\t\t\t<xr:TypeId>{MGR_TYPE_ID}</xr:TypeId>
\t\t\t\t<xr:ValueId>{MGR_VALUE_ID}</xr:ValueId>
\t\t\t</xr:GeneratedType>
\t\t</InternalInfo>
\t\t<Properties>
\t\t\t<Name>{DP_NAME}</Name>
\t\t\t<Synonym>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Массовая установка налоговых групп</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Synonym>
\t\t\t<Comment>Массовая установка налоговых групп для Номенклатуры</Comment>
\t\t\t<UseStandardCommands>true</UseStandardCommands>
\t\t\t<DefaultForm>DataProcessor.{DP_NAME}.Form.Форма</DefaultForm>
\t\t\t<AuxiliaryForm/>
\t\t\t<IncludeHelpInContents>false</IncludeHelpInContents>
\t\t\t<ExtendedPresentation/>
\t\t\t<Explanation/>
\t\t</Properties>
\t\t<ChildObjects>
\t\t\t<Attribute>НалоговаяГруппа</Attribute>
\t\t\t<TabularSection>Товары</TabularSection>
\t\t\t<Form>Форма</Form>
\t\t</ChildObjects>
\t\t<Attributes uuid="{ATTR_NG_UUID}">
\t\t\t<Properties>
\t\t\t\t<Name>НалоговаяГруппа</Name>
\t\t\t\t<Synonym>
\t\t\t\t\t<v8:item>
\t\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t\t<v8:content>Налоговая группа</v8:content>
\t\t\t\t\t</v8:item>
\t\t\t\t</Synonym>
\t\t\t\t<Comment/>
\t\t\t\t<Type>
\t\t\t\t\t<v8:Type xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config">d5p1:CatalogRef.НалоговыеГруппы</v8:Type>
\t\t\t\t</Type>
\t\t\t\t<ToolTip/>
\t\t\t\t<MinValue xsi:type="xs:string"/>
\t\t\t\t<MaxValue xsi:type="xs:string"/>
\t\t\t\t<FillChecking>DontCheck</FillChecking>
\t\t\t\t<ChoiceParameters/>
\t\t\t\t<QuickChoice>DontUse</QuickChoice>
\t\t\t\t<CreateOnInput>DontUse</CreateOnInput>
\t\t\t\t<FillValue xsi:type="xs:string"/>
\t\t\t\t<Indexing>DontIndex</Indexing>
\t\t\t</Properties>
\t\t</Attributes>
\t\t<TabularSections uuid="{TS_TOVARY_UUID}">
\t\t\t<Properties>
\t\t\t\t<Name>Товары</Name>
\t\t\t\t<Synonym>
\t\t\t\t\t<v8:item>
\t\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t\t<v8:content>Товары</v8:content>
\t\t\t\t\t</v8:item>
\t\t\t\t</Synonym>
\t\t\t\t<Comment/>
\t\t\t\t<ToolTip/>
\t\t\t</Properties>
\t\t\t<ChildObjects>
\t\t\t\t<Attribute>Отметка</Attribute>
\t\t\t\t<Attribute>Номенклатура</Attribute>
\t\t\t\t<Attribute>Наименование</Attribute>
\t\t\t\t<Attribute>ТекущаяНалоговаяГруппа</Attribute>
\t\t\t</ChildObjects>
\t\t\t<Attributes uuid="{TS_ATTR_OTMETKA}">
\t\t\t\t<Properties>
\t\t\t\t\t<Name>Отметка</Name>
\t\t\t\t\t<Synonym>
\t\t\t\t\t\t<v8:item>
\t\t\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t\t\t<v8:content>Отметка</v8:content>
\t\t\t\t\t\t</v8:item>
\t\t\t\t\t</Synonym>
\t\t\t\t\t<Comment/>
\t\t\t\t\t<Type>
\t\t\t\t\t\t<v8:Type>xs:boolean</v8:Type>
\t\t\t\t\t</Type>
\t\t\t\t\t<ToolTip/>
\t\t\t\t\t<MinValue xsi:type="xs:string"/>
\t\t\t\t\t<MaxValue xsi:type="xs:string"/>
\t\t\t\t\t<FillChecking>DontCheck</FillChecking>
\t\t\t\t\t<ChoiceParameters/>
\t\t\t\t\t<QuickChoice>DontUse</QuickChoice>
\t\t\t\t\t<CreateOnInput>DontUse</CreateOnInput>
\t\t\t\t\t<FillValue xsi:type="xs:string"/>
\t\t\t\t\t<Indexing>DontIndex</Indexing>
\t\t\t\t</Properties>
\t\t\t</Attributes>
\t\t\t<Attributes uuid="{TS_ATTR_NOM}">
\t\t\t\t<Properties>
\t\t\t\t\t<Name>Номенклатура</Name>
\t\t\t\t\t<Synonym>
\t\t\t\t\t\t<v8:item>
\t\t\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t\t\t<v8:content>Номенклатура</v8:content>
\t\t\t\t\t\t</v8:item>
\t\t\t\t\t</Synonym>
\t\t\t\t\t<Comment/>
\t\t\t\t\t<Type>
\t\t\t\t\t\t<v8:Type xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config">d5p1:CatalogRef.Номенклатура</v8:Type>
\t\t\t\t\t</Type>
\t\t\t\t\t<ToolTip/>
\t\t\t\t\t<MinValue xsi:type="xs:string"/>
\t\t\t\t\t<MaxValue xsi:type="xs:string"/>
\t\t\t\t\t<FillChecking>DontCheck</FillChecking>
\t\t\t\t\t<ChoiceParameters/>
\t\t\t\t\t<QuickChoice>DontUse</QuickChoice>
\t\t\t\t\t<CreateOnInput>DontUse</CreateOnInput>
\t\t\t\t\t<FillValue xsi:type="xs:string"/>
\t\t\t\t\t<Indexing>DontIndex</Indexing>
\t\t\t\t</Properties>
\t\t\t</Attributes>
\t\t\t<Attributes uuid="{TS_ATTR_NAIM}">
\t\t\t\t<Properties>
\t\t\t\t\t<Name>Наименование</Name>
\t\t\t\t\t<Synonym>
\t\t\t\t\t\t<v8:item>
\t\t\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t\t\t<v8:content>Наименование</v8:content>
\t\t\t\t\t\t</v8:item>
\t\t\t\t\t</Synonym>
\t\t\t\t\t<Comment/>
\t\t\t\t\t<Type>
\t\t\t\t\t\t<v8:Type>xs:string</v8:Type>
\t\t\t\t\t\t<v8:StringQualifiers>
\t\t\t\t\t\t\t<v8:Length>250</v8:Length>
\t\t\t\t\t\t\t<v8:AllowedLength>Variable</v8:AllowedLength>
\t\t\t\t\t\t</v8:StringQualifiers>
\t\t\t\t\t</Type>
\t\t\t\t\t<ToolTip/>
\t\t\t\t\t<MinValue xsi:type="xs:string"/>
\t\t\t\t\t<MaxValue xsi:type="xs:string"/>
\t\t\t\t\t<FillChecking>DontCheck</FillChecking>
\t\t\t\t\t<ChoiceParameters/>
\t\t\t\t\t<QuickChoice>DontUse</QuickChoice>
\t\t\t\t\t<CreateOnInput>DontUse</CreateOnInput>
\t\t\t\t\t<FillValue xsi:type="xs:string"/>
\t\t\t\t\t<Indexing>DontIndex</Indexing>
\t\t\t\t</Properties>
\t\t\t</Attributes>
\t\t\t<Attributes uuid="{TS_ATTR_CUR_NG}">
\t\t\t\t<Properties>
\t\t\t\t\t<Name>ТекущаяНалоговаяГруппа</Name>
\t\t\t\t\t<Synonym>
\t\t\t\t\t\t<v8:item>
\t\t\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t\t\t<v8:content>Текущая налоговая группа</v8:content>
\t\t\t\t\t\t</v8:item>
\t\t\t\t\t</Synonym>
\t\t\t\t\t<Comment/>
\t\t\t\t\t<Type>
\t\t\t\t\t\t<v8:Type xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config">d5p1:CatalogRef.НалоговыеГруппы</v8:Type>
\t\t\t\t\t</Type>
\t\t\t\t\t<ToolTip/>
\t\t\t\t\t<MinValue xsi:type="xs:string"/>
\t\t\t\t\t<MaxValue xsi:type="xs:string"/>
\t\t\t\t\t<FillChecking>DontCheck</FillChecking>
\t\t\t\t\t<ChoiceParameters/>
\t\t\t\t\t<QuickChoice>DontUse</QuickChoice>
\t\t\t\t\t<CreateOnInput>DontUse</CreateOnInput>
\t\t\t\t\t<FillValue xsi:type="xs:string"/>
\t\t\t\t\t<Indexing>DontIndex</Indexing>
\t\t\t\t</Properties>
\t\t\t</Attributes>
\t\t</TabularSections>
\t</DataProcessor>
</MetaDataObject>"""

write_bom(os.path.join(DP_DIR, f"{DP_NAME}.xml"), dp_xml)


# === 2. Form descriptor ===
form_desc_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject {NS_HEADER}>
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
</MetaDataObject>"""

form_desc_path = os.path.join(DP_DIR, DP_NAME, "Forms", "Форма.xml")
write_bom(form_desc_path, form_desc_xml)


# === 3. Form.xml (layout) ===
form_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Form xmlns="http://v8.1c.ru/8.3/xcf/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
\t<AutoCommandBar name="ФормаКоманднаяПанель" id="-1">
\t\t<Autofill>true</Autofill>
\t\t<ExtendedTooltip name="ФормаКоманднаяПанельРасширеннаяПодсказка" id="50">
\t\t\t<Type>Label</Type>
\t\t</ExtendedTooltip>
\t\t<ChildItems>
\t\t\t<Button name="КнопкаЗаполнить" id="1">
\t\t\t\t<Type>CommandBarButton</Type>
\t\t\t\t<Representation>PictureAndText</Representation>
\t\t\t\t<CommandName>Form.Command.Заполнить</CommandName>
\t\t\t\t<Title>
\t\t\t\t\t<v8:item>
\t\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t\t<v8:content>Заполнить</v8:content>
\t\t\t\t\t</v8:item>
\t\t\t\t</Title>
\t\t\t\t<ExtendedTooltip name="КнопкаЗаполнитьРасширеннаяПодсказка" id="100">
\t\t\t\t\t<Type>Label</Type>
\t\t\t\t</ExtendedTooltip>
\t\t\t</Button>
\t\t\t<Button name="КнопкаУстановитьНГ" id="2">
\t\t\t\t<Type>CommandBarButton</Type>
\t\t\t\t<Representation>PictureAndText</Representation>
\t\t\t\t<DefaultButton>true</DefaultButton>
\t\t\t\t<CommandName>Form.Command.УстановитьНалоговуюГруппу</CommandName>
\t\t\t\t<Title>
\t\t\t\t\t<v8:item>
\t\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t\t<v8:content>Установить НГ</v8:content>
\t\t\t\t\t</v8:item>
\t\t\t\t</Title>
\t\t\t\t<ExtendedTooltip name="КнопкаУстановитьНГРасширеннаяПодсказка" id="101">
\t\t\t\t\t<Type>Label</Type>
\t\t\t\t</ExtendedTooltip>
\t\t\t</Button>
\t\t\t<Button name="КнопкаОтметитьВсе" id="3">
\t\t\t\t<Type>CommandBarButton</Type>
\t\t\t\t<CommandName>Form.Command.ОтметитьВсе</CommandName>
\t\t\t\t<Title>
\t\t\t\t\t<v8:item>
\t\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t\t<v8:content>Отметить все</v8:content>
\t\t\t\t\t</v8:item>
\t\t\t\t</Title>
\t\t\t\t<ExtendedTooltip name="КнопкаОтметитьВсеРасширеннаяПодсказка" id="102">
\t\t\t\t\t<Type>Label</Type>
\t\t\t\t</ExtendedTooltip>
\t\t\t</Button>
\t\t\t<Button name="КнопкаСнятьОтметки" id="4">
\t\t\t\t<Type>CommandBarButton</Type>
\t\t\t\t<CommandName>Form.Command.СнятьОтметки</CommandName>
\t\t\t\t<Title>
\t\t\t\t\t<v8:item>
\t\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t\t<v8:content>Снять отметки</v8:content>
\t\t\t\t\t</v8:item>
\t\t\t\t</Title>
\t\t\t\t<ExtendedTooltip name="КнопкаСнятьОтметкиРасширеннаяПодсказка" id="103">
\t\t\t\t\t<Type>Label</Type>
\t\t\t\t</ExtendedTooltip>
\t\t\t</Button>
\t\t</ChildItems>
\t</AutoCommandBar>
\t<Events>
\t\t<Event name="OnCreateAtServer">ПриСозданииНаСервере</Event>
\t</Events>
\t<ChildItems>
\t\t<CheckBoxField name="ПоказыватьТолькоБезНГ" id="12">
\t\t\t<DataPath>ПоказыватьТолькоБезНГ</DataPath>
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Только без налоговой группы</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<ExtendedTooltip name="ПоказыватьТолькоБезНГРасширеннаяПодсказка" id="104">
\t\t\t\t<Type>Label</Type>
\t\t\t</ExtendedTooltip>
\t\t</CheckBoxField>
\t\t<InputField name="НалоговаяГруппа" id="5">
\t\t\t<DataPath>Объект.НалоговаяГруппа</DataPath>
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Целевая налоговая группа</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<ContextMenu name="НалоговаяГруппаКонтекстноеМеню" id="105">
\t\t\t\t<Autofill>true</Autofill>
\t\t\t</ContextMenu>
\t\t\t<ExtendedTooltip name="НалоговаяГруппаРасширеннаяПодсказка" id="106">
\t\t\t\t<Type>Label</Type>
\t\t\t</ExtendedTooltip>
\t\t</InputField>
\t\t<Table name="Товары" id="6">
\t\t\t<DataPath>Объект.Товары</DataPath>
\t\t\t<ContextMenu name="ТоварыКонтекстноеМеню" id="107">
\t\t\t\t<Autofill>true</Autofill>
\t\t\t</ContextMenu>
\t\t\t<ExtendedTooltip name="ТоварыРасширеннаяПодсказка" id="108">
\t\t\t\t<Type>Label</Type>
\t\t\t</ExtendedTooltip>
\t\t\t<SearchControlAddition name="ТоварыСтрокаПоиска" id="109">
\t\t\t\t<ExtendedTooltip name="ТоварыСтрокаПоискаРасширеннаяПодсказка" id="130">
\t\t\t\t\t<Type>Label</Type>
\t\t\t\t</ExtendedTooltip>
\t\t\t</SearchControlAddition>
\t\t\t<ViewStatusAddition name="ТоварыСтрокаСостоянияПросмотра" id="110">
\t\t\t\t<ExtendedTooltip name="ТоварыСтрокаСостоянияПросмотраРасширеннаяПодсказка" id="131">
\t\t\t\t\t<Type>Label</Type>
\t\t\t\t</ExtendedTooltip>
\t\t\t</ViewStatusAddition>
\t\t\t<SearchStringAddition name="ТоварыСтрокаПоискаДоп" id="111">
\t\t\t\t<ExtendedTooltip name="ТоварыСтрокаПоискаДопРасширеннаяПодсказка" id="132">
\t\t\t\t\t<Type>Label</Type>
\t\t\t\t</ExtendedTooltip>
\t\t\t</SearchStringAddition>
\t\t\t<ChildItems>
\t\t\t\t<CheckBoxField name="ТоварыОтметка" id="7">
\t\t\t\t\t<DataPath>Объект.Товары.Отметка</DataPath>
\t\t\t\t\t<ExtendedTooltip name="ТоварыОтметкаРасширеннаяПодсказка" id="112">
\t\t\t\t\t\t<Type>Label</Type>
\t\t\t\t\t</ExtendedTooltip>
\t\t\t\t</CheckBoxField>
\t\t\t\t<InputField name="ТоварыНаименование" id="8">
\t\t\t\t\t<DataPath>Объект.Товары.Наименование</DataPath>
\t\t\t\t\t<ReadOnly>true</ReadOnly>
\t\t\t\t\t<ContextMenu name="ТоварыНаименованиеКонтекстноеМеню" id="113">
\t\t\t\t\t\t<Autofill>true</Autofill>
\t\t\t\t\t</ContextMenu>
\t\t\t\t\t<ExtendedTooltip name="ТоварыНаименованиеРасширеннаяПодсказка" id="114">
\t\t\t\t\t\t<Type>Label</Type>
\t\t\t\t\t</ExtendedTooltip>
\t\t\t\t</InputField>
\t\t\t\t<InputField name="ТоварыНоменклатура" id="9">
\t\t\t\t\t<DataPath>Объект.Товары.Номенклатура</DataPath>
\t\t\t\t\t<ReadOnly>true</ReadOnly>
\t\t\t\t\t<ContextMenu name="ТоварыНоменклатураКонтекстноеМеню" id="115">
\t\t\t\t\t\t<Autofill>true</Autofill>
\t\t\t\t\t</ContextMenu>
\t\t\t\t\t<ExtendedTooltip name="ТоварыНоменклатураРасширеннаяПодсказка" id="116">
\t\t\t\t\t\t<Type>Label</Type>
\t\t\t\t\t</ExtendedTooltip>
\t\t\t\t</InputField>
\t\t\t\t<InputField name="ТоварыТекущаяНалоговаяГруппа" id="10">
\t\t\t\t\t<DataPath>Объект.Товары.ТекущаяНалоговаяГруппа</DataPath>
\t\t\t\t\t<ReadOnly>true</ReadOnly>
\t\t\t\t\t<ContextMenu name="ТоварыТекущаяНГКонтекстноеМеню" id="117">
\t\t\t\t\t\t<Autofill>true</Autofill>
\t\t\t\t\t</ContextMenu>
\t\t\t\t\t<ExtendedTooltip name="ТоварыТекущаяНГРасширеннаяПодсказка" id="118">
\t\t\t\t\t\t<Type>Label</Type>
\t\t\t\t\t</ExtendedTooltip>
\t\t\t\t</InputField>
\t\t\t</ChildItems>
\t\t\t<CommandBarLocation>None</CommandBarLocation>
\t\t</Table>
\t\t<LabelDecoration name="НадписьИнфо" id="11">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Нажмите "Заполнить" для загрузки товаров</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<ExtendedTooltip name="НадписьИнфоРасширеннаяПодсказка" id="119">
\t\t\t\t<Type>Label</Type>
\t\t\t</ExtendedTooltip>
\t\t</LabelDecoration>
\t</ChildItems>
\t<CommandInterface/>
\t<Attributes>
\t\t<Attribute>
\t\t\t<Name>ПоказыватьТолькоБезНГ</Name>
\t\t\t<Id>1</Id>
\t\t\t<ValueType>
\t\t\t\t<v8:Type>xs:boolean</v8:Type>
\t\t\t</ValueType>
\t\t</Attribute>
\t</Attributes>
\t<Commands>
\t\t<Command>
\t\t\t<Name>Заполнить</Name>
\t\t\t<Action>Заполнить</Action>
\t\t\t<Representation>Auto</Representation>
\t\t</Command>
\t\t<Command>
\t\t\t<Name>УстановитьНалоговуюГруппу</Name>
\t\t\t<Action>УстановитьНалоговуюГруппу</Action>
\t\t\t<Representation>Auto</Representation>
\t\t</Command>
\t\t<Command>
\t\t\t<Name>ОтметитьВсе</Name>
\t\t\t<Action>ОтметитьВсе</Action>
\t\t\t<Representation>Auto</Representation>
\t\t</Command>
\t\t<Command>
\t\t\t<Name>СнятьОтметки</Name>
\t\t\t<Action>СнятьОтметки</Action>
\t\t\t<Representation>Auto</Representation>
\t\t</Command>
\t</Commands>
</Form>"""

form_xml_path = os.path.join(DP_DIR, DP_NAME, "Forms", "Форма", "Ext", "Form.xml")
write_bom(form_xml_path, form_xml)


# === 4. Module.bsl ===
module_bsl = """#Область ОбработчикиСобытийФормы

&НаСервере
Процедура ПриСозданииНаСервере(Отказ, СтандартнаяОбработка)
\t// Ничего — пользователь сначала нажимает "Заполнить"
КонецПроцедуры

#КонецОбласти

#Область ОбработчикиКоманд

&НаКлиенте
Процедура Заполнить(Команда)
\tЗаполнитьТоварыНаСервере();
КонецПроцедуры

&НаКлиенте
Процедура УстановитьНалоговуюГруппу(Команда)
\tЕсли НЕ ЗначениеЗаполнено(Объект.НалоговаяГруппа) Тогда
\t\tПоказатьПредупреждение(, "Выберите налоговую группу");
\t\tВозврат;
\tКонецЕсли;
\tУстановитьНалоговуюГруппуНаСервере();
КонецПроцедуры

&НаКлиенте
Процедура ОтметитьВсе(Команда)
\tДля Каждого СтрокаТовара Из Объект.Товары Цикл
\t\tСтрокаТовара.Отметка = Истина;
\tКонецЦикла;
КонецПроцедуры

&НаКлиенте
Процедура СнятьОтметки(Команда)
\tДля Каждого СтрокаТовара Из Объект.Товары Цикл
\t\tСтрокаТовара.Отметка = Ложь;
\tКонецЦикла;
КонецПроцедуры

#КонецОбласти

#Область СлужебныеПроцедурыИФункции

&НаСервере
Процедура ЗаполнитьТоварыНаСервере()
\t
\tОбъект.Товары.Очистить();
\t
\tЗапрос = Новый Запрос;
\tЗапрос.Текст =
\t"ВЫБРАТЬ
\t|\tНоменклатура.Ссылка КАК Номенклатура,
\t|\tНоменклатура.Наименование КАК Наименование,
\t|\tНоменклатура.НалоговаяГруппа КАК ТекущаяНалоговаяГруппа
\t|ИЗ
\t|\tСправочник.Номенклатура КАК Номенклатура
\t|ГДЕ
\t|\tНЕ Номенклатура.ЭтоГруппа
\t|\tИ НЕ Номенклатура.ПометкаУдаления";
\t
\tЕсли ПоказыватьТолькоБезНГ Тогда
\t\tЗапрос.Текст = Запрос.Текст + "
\t\t|\tИ Номенклатура.НалоговаяГруппа = ЗНАЧЕНИЕ(Справочник.НалоговыеГруппы.ПустаяСсылка)";
\tКонецЕсли;
\t
\tЗапрос.Текст = Запрос.Текст + "
\t|УПОРЯДОЧИТЬ ПО
\t|\tНоменклатура.Наименование";
\t
\tВыборка = Запрос.Выполнить().Выбрать();
\tПока Выборка.Следующий() Цикл
\t\tНоваяСтрока = Объект.Товары.Добавить();
\t\tНоваяСтрока.Отметка = Истина;
\t\tНоваяСтрока.Номенклатура = Выборка.Номенклатура;
\t\tНоваяСтрока.Наименование = Выборка.Наименование;
\t\tНоваяСтрока.ТекущаяНалоговаяГруппа = Выборка.ТекущаяНалоговаяГруппа;
\tКонецЦикла;
\t
\tОбновитьИнфо();
\t
КонецПроцедуры

&НаСервере
Процедура УстановитьНалоговуюГруппуНаСервере()
\t
\tЕсли НЕ ЗначениеЗаполнено(Объект.НалоговаяГруппа) Тогда
\t\tВозврат;
\tКонецЕсли;
\t
\tСчетчик = 0;
\tДля Каждого СтрокаТовара Из Объект.Товары Цикл
\t\tЕсли НЕ СтрокаТовара.Отметка Тогда
\t\t\tПродолжить;
\t\tКонецЕсли;
\t\t
\t\tНоменклатураОбъект = СтрокаТовара.Номенклатура.ПолучитьОбъект();
\t\tЕсли НоменклатураОбъект = Неопределено Тогда
\t\t\tПродолжить;
\t\tКонецЕсли;
\t\t
\t\tНоменклатураОбъект.НалоговаяГруппа = Объект.НалоговаяГруппа;
\t\tПопытка
\t\t\tНоменклатураОбъект.Записать();
\t\t\tСтрокаТовара.ТекущаяНалоговаяГруппа = Объект.НалоговаяГруппа;
\t\t\tСчетчик = Счетчик + 1;
\t\tИсключение
\t\t\tСообщить("Ошибка записи " + СтрокаТовара.Наименование + ": " + ОписаниеОшибки());
\t\tКонецПопытки;
\tКонецЦикла;
\t
\tОбновитьИнфо();
\tСообщить("Установлена налоговая группа для " + Счетчик + " товаров");
\t
КонецПроцедуры

&НаСервере
Процедура ОбновитьИнфо()
\tКоличествоВсего = Объект.Товары.Количество();
\tКоличествоОтмечено = 0;
\tДля Каждого СтрокаТовара Из Объект.Товары Цикл
\t\tЕсли СтрокаТовара.Отметка Тогда
\t\t\tКоличествоОтмечено = КоличествоОтмечено + 1;
\t\tКонецЕсли;
\tКонецЦикла;
\tЭлементы.НадписьИнфо.Заголовок = "Загружено: " + КоличествоВсего + ", отмечено: " + КоличествоОтмечено;
КонецПроцедуры

#КонецОбласти
"""

module_path = os.path.join(DP_DIR, DP_NAME, "Forms", "Форма", "Ext", "Form", "Module.bsl")
write_bom(module_path, module_bsl)

print("\n=== Все 4 новых файла созданы ===")
print(f"DataProcessor UUID: {DP_UUID}")
print(f"Form UUID: {FORM_UUID}")
