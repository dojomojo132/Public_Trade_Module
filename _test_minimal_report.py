# -*- coding: utf-8 -*-
"""Test: minimal report (no form, no objectmodule) to isolate the issue"""
import pathlib
import re

BASE = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка")

# UUID remains from regen
REPORT_UUID = "fe541e03-869c-4899-a712-32a22e4dfab4"
# TypeId/ValueId from regen
OBJ_TYPE_ID = "32aeee7b-cfb2-45d9-889d-4987cd9b2bdd"
OBJ_VALUE_ID = "d1514326-9d5c-42c1-ba77-d3180c478211"
MGR_TYPE_ID = "89922bd2-8af5-4a4b-8b62-5ae3960e3091"
MGR_VALUE_ID = "a18c3c40-85ff-4289-8a17-f2bbf0a5b41c"
FORM_UUID = "81722667-e306-4400-8407-ad097c01c5e1"

# Step 1: Overwrite Report.xml - bare minimum, NO form ref, NO childObjects
report_xml_minimal = f'''<?xml version="1.0" encoding="UTF-8"?>
<MetaDataObject xmlns="http://v8.1c.ru/8.3/MDClasses" xmlns:app="http://v8.1c.ru/8.2/managed-application/core" xmlns:cfg="http://v8.1c.ru/8.1/data/enterprise/current-config" xmlns:cmi="http://v8.1c.ru/8.2/managed-application/cmi" xmlns:ent="http://v8.1c.ru/8.1/data/enterprise" xmlns:lf="http://v8.1c.ru/8.2/managed-application/logform" xmlns:style="http://v8.1c.ru/8.1/data/ui/style" xmlns:sys="http://v8.1c.ru/8.1/data/ui/fonts/system" xmlns:v8="http://v8.1c.ru/8.1/data/core" xmlns:v8ui="http://v8.1c.ru/8.1/data/ui" xmlns:web="http://v8.1c.ru/8.1/data/ui/colors/web" xmlns:win="http://v8.1c.ru/8.1/data/ui/colors/windows" xmlns:xen="http://v8.1c.ru/8.3/xcf/enums" xmlns:xpr="http://v8.1c.ru/8.3/xcf/predef" xmlns:xr="http://v8.1c.ru/8.3/xcf/readable" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="2.20">
\t<Report uuid="{REPORT_UUID}">
\t\t<InternalInfo>
\t\t\t<xr:GeneratedType name="ReportObject.\u0421\u043f\u0440\u0430\u0432\u043e\u0447\u043d\u0438\u043a\u041d\u043e\u043c\u0435\u043d\u043a\u043b\u0430\u0442\u0443\u0440\u044b" category="Object">
\t\t\t\t<xr:TypeId>{OBJ_TYPE_ID}</xr:TypeId>
\t\t\t\t<xr:ValueId>{OBJ_VALUE_ID}</xr:ValueId>
\t\t\t</xr:GeneratedType>
\t\t\t<xr:GeneratedType name="ReportManager.\u0421\u043f\u0440\u0430\u0432\u043e\u0447\u043d\u0438\u043a\u041d\u043e\u043c\u0435\u043d\u043a\u043b\u0430\u0442\u0443\u0440\u044b" category="Manager">
\t\t\t\t<xr:TypeId>{MGR_TYPE_ID}</xr:TypeId>
\t\t\t\t<xr:ValueId>{MGR_VALUE_ID}</xr:ValueId>
\t\t\t</xr:GeneratedType>
\t\t</InternalInfo>
\t\t<Properties>
\t\t\t<Name>\u0421\u043f\u0440\u0430\u0432\u043e\u0447\u043d\u0438\u043a\u041d\u043e\u043c\u0435\u043d\u043a\u043b\u0430\u0442\u0443\u0440\u044b</Name>
\t\t\t<Synonym>
\t\t\t\t<v8:item>
\t\t\t\t\t<v8:lang>ru</v8:lang>
\t\t\t\t\t<v8:content>\u0421\u043f\u0440\u0430\u0432\u043e\u0447\u043d\u0438\u043a \u043d\u043e\u043c\u0435\u043d\u043a\u043b\u0430\u0442\u0443\u0440\u044b</v8:content>
\t\t\t\t</v8:item>
\t\t\t</Synonym>
\t\t\t<UseStandardCommands>true</UseStandardCommands>
\t\t\t<MainDataCompositionSchema/>
\t\t\t<IncludeHelpInContents>false</IncludeHelpInContents>
\t\t</Properties>
\t\t<ChildObjects/>
\t</Report>
</MetaDataObject>
'''

# Step 2: Write minimal report XML
report_path = BASE / "Reports" / "\u0421\u043f\u0440\u0430\u0432\u043e\u0447\u043d\u0438\u043a\u041d\u043e\u043c\u0435\u043d\u043a\u043b\u0430\u0442\u0443\u0440\u044b.xml"
report_path.write_text(report_xml_minimal, encoding='utf-8')
print("Report XML rewritten (minimal, no form)")

# Step 3: Remove form folder and objectmodule from disk
import shutil
form_folder = BASE / "Reports" / "\u0421\u043f\u0440\u0430\u0432\u043e\u0447\u043d\u0438\u043a\u041d\u043e\u043c\u0435\u043d\u043a\u043b\u0430\u0442\u0443\u0440\u044b"
if form_folder.exists():
    shutil.rmtree(form_folder)
    print("Removed report subdirectory (forms, modules)")

# Step 4: Update ConfigDumpInfo - remove ObjectModule, Form entries
cdi_path = BASE / "ConfigDumpInfo.xml"
cdi = cdi_path.read_text(encoding='utf-8')

# Remove ObjectModule nested entry - change parent to self-closing
old_parent = f'''		<Metadata name="Report.\u0421\u043f\u0440\u0430\u0432\u043e\u0447\u043d\u0438\u043a\u041d\u043e\u043c\u0435\u043d\u043a\u043b\u0430\u0442\u0443\u0440\u044b" id="{REPORT_UUID}" configVersion="d3c024c8f475b6e5d9d61d9da0b9603c00000000">
			<Metadata name="Report.\u0421\u043f\u0440\u0430\u0432\u043e\u0447\u043d\u0438\u043a\u041d\u043e\u043c\u0435\u043d\u043a\u043b\u0430\u0442\u0443\u0440\u044b.ObjectModule" id="{REPORT_UUID}.0" configVersion="745a39e3f60c4743f41a2d6052aa912400000000"/>
		</Metadata>'''
new_parent = f'''		<Metadata name="Report.\u0421\u043f\u0440\u0430\u0432\u043e\u0447\u043d\u0438\u043a\u041d\u043e\u043c\u0435\u043d\u043a\u043b\u0430\u0442\u0443\u0440\u044b" id="{REPORT_UUID}" configVersion="d3c024c8f475b6e5d9d61d9da0b9603c00000000"/>'''
cdi = cdi.replace(old_parent, new_parent)

# Remove Form entries
cdi = re.sub(r'\s*<Metadata name="Report\.СправочникНоменклатуры\.Form\.[^/]*/>',  '', cdi)

cdi_path.write_text(cdi, encoding='utf-8')
print("CDI updated (no ObjectModule, no Form)")

print("\nReady to test minimal report deploy!")
