# -*- coding: utf-8 -*-
"""
Add form attributes ИспользоватьПодключаемоеОборудование and 
ПоддерживаемыеТипыПодключаемогоОборудования to ПриходТовара Form.xml
"""
import pathlib

base_folders = [
    pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка"),
    pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация"),
]

for base in base_folders:
    form_xml = base / "Documents" / "ПриходТовара" / "Forms" / "ФормаДокумента" / "Ext" / "Form.xml"
    if not form_xml.exists():
        print(f"  [SKIP] {form_xml}")
        continue
    
    content = form_xml.read_text(encoding="utf-8")
    
    if "ИспользоватьПодключаемоеОборудование" in content:
        print(f"  [ALREADY] Attribute already exists in {base.name}")
        continue
    
    # Find the </Attributes> closing tag to add new attributes before it
    close_attrs = content.find("</Attributes>")
    if close_attrs < 0:
        print(f"  [ERROR] </Attributes> not found")
        continue
    
    # Find the last existing attribute id to continue numbering
    # Current attributes section - find max id
    import re
    attrs_section = content[:close_attrs]
    ids = [int(m.group(1)) for m in re.finditer(r'<Attribute\s+name="[^"]+"\s+id="(\d+)"', attrs_section)]
    next_id = max(ids) + 1 if ids else 100
    
    # New attributes XML
    new_attrs = f'''
\t\t<Attribute name="ИспользоватьПодключаемоеОборудование" id="{next_id}">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Использовать подключаемое оборудование</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<Type>
\t\t\t\t<v8:Type>xs:boolean</v8:Type>
\t\t\t</Type>
\t\t</Attribute>
\t\t<Attribute name="ПоддерживаемыеТипыПодключаемогоОборудования" id="{next_id + 1}">
\t\t\t<Title>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>Поддерживаемые типы подключаемого оборудования</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Title>
\t\t\t<Type>
\t\t\t\t<v8:Type>xs:string</v8:Type>
\t\t\t\t<v8:StringQualifiers>
\t\t\t\t\t<v8:Length>0</v8:Length>
\t\t\t\t\t<v8:AllowedLength>Variable</v8:AllowedLength>
\t\t\t\t</v8:StringQualifiers>
\t\t\t</Type>
\t\t</Attribute>'''
    
    content = content[:close_attrs] + new_attrs + "\n\t" + content[close_attrs:]
    form_xml.write_text(content, encoding="utf-8")
    print(f"  [OK] Added 2 attributes (ids {next_id}, {next_id+1}) to {base.name}")

print("\nDone!")
