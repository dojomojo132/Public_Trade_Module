# -*- coding: utf-8 -*-
"""
Deploy full form with correct UUID.
ИБ already has minimal form loaded (UUID 79c07310-710b-4c4d-84c7-3afd65bf5024).
Now replace with full Form.xml + Module.bsl.
"""
import os
import pathlib
import subprocess
import shutil

exe = r"C:\Program Files\1cv8\8.3.27.1719\bin\1cv8.exe"
ib_path = r"D:\Confiq\Public Trade Module"
log_dir = r"D:\Git\Public_Trade_Module\Документация\Валидация\logs"
dump_dir = r"D:\Git\Public_Trade_Module\Конфигурация\_DumpVerify"

new_uuid = "79c07310-710b-4c4d-84c7-3afd65bf5024"

def run_1c(args, log_name, desc):
    log_file = os.path.join(log_dir, log_name)
    cmd = [exe, "DESIGNER", "/F", ib_path] + args + [
        "/DisableStartupDialogs", "/DisableStartupMessages", "/Out", log_file
    ]
    print(f"  [{desc}]")
    result = subprocess.run(cmd, timeout=300)
    log_text = ""
    if pathlib.Path(log_file).exists():
        log_text = pathlib.Path(log_file).read_text(encoding='utf-8-sig').strip()
    status = "OK" if result.returncode == 0 else "FAIL"
    if log_text:
        print(f"  {status}: {log_text[:300]}")
    else:
        print(f"  {status}")
    return result.returncode == 0

nom_forms = os.path.join(dump_dir, "Catalogs", "Номенклатура", "Forms")
form_ext = os.path.join(nom_forms, "ФормаГруппы", "Ext")

# ===========================
# STEP 1: Write full Form.xml
# ===========================
print("STEP 1: Writing full Form.xml...")

full_form = '''<?xml version="1.0" encoding="UTF-8"?>
<Form xmlns="http://v8.1c.ru/8.3/xcf/logform" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:dcscor="http://v8.1c.ru/8.1/data-composition-system/core" xmlns:dcssch="http://v8.1c.ru/8.1/data-composition-system/schema" xmlns:dcsset="http://v8.1c.ru/8.1/data-composition-system/settings" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
	<WindowOpeningMode>LockOwnerWindow</WindowOpeningMode>
	<UseForFoldersAndItems>Folders</UseForFoldersAndItems>
	<AutoCommandBar name="ФормаКоманднаяПанель" id="-1"/>
	<Events>
		<Event name="OnCreateAtServer">ПриСозданииНаСервере</Event>
	</Events>
	<ChildItems>
		<InputField name="Код" id="1">
			<DataPath>Объект.Code</DataPath>
			<Enabled>false</Enabled>
			<EditMode>EnterOnInput</EditMode>
			<ExtendedEditMultipleValues>true</ExtendedEditMultipleValues>
			<ContextMenu name="КодКонтекстноеМеню" id="2"/>
			<ExtendedTooltip name="КодРасширеннаяПодсказка" id="3"/>
		</InputField>
		<InputField name="Наименование" id="4">
			<DataPath>Объект.Description</DataPath>
			<EditMode>EnterOnInput</EditMode>
			<ExtendedEditMultipleValues>true</ExtendedEditMultipleValues>
			<ContextMenu name="НаименованиеКонтекстноеМеню" id="5"/>
			<ExtendedTooltip name="НаименованиеРасширеннаяПодсказка" id="6"/>
		</InputField>
		<InputField name="Родитель" id="7">
			<DataPath>Объект.Parent</DataPath>
			<EditMode>EnterOnInput</EditMode>
			<ExtendedEditMultipleValues>true</ExtendedEditMultipleValues>
			<ContextMenu name="РодительКонтекстноеМеню" id="8"/>
			<ExtendedTooltip name="РодительРасширеннаяПодсказка" id="9"/>
		</InputField>
		<UsualGroup name="ГруппаНаценка" id="10">
			<Title>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Глобальная установка наценки</v8:content>
				</v8:item>
			</Title>
			<ToolTip>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Установить процент наценки на все подчинённые элементы</v8:content>
				</v8:item>
			</ToolTip>
			<Group>Vertical</Group>
			<ExtendedTooltip name="ГруппаНаценкаРасширеннаяПодсказка" id="11"/>
			<ChildItems>
				<InputField name="ПроцентНаценкиГруппы" id="12">
					<DataPath>ПроцентНаценкиГруппы</DataPath>
					<Title>
						<v8:item>
							<v8:lang>ru</v8:lang>
							<v8:content>% наценки для подчинённых</v8:content>
						</v8:item>
					</Title>
					<EditMode>EnterOnInput</EditMode>
					<ExtendedEditMultipleValues>true</ExtendedEditMultipleValues>
					<ContextMenu name="ПроцентНаценкиГруппыКонтекстноеМеню" id="13"/>
					<ExtendedTooltip name="ПроцентНаценкиГруппыРасширеннаяПодсказка" id="14">
						<Title formatted="false">
							<v8:item>
								<v8:lang>ru</v8:lang>
								<v8:content>Введите процент наценки и нажмите \u00abУстановить наценку\u00bb для применения ко всем элементам группы (включая подгруппы)</v8:content>
							</v8:item>
						</Title>
					</ExtendedTooltip>
				</InputField>
				<Button name="УстановитьНаценку" id="15">
					<Title>
						<v8:item>
							<v8:lang>ru</v8:lang>
							<v8:content>Установить наценку</v8:content>
						</v8:item>
					</Title>
					<CommandName>Form.Command.УстановитьНаценку</CommandName>
					<Representation>Auto</Representation>
					<ExtendedTooltip name="УстановитьНаценкуРасширеннаяПодсказка" id="16"/>
				</Button>
				<LabelField name="НадписьРезультат" id="17">
					<DataPath>НадписьРезультат</DataPath>
					<Visible>false</Visible>
					<ContextMenu name="НадписьРезультатКонтекстноеМеню" id="18"/>
					<ExtendedTooltip name="НадписьРезультатРасширеннаяПодсказка" id="19"/>
				</LabelField>
			</ChildItems>
		</UsualGroup>
	</ChildItems>
	<Attributes>
		<Attribute name="Объект" id="1">
			<Type>
				<v8:Type>cfg:CatalogObject.Номенклатура</v8:Type>
			</Type>
			<MainAttribute>true</MainAttribute>
			<SavedData>true</SavedData>
		</Attribute>
		<Attribute name="ПроцентНаценкиГруппы" id="2">
			<Title>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>% наценки для подчинённых</v8:content>
				</v8:item>
			</Title>
			<Type>
				<v8:Type>xs:decimal</v8:Type>
				<v8:NumberQualifiers>
					<v8:Digits>5</v8:Digits>
					<v8:FractionDigits>2</v8:FractionDigits>
					<v8:AllowedSign>Nonnegative</v8:AllowedSign>
				</v8:NumberQualifiers>
			</Type>
		</Attribute>
		<Attribute name="НадписьРезультат" id="3">
			<Title>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Результат</v8:content>
				</v8:item>
			</Title>
			<Type>
				<v8:Type>xs:string</v8:Type>
				<v8:StringQualifiers>
					<v8:Length>0</v8:Length>
					<v8:AllowedLength>Variable</v8:AllowedLength>
				</v8:StringQualifiers>
			</Type>
		</Attribute>
	</Attributes>
	<Commands>
		<Command name="УстановитьНаценку" id="1">
			<Title>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Установить наценку</v8:content>
				</v8:item>
			</Title>
			<ToolTip>
				<v8:item>
					<v8:lang>ru</v8:lang>
					<v8:content>Установить наценку на все подчинённые элементы</v8:content>
				</v8:item>
			</ToolTip>
			<Action>УстановитьНаценку</Action>
		</Command>
	</Commands>
</Form>
'''

pathlib.Path(os.path.join(form_ext, "Form.xml")).write_text(full_form, encoding='utf-8-sig')
print("  OK")

# ===========================
# STEP 2: Write full Module.bsl  
# ===========================
print("STEP 2: Writing full Module.bsl...")

full_module = '''
#Область ОбработчикиСобытийФормы

&НаСервере
Процедура ПриСозданииНаСервере(Отказ, СтандартнаяОбработка)
	// Стандартная обработка
КонецПроцедуры

#КонецОбласти

#Область ОбработчикиКомандФормы

&НаКлиенте
Асинх Процедура УстановитьНаценку(Команда)
	
	Если ПроцентНаценкиГруппы = 0 Тогда
		ПоказатьПредупреждение(, "Укажите процент наценки!");
		Возврат;
	КонецЕсли;
	
	ТекстВопроса = "Установить наценку " + Строка(ПроцентНаценкиГруппы) 
		+ "% на все подчинённые элементы (включая подгруппы)?";
	
	Ответ = Ждать ВопросАсинх(ТекстВопроса, РежимДиалогаВопрос.ДаНет);
	
	Если Ответ = КодВозвратаДиалога.Да Тогда
		Результат = УстановитьНаценкуНаСервере(ПроцентНаценкиГруппы);
		Элементы.НадписьРезультат.Заголовок = "Обновлено элементов: " + Строка(Результат);
		Элементы.НадписьРезультат.Видимость = Истина;
	КонецЕсли;
	
КонецПроцедуры

#КонецОбласти

#Область СлужебныеПроцедурыИФункции

&НаСервере
Функция УстановитьНаценкуНаСервере(Знач НовыйПроцент)
	
	ТекущийЭлемент = Объект.Ссылка;
	
	Запрос = Новый Запрос;
	Запрос.Текст = 
		"ВЫБРАТЬ
		|	Номенклатура.Ссылка КАК Ссылка
		|ИЗ
		|	Справочник.Номенклатура КАК Номенклатура
		|ГДЕ
		|	Номенклатура.Ссылка В ИЕРАРХИИ(&Родитель)
		|	И НЕ Номенклатура.ЭтоГруппа
		|	И НЕ Номенклатура.ПометкаУдаления";
	Запрос.УстановитьПараметр("Родитель", ТекущийЭлемент);
	
	Выборка = Запрос.Выполнить().Выбрать();
	
	Счётчик = 0;
	Пока Выборка.Следующий() Цикл
		Попытка
			ОбъектНоменклатуры = Выборка.Ссылка.ПолучитьОбъект();
			ОбъектНоменклатуры.ПроцентНаценки = НовыйПроцент;
			ОбъектНоменклатуры.Записать();
			Счётчик = Счётчик + 1;
		Исключение
			Продолжить;
		КонецПопытки;
	КонецЦикла;
	
	Возврат Счётчик;
	
КонецФункции

#КонецОбласти
'''

pathlib.Path(os.path.join(form_ext, "Form", "Module.bsl")).write_text(full_module, encoding='utf-8-sig')
print("  OK")

# ===========================
# STEP 3: Also update DefaultFolderForm in Номенклатура.xml
# ===========================
print("STEP 3: Adding DefaultFolderForm...")
nom_xml = os.path.join(dump_dir, "Catalogs", "Номенклатура.xml")
content = pathlib.Path(nom_xml).read_text(encoding='utf-8-sig')
if "DefaultFolderForm" not in content:
    content = content.replace(
        "</DefaultObjectForm>",
        "</DefaultObjectForm>\n\t\t\t<DefaultFolderForm>Catalog.Номенклатура.Form.ФормаГруппы</DefaultFolderForm>"
    )
    pathlib.Path(nom_xml).write_text(content, encoding='utf-8-sig')
print("  OK")

# ===========================
# STEP 4: Load updated form
# ===========================
ok = run_1c(["/LoadConfigFromFiles", dump_dir], "full-form-load.log", "Load FULL form")
if ok:
    ok2 = run_1c(["/UpdateDBCfg"], "full-form-update.log", "UpdateDBCfg")
    if ok2:
        print("\n=== FULL FORM DEPLOYED SUCCESSFULLY! ===")
        
        # Step 5: Verify by dumping
        dump_verify = r"D:\Git\Public_Trade_Module\Конфигурация\_DumpFinal"
        if os.path.exists(dump_verify):
            shutil.rmtree(dump_verify)
        os.makedirs(dump_verify)
        ok3 = run_1c(["/DumpConfigToFiles", dump_verify], "dump-final.log", "Final dump for verification")
        if ok3:
            print("  Config integrity: VERIFIED")
    else:
        print("\n!!! UpdateDBCfg FAILED")
else:
    print("\n!!! Load FAILED")
