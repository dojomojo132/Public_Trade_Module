# -*- coding: utf-8 -*-
"""Fix form descriptor - remove owner attr, add full Properties"""
import pathlib

FORM_DESCRIPTOR = '''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
\t<Form uuid="b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e">
\t\t<Properties>
\t\t\t<Name>\u0424\u043e\u0440\u043c\u0430\u041e\u0442\u0447\u0435\u0442\u0430</Name>
\t\t\t<Synonym>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>\u0424\u043e\u0440\u043c\u0430 \u043e\u0442\u0447\u0435\u0442\u0430</v8:content>
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
</MetaDataObject>
'''

BASE = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")
COPY = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка")

for base in [BASE, COPY]:
    p = base / "Reports" / "СправочникНоменклатуры" / "Forms" / "ФормаОтчета.xml"
    p.write_text(FORM_DESCRIPTOR, encoding='utf-8')
    print(f"  OK: {base.name}/{p.relative_to(base)}")

print("\nFixed!")
