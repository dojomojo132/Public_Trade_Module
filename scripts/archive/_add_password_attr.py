# Добавляем атрибут ПарольМобильнойКассы в Пользователи.xml и CDI
import pathlib

base = pathlib.Path(r'D:\Git\Public_Trade_Module')
NEW_UUID = "03888042-5fba-4b28-8100-d7f42c6ec362"

# ==========================================
# 1. Редактируем Пользователи.xml
# ==========================================
pz_path = base / 'Конфигурация' / 'Catalogs' / 'Пользователи.xml'
pz = pz_path.read_text(encoding='utf-8-sig', errors='replace')

# Тег </ChildObjects> внутри каталога Пользователи
# Мы вставляем новый атрибут перед этой строкой
search_str = '\t\t\t</ChildObjects>'
new_attr = f'''\t\t\t<Attribute uuid="{NEW_UUID}">
\t\t\t\t<Properties>
\t\t\t\t\t<Name>ПарольМобильнойКассы</Name>
\t\t\t\t\t<Synonym>
\t\t\t\t\t\t<v8:item>
\t\t\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t\t\t<v8:content>Пароль мобильной кассы (хеш)</v8:content>
\t\t\t\t\t\t</v8:item>
\t\t\t\t\t</Synonym>
\t\t\t\t\t<Comment>SHA-256 хеш пароля для авторизации на мобильной кассе</Comment>
\t\t\t\t\t<Type>
\t\t\t\t\t\t<v8:Type>xs:string</v8:Type>
\t\t\t\t\t\t<v8:Length>64</v8:Length>
\t\t\t\t\t\t<v8:AllowedLength>Variable</v8:AllowedLength>
\t\t\t\t\t</Type>
\t\t\t\t\t<PasswordMode>false</PasswordMode>
\t\t\t\t\t<Format/>
\t\t\t\t\t<EditFormat/>
\t\t\t\t\t<ToolTip/>
\t\t\t\t\t<MarkNegatives>false</MarkNegatives>
\t\t\t\t\t<Mask/>
\t\t\t\t\t<MultiLine>false</MultiLine>
\t\t\t\t\t<ExtendedEdit>false</ExtendedEdit>
\t\t\t\t\t<MinValue xsi:nil="true"/>
\t\t\t\t\t<MaxValue xsi:nil="true"/>
\t\t\t\t\t<FillFromFillingValue>false</FillFromFillingValue>
\t\t\t\t\t<FillValue xsi:nil="true"/>
\t\t\t\t\t<FillChecking>DontCheck</FillChecking>
\t\t\t\t\t<ChoiceFoldersAndItems>Items</ChoiceFoldersAndItems>
\t\t\t\t\t<ChoiceParameterLinks/>
\t\t\t\t\t<ChoiceParameters/>
\t\t\t\t\t<QuickChoice>Auto</QuickChoice>
\t\t\t\t\t<CreateOnInput>Auto</CreateOnInput>
\t\t\t\t\t<ChoiceForm/>
\t\t\t\t\t<LinkByType/>
\t\t\t\t\t<ChoiceHistoryOnInput>Auto</ChoiceHistoryOnInput>
\t\t\t\t\t<Use>ForItem</Use>
\t\t\t\t\t<Indexing>DontIndex</Indexing>
\t\t\t\t\t<FullTextSearch>DontUse</FullTextSearch>
\t\t\t\t\t<DataHistory>DontUse</DataHistory>
\t\t\t\t</Properties>
\t\t\t</Attribute>
'''

if search_str not in pz:
    print('ОШИБКА: строка</ChildObjects> не найдена в Пользователи.xml')
    print('Поиск альтернативы...')
    # Попробуем с пробелами
    for s in ['</ChildObjects>', '\t\t</ChildObjects>', '        </ChildObjects>', '                </ChildObjects>']:
        if s in pz:
            print(f'Найдено: {repr(s)}')
            break
else:
    new_pz = pz.replace(search_str, new_attr + search_str, 1)
    pz_path.write_text(new_pz, encoding='utf-8-sig', newline='\r\n')
    print(f'OK: атрибут добавлен в Пользователи.xml (UUID={NEW_UUID})')

# ==========================================
# 2. Редактируем ConfigDumpInfo.xml
# ==========================================
cdi_path = base / 'Конфигурация' / 'ConfigDumpInfo.xml'
cdi = cdi_path.read_text(encoding='utf-8-sig', errors='replace')

cdi_search = '\t\t\t<Metadata name="Catalog.Пользователи.Attribute.ИдентификаторПользователяИБ" id="d7e554b5-8c1f-4df2-a27c-0c0e98771b71"/>\n\t\t</Metadata>'
cdi_replace = f'\t\t\t<Metadata name="Catalog.Пользователи.Attribute.ИдентификаторПользователяИБ" id="d7e554b5-8c1f-4df2-a27c-0c0e98771b71"/>\n\t\t\t<Metadata name="Catalog.Пользователи.Attribute.ПарольМобильнойКассы" id="{NEW_UUID}"/>\n\t\t</Metadata>'

if cdi_search not in cdi:
    print('ОШИБКА: блок Пользователи не найден в CDI для вставки')
    # Показываем что есть
    idx = cdi.find('Catalog.Пользователи.Attribute.ИдентификаторПользователяИБ')
    if idx >= 0:
        print('Контекст вокруг ИдентификаторПользователяИБ:')
        print(repr(cdi[idx:idx+300]))
else:
    new_cdi = cdi.replace(cdi_search, cdi_replace, 1)
    cdi_path.write_text(new_cdi, encoding='utf-8-sig', newline='\r\n')
    print(f'OK: запись добавлена в ConfigDumpInfo.xml')

print('Готово!')
