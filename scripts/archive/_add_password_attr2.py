# Добавляем атрибут ПарольМобильнойКассы в Пользователи.xml
import pathlib

base = pathlib.Path(r'D:\Git\Public_Trade_Module')
NEW_UUID = "03888042-5fba-4b28-8100-d7f42c6ec362"

pz_path = base / 'Конфигурация' / 'Catalogs' / 'Пользователи.xml'
pz = pz_path.read_text(encoding='utf-8-sig', errors='replace')

# Проверить что атрибут ещё не добавлен
if 'ПарольМобильнойКассы' in pz:
    print('Атрибут уже присутствует в Пользователи.xml')
else:
    # Новый атрибут (3 таба = внутри ChildObjects)
    new_attr = (
        '\t\t\t<Attribute uuid="' + NEW_UUID + '">\n'
        '\t\t\t\t<Properties>\n'
        '\t\t\t\t\t<Name>ПарольМобильнойКассы</Name>\n'
        '\t\t\t\t\t<Synonym>\n'
        '\t\t\t\t\t\t<v8:item>\n'
        '\t\t\t\t\t\t\t<v8:lang>ru</v8:lang>\n'
        '\t\t\t\t\t\t\t<v8:content>Пароль мобильной кассы (хеш)</v8:content>\n'
        '\t\t\t\t\t\t</v8:item>\n'
        '\t\t\t\t\t</Synonym>\n'
        '\t\t\t\t\t<Comment>SHA-256 хеш пароля для авторизации на мобильной кассе</Comment>\n'
        '\t\t\t\t\t<Type>\n'
        '\t\t\t\t\t\t<v8:Type>xs:string</v8:Type>\n'
        '\t\t\t\t\t\t<v8:Length>64</v8:Length>\n'
        '\t\t\t\t\t\t<v8:AllowedLength>Variable</v8:AllowedLength>\n'
        '\t\t\t\t\t</Type>\n'
        '\t\t\t\t\t<PasswordMode>false</PasswordMode>\n'
        '\t\t\t\t\t<Format/>\n'
        '\t\t\t\t\t<EditFormat/>\n'
        '\t\t\t\t\t<ToolTip/>\n'
        '\t\t\t\t\t<MarkNegatives>false</MarkNegatives>\n'
        '\t\t\t\t\t<Mask/>\n'
        '\t\t\t\t\t<MultiLine>false</MultiLine>\n'
        '\t\t\t\t\t<ExtendedEdit>false</ExtendedEdit>\n'
        '\t\t\t\t\t<MinValue xsi:nil="true"/>\n'
        '\t\t\t\t\t<MaxValue xsi:nil="true"/>\n'
        '\t\t\t\t\t<FillFromFillingValue>false</FillFromFillingValue>\n'
        '\t\t\t\t\t<FillValue xsi:nil="true"/>\n'
        '\t\t\t\t\t<FillChecking>DontCheck</FillChecking>\n'
        '\t\t\t\t\t<ChoiceFoldersAndItems>Items</ChoiceFoldersAndItems>\n'
        '\t\t\t\t\t<ChoiceParameterLinks/>\n'
        '\t\t\t\t\t<ChoiceParameters/>\n'
        '\t\t\t\t\t<QuickChoice>Auto</QuickChoice>\n'
        '\t\t\t\t\t<CreateOnInput>Auto</CreateOnInput>\n'
        '\t\t\t\t\t<ChoiceForm/>\n'
        '\t\t\t\t\t<LinkByType/>\n'
        '\t\t\t\t\t<ChoiceHistoryOnInput>Auto</ChoiceHistoryOnInput>\n'
        '\t\t\t\t\t<Use>ForItem</Use>\n'
        '\t\t\t\t\t<Indexing>DontIndex</Indexing>\n'
        '\t\t\t\t\t<FullTextSearch>DontUse</FullTextSearch>\n'
        '\t\t\t\t\t<DataHistory>DontUse</DataHistory>\n'
        '\t\t\t\t</Properties>\n'
        '\t\t\t</Attribute>\n'
    )

    # Вставляем перед \t\t</ChildObjects>
    search = '\t\t</ChildObjects>'
    if search not in pz:
        print(f'ERROR: "{search}" не найдено в файле!')
    else:
        new_pz = pz.replace(search, new_attr + search, 1)
        pz_path.write_text(new_pz, encoding='utf-8-sig', newline='\r\n')
        print(f'OK: атрибут ПарольМобильнойКассы добавлен в Пользователи.xml')
        print(f'UUID: {NEW_UUID}')

# Проверяем CDI
cdi_path = base / 'Конфигурация' / 'ConfigDumpInfo.xml'
cdi = cdi_path.read_text(encoding='utf-8-sig', errors='replace')
if 'ПарольМобильнойКассы' in cdi:
    print('CDI: запись уже есть')
else:
    print('WARNING: CDI был обновлён в предыдущем запуске, но атрибут не найден — проверь вручную')

print()
print('=== Проверка итога ===')
pz_new = pz_path.read_text(encoding='utf-8-sig')
cdi_new = cdi_path.read_text(encoding='utf-8-sig')
print('Пользователи.xml содержит ПарольМобильнойКассы:', 'ПарольМобильнойКассы' in pz_new)
print('ConfigDumpInfo.xml содержит ПарольМобильнойКассы:', 'ПарольМобильнойКассы' in cdi_new)
print('UUID в обоих файлах одинаковый:', NEW_UUID in pz_new and NEW_UUID in cdi_new)
