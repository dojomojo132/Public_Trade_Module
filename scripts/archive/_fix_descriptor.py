# -*- coding: utf-8 -*-
import pathlib

BOM = b'\xef\xbb\xbf'

content = '''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
\t<Form uuid="269056ab-f467-4c3f-884e-5c95ef7fbba7">
\t\t<Properties>
\t\t\t<Name>\u0424\u043e\u0440\u043c\u0430\u0412\u044b\u0431\u043e\u0440\u0430</Name>
\t\t\t<Synonym>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>\u0424\u043e\u0440\u043c\u0430 \u0432\u044b\u0431\u043e\u0440\u0430</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Synonym>
\t\t\t<Comment/>
\t\t\t<FormType>Managed</FormType>
\t\t\t<IncludeHelpInContents>false</IncludeHelpInContents>
\t\t\t<UsePurposes>
\t\t\t\t<v8:Value xsi:type="app:ApplicationUsePurpose">PlatformApplication</v8:Value>
\t\t\t\t<v8:Value xsi:type="app:ApplicationUsePurpose">MobilePlatformApplication</v8:Value>
\t\t\t</UsePurposes>
\t\t</Properties>
\t</Form>
</MetaDataObject>
'''

files = [
    pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\Catalogs\Контрагенты\Forms\ФормаВыбора.xml"),
    pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Catalogs\Контрагенты\Forms\ФормаВыбора.xml"),
]

for f in files:
    data = BOM + content.encode('utf-8')
    f.write_bytes(data)
    print(f"  OK {f}")

print("Done!")
