# -*- coding: utf-8 -*-
"""Add ИсходныйШтрихкод parameter + BeforeWriteAtServer event to Номенклатура Form.xml"""
import pathlib

base = pathlib.Path(r"D:\Git\Public_Trade_Module")

folders = [
    base / "Конфигурация" / "Проверка" / "Catalogs" / "Номенклатура" / "Forms" / "ФормаЭлемента" / "Ext" / "Form.xml",
    base / "Конфигурация" / "Catalogs" / "Номенклатура" / "Forms" / "ФормаЭлемента" / "Ext" / "Form.xml",
]

PARAMS_BLOCK = '''\t<Parameters>
\t\t<Parameter name="ИсходныйШтрихкод">
\t\t\t<Type>
\t\t\t\t<v8:Type>xs:string</v8:Type>
\t\t\t\t<v8:StringQualifiers>
\t\t\t\t\t<v8:Length>0</v8:Length>
\t\t\t\t\t<v8:AllowedLength>Variable</v8:AllowedLength>
\t\t\t\t</v8:StringQualifiers>
\t\t\t</Type>
\t\t</Parameter>
\t</Parameters>
'''

BEFORE_WRITE_EVENT = '\t\t<Event name="BeforeWriteAtServer">ПередЗаписьюНаСервере</Event>\n'

for form_xml in folders:
    if not form_xml.exists():
        print(f"  [!] Not found: {form_xml}")
        continue
    
    content = form_xml.read_text(encoding="utf-8")
    changed = False
    
    # 1. Add BeforeWriteAtServer event if missing
    if 'BeforeWriteAtServer' not in content:
        # Insert before </Events>
        content = content.replace(
            '\t</Events>',
            BEFORE_WRITE_EVENT + '\t</Events>'
        )
        changed = True
        print(f"  [+] Added BeforeWriteAtServer event")
    
    # 2. Add Parameters section if missing
    if '<Parameters>' not in content:
        # Insert before </Form>
        content = content.replace(
            '</Form>',
            PARAMS_BLOCK + '</Form>'
        )
        changed = True
        print(f"  [+] Added Parameters section with ИсходныйШтрихкод")
    
    if changed:
        form_xml.write_text(content, encoding="utf-8")
        folder_name = "Проверка" if "Проверка" in str(form_xml) else "Конфигурация"
        print(f"  [OK] Saved: {folder_name}")
    else:
        print(f"  [-] Already up to date")

print("\nDone!")
