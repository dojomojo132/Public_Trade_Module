#!/usr/bin/env python3
"""Создаёт недостающие файлы-дескрипторы шаблонов для мигрированных отчётов."""
import uuid
from pathlib import Path

BOM = b"\xef\xbb\xbf"
EXT = Path(r"D:\Git\Public_Trade_Module\Конфигурация_PTM_Analytics")

NS = (
    'xmlns="http://v8.1c.ru/8.3/MDClasses" '
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
    'version="2.20"'
)

REPORTS = [
    "Анл_Возвраты",
    "Анл_ВаловаяПрибыль",
    "Анл_ПродажиПоСчетам",
    "Анл_ДвижениеДенежныхСредств",
    "Анл_ПродажиЗаСмену",
    "Анл_ДвижениеТоваров",
]

for name in REPORTS:
    t_uuid = str(uuid.uuid4())
    content = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f"<MetaDataObject {NS}>\n"
        f'\t<Template uuid="{t_uuid}">\n'
        f"\t\t<Properties>\n"
        f"\t\t\t<Name>ОсновнаяСхемаКомпоновкиДанных</Name>\n"
        f"\t\t\t<Synonym>\n"
        f"\t\t\t\t<v8:item>\n"
        f"\t\t\t\t\t<v8:lang>ru</v8:lang>\n"
        f"\t\t\t\t\t<v8:content>Основная схема компоновки данных</v8:content>\n"
        f"\t\t\t\t</v8:item>\n"
        f"\t\t\t</Synonym>\n"
        f"\t\t\t<Comment/>\n"
        f"\t\t\t<TemplateType>DataCompositionSchema</TemplateType>\n"
        f"\t\t</Properties>\n"
        f"\t</Template>\n"
        f"</MetaDataObject>"
    )
    path = EXT / "Reports" / name / "Templates" / "ОсновнаяСхемаКомпоновкиДанных.xml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(BOM + content.encode("utf-8"))
    print(f"  ✓ {name} (uuid={t_uuid})")

print("\nГотово! Дескрипторы шаблонов созданы.")
