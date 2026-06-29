import os
import re
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# ==========================================
# ⚙️ НАСТРОЙКИ (Загружаются из config.json)
# ==========================================
CONFIG_FILE = Path("config.json")

def load_config():
    if not CONFIG_FILE.exists():
        default_config = {
            "obsidian_vault_path": "C:\\Users\\User\\Documents\\Obsidian\\Мой Vault\\PTM_Project",
            "project_paths": {
                "Основная": "C:\\Projects\\PTM_Source\\MainConfig"
            }
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        print(f"⚠️ Файл {CONFIG_FILE} не найден. Я создал шаблон.")
        exit()
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()
OBSIDIAN_VAULT = Path(config["obsidian_vault_path"])
INDEX_FOLDER = config.get("obsidian_index_folder", "99-Meta/1C-Index")
INDEX_ROOT = OBSIDIAN_VAULT / INDEX_FOLDER
INDEX_PREFIX = INDEX_FOLDER.replace("\\", "/")
PROJECT_PATHS = {name: Path(path) for name, path in config["project_paths"].items()}

# Папки 1С, которые мы анализируем (английские имена папок из XML выгрузки)
TARGET_TYPES = {
    "Subsystems": "Подсистемы",
    "CommonModules": "ОбщиеМодули",
    "SessionParameters": "ПараметрыСеанса",
    "Roles": "Роли",
    "EventSubscriptions": "ПодпискиНаСобытия",
    "ScheduledJobs": "РегламентныеЗадания",
    "Constants": "Константы",
    "Catalogs": "Справочники",
    "Documents": "Документы",
    "DocumentJournals": "ЖурналыДокументов",
    "Enums": "Перечисления",
    "Reports": "Отчеты",
    "DataProcessors": "Обработки",
    "ChartsOfCharacteristicTypes": "ПланыВидовХарактеристик",
    "ChartsOfAccounts": "ПланыСчетов",
    "ChartsOfCalculationTypes": "ПланыВидовРасчета",
    "InformationRegisters": "РегистрыСведений",
    "AccumulationRegisters": "РегистрыНакопления",
    "AccountingRegisters": "РегистрыБухгалтерии",
    "CalculationRegisters": "РегистрыРасчета",
    "BusinessProcesses": "БизнесПроцессы",
    "Tasks": "Задачи",
    "ExchangePlans": "ПланыОбмена",
    "HTTPServices": "HTTPСервисы",
}

# Префиксы для создания красивых ссылок и файлов (Справочники -> Справочник)
PREFIX_MAP = {
    "Подсистемы": "Подсистема",
    "ОбщиеМодули": "ОбщийМодуль",
    "ПараметрыСеанса": "ПараметрСеанса",
    "Роли": "Роль",
    "ПодпискиНаСобытия": "ПодпискаНаСобытие",
    "РегламентныеЗадания": "РегламентноеЗадание",
    "Константы": "Константа",
    "Справочники": "Справочник",
    "Документы": "Документ",
    "ЖурналыДокументов": "ЖурналДокументов",
    "Перечисления": "Перечисление",
    "Отчеты": "Отчет",
    "Обработки": "Обработка",
    "ПланыВидовХарактеристик": "ПланВидовХарактеристик",
    "ПланыСчетов": "ПланСчетов",
    "ПланыВидовРасчета": "ПланВидовРасчета",
    "РегистрыСведений": "РегистрСведений",
    "РегистрыНакопления": "РегистрНакопления",
    "РегистрыБухгалтерии": "РегистрБухгалтерии",
    "РегистрыРасчета": "РегистрРасчета",
    "БизнесПроцессы": "БизнесПроцесс",
    "Задачи": "Задача",
    "ПланыОбмена": "ПланОбмена",
    "HTTPСервисы": "HTTPСервис",
}

REGISTER_EN_PREFIXES = {
    "InformationRegister": "РегистрСведений",
    "AccumulationRegister": "РегистрНакопления",
    "AccountingRegister": "РегистрБухгалтерии",
    "CalculationRegister": "РегистрРасчета",
}

METADATA_HANDLER_KINDS = {
    "ОбработкаПроведения": "posting",
    "ОбработкаУдаленияПроведения": "unposting",
    "ПередЗаписью": "before_write",
    "ПриЗаписи": "on_write",
    "ОбработкаЗаполнения": "filling",
    "ОбработкаПроверкиЗаполнения": "check_filling",
}


# ==========================================
# 🛠 БАЗОВЫЕ ФУНКЦИИ
# ==========================================
def read_1c_file(file_path: Path) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            return f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='windows-1251') as f:
            return f.read()

def parse_metadata(xml_content: str):
    name_match = re.search(r'<Name>([А-Яа-яЁёA-Za-z0-9_]+)</Name>', xml_content)
    synonym_match = re.search(r'<Synonym>.*?<.*?content>(.*?)</.*?content>.*?</Synonym>', xml_content, re.DOTALL)
    comment_match = re.search(r'<Comment>(.*?)</Comment>', xml_content, re.DOTALL)
    
    # НОВОЕ: Ищем все структурные ссылки на другие объекты (реквизиты, ТЧ, измерения)
    # Ищем паттерны вида cfg:CatalogRef.ИмяОбъекта или cfg:DocumentRef.ИмяОбъекта
    xml_links = set(re.findall(r'cfg:\w+\.([А-Яа-яЁёA-Za-z0-9_]+)', xml_content))

    return {
        "name": name_match.group(1) if name_match else "Неизвестно",
        "synonym": synonym_match.group(1) if synonym_match else "",
        "comment": comment_match.group(1) if comment_match else "",
        "xml_links": xml_links, # Сохраняем найденные реквизиты
        "structure": parse_structure(xml_content)
    }


# ---- Парсинг внутренней структуры объекта (реквизиты, ТЧ, измерения, ресурсы) ----

# Маппинг XML-типов 1С → компактные русские обозначения
_TYPE_NORMALIZE = {
    "String": "Строка",
    "Number": "Число",
    "Boolean": "Булево",
    "Date": "Дата",
    "UUID": "УникальныйИдентификатор",
    "ValueStorage": "ХранилищеЗначения"
}

_CFG_PREFIX_MAP = {
    "DocumentRef": "ДокументСсылка",
    "CatalogRef": "СправочникСсылка",
    "EnumRef": "ПеречислениеСсылка",
    "ChartOfCharacteristicTypesRef": "ПланВидовХарактеристикСсылка",
    "ChartOfAccountsRef": "ПланСчетовСсылка",
    "BusinessProcessRef": "БизнесПроцессСсылка",
    "TaskRef": "ЗадачаСсылка",
    "InformationRegisterRecordKey": "РегистрСведенийКлючЗаписи",
    "AccumulationRegisterRecordKey": "РегистрНакопленияКлючЗаписи"
}

# Суффиксы ссылочных типов 1С → префикс object_id (как в PREFIX_MAP)
_REF_SUFFIXES = ("Ссылка", "КлючЗаписи", "Объект", "СписокОбъектов", "Менеджер")


def extract_object_ids_from_type(type_str: str) -> set[str]:
    """Из строки типа вида 'СправочникСсылка.Оборудование|Число' вернёт {'Справочник.Оборудование'}.

    Поддерживает любой суффикс из _REF_SUFFIXES. Используется для построения
    графовых связей по типам реквизитов/ТЧ/измерений/ресурсов.
    """
    if not type_str:
        return set()
    result: set[str] = set()
    for part in type_str.split("|"):
        part = part.strip()
        if "." not in part:
            continue
        kind, name = part.split(".", 1)
        for suffix in _REF_SUFFIXES:
            if kind.endswith(suffix) and len(kind) > len(suffix):
                prefix = kind[: -len(suffix)]
                result.add(f"{prefix}.{name}")
                break
    return result


def _compact_type(xml_type_block: str) -> str:
    """Из <Type><v8:Type>...</v8:Type>...</Type> делает компактную строку через '|'."""
    if not xml_type_block:
        return ""
    types = re.findall(r'<v8:Type>([^<]+)</v8:Type>', xml_type_block)
    parts = []
    for raw in types:
        if raw.startswith("v8:") or raw.startswith("xs:"):
            simple = raw.split(":", 1)[1]
            parts.append(_TYPE_NORMALIZE.get(simple, simple))
        elif raw.startswith("cfg:"):
            body = raw[4:]
            if "." in body:
                kind, obj_name = body.split(".", 1)
                kind_ru = _CFG_PREFIX_MAP.get(kind, kind)
                parts.append(f"{kind_ru}.{obj_name}")
            else:
                parts.append(body)
        else:
            parts.append(raw)
    return "|".join(parts) if parts else ""


_BLOCK_PATTERN = re.compile(
    r'<(?P<tag>Attribute|TabularSection|Dimension|Resource|EnumValue)\s[^>]*>(?P<body>.*?)</(?P=tag)>',
    re.DOTALL
)


def _parse_block_field(body: str) -> dict:
    name = re.search(r'<Name>([^<]+)</Name>', body)
    synonym = re.search(r'<Synonym>.*?<v8:content>([^<]*)</v8:content>', body, re.DOTALL)
    type_block = re.search(r'<Type>(.*?)</Type>', body, re.DOTALL)
    return {
        "name": name.group(1) if name else "",
        "synonym": synonym.group(1) if synonym else "",
        "type": _compact_type(type_block.group(1)) if type_block else ""
    }


def parse_structure(xml_content: str) -> dict:
    """Извлекает реквизиты, ТЧ (с реквизитами), измерения, ресурсы, значения перечислений."""
    structure: dict = {
        "attributes": [],
        "tabular_sections": [],
        "dimensions": [],
        "resources": [],
        "enum_values": []
    }

    # Идём по верхнеуровневым блокам. Для ТЧ дополнительно парсим вложенные Attribute.
    for match in _BLOCK_PATTERN.finditer(xml_content):
        tag = match.group("tag")
        body = match.group("body")
        # Берём только Properties-блок (вложенные Attribute внутри ТЧ обработаем отдельно)
        props_match = re.search(r'<Properties>(.*?)</Properties>', body, re.DOTALL)
        props = props_match.group(1) if props_match else body
        field = _parse_block_field(props)
        if not field["name"]:
            continue

        if tag == "Attribute":
            # Может быть либо реквизит документа/справочника, либо реквизит ТЧ.
            # Реквизиты ТЧ обработаются ниже внутри своих контейнеров и удаляются дубликаты.
            structure["attributes"].append(field)
        elif tag == "Dimension":
            structure["dimensions"].append(field)
        elif tag == "Resource":
            structure["resources"].append(field)
        elif tag == "EnumValue":
            structure["enum_values"].append({"name": field["name"], "synonym": field["synonym"]})
        elif tag == "TabularSection":
            ts_attrs = []
            for inner in re.finditer(
                r'<Attribute\s[^>]*>(.*?)</Attribute>', body, re.DOTALL
            ):
                inner_body = inner.group(1)
                inner_props = re.search(r'<Properties>(.*?)</Properties>', inner_body, re.DOTALL)
                ts_attrs.append(_parse_block_field(
                    inner_props.group(1) if inner_props else inner_body))
            structure["tabular_sections"].append({
                "name": field["name"],
                "synonym": field["synonym"],
                "attributes": [a for a in ts_attrs if a["name"]]
            })

    # Удаляем из верхнеуровневых attributes те, что на самом деле принадлежат ТЧ
    ts_attr_names = {
        attr["name"]
        for ts in structure["tabular_sections"]
        for attr in ts["attributes"]
    }
    if ts_attr_names:
        structure["attributes"] = [
            a for a in structure["attributes"] if a["name"] not in ts_attr_names
        ]

    # Регистраторы (для документов): <RegisterRecords><xr:Item>InformationRegister.X</xr:Item>...</RegisterRecords>
    rr_match = re.search(r'<RegisterRecords>(.+?)</RegisterRecords>', xml_content, re.DOTALL)
    if rr_match:
        rr_body = rr_match.group(1)
        registers = []
        # type_to_prefix должен совпадать с build_subsystems_index
        type_to_prefix_local = {
            "InformationRegister": "РегистрСведений",
            "AccumulationRegister": "РегистрНакопления",
            "AccountingRegister": "РегистрБухгалтерии",
            "CalculationRegister": "РегистрРасчета",
        }
        for en_type, ru_name in re.findall(
            r'<xr:Item[^>]*>([A-Za-z]+)\.([А-Яа-яЁёA-Za-z0-9_]+)</xr:Item>', rr_body
        ):
            prefix = type_to_prefix_local.get(en_type, en_type)
            registers.append(f"{prefix}.{ru_name}")
        if registers:
            structure["register_records"] = registers

    # Чистим пустые секции для компактности
    return {key: value for key, value in structure.items() if value}


def parse_predefined_file(predefined_path: Path, catalog_name: str) -> list[dict]:
    """Парсит Ext/Predefined.xml справочника (или ПВХ)."""
    if not predefined_path or not predefined_path.exists():
        return []
    try:
        content = read_1c_file(predefined_path)
    except Exception:
        return []

    items: list[dict] = []
    for block in re.finditer(r"<Item\b[^>]*>(.*?)</Item>", content, re.DOTALL):
        body = block.group(1)
        name_m = re.search(r"<Name>([^<]+)</Name>", body)
        if not name_m:
            continue
        name = name_m.group(1).strip()
        code_m = re.search(r"<Code>([^<]*)</Code>", body)
        desc_m = re.search(r"<Description>([^<]*)</Description>", body)
        folder_m = re.search(r"<IsFolder>([^<]*)</IsFolder>", body)
        items.append({
            "name": name,
            "code": code_m.group(1).strip() if code_m else "",
            "description": desc_m.group(1).strip() if desc_m else "",
            "is_folder": (folder_m.group(1).strip().lower() == "true") if folder_m else False,
            "bsl_access": f"Справочники.{catalog_name}.{name}",
        })
    return items


def parse_common_module_flags(xml_content: str) -> dict:
    """Свойства общего модуля: Server, Client, Global и т.д."""
    flags: dict[str, bool] = {}
    for key in (
        "Global", "Server", "ClientManagedApplication", "ClientOrdinaryApplication",
        "ServerCall", "Privileged", "ExternalConnection",
    ):
        match = re.search(rf"<{key}>(true|false)</{key}>", xml_content, re.IGNORECASE)
        if match:
            flags[key] = match.group(1).lower() == "true"
    return flags


def parse_http_service_structure(xml_content: str) -> dict:
    """RootURL и HTTP-методы из XML HTTP-сервиса."""
    structure: dict = {}
    root = re.search(r"<RootURL>([^<]+)</RootURL>", xml_content)
    if root:
        structure["root_url"] = root.group(1).strip()

    endpoints: list[dict] = []
    for tpl_match in re.finditer(r"<URLTemplate\s[^>]*>(.*?)</URLTemplate>", xml_content, re.DOTALL):
        tpl_body = tpl_match.group(1)
        template = re.search(r"<Template>([^<]+)</Template>", tpl_body)
        for method_match in re.finditer(r"<Method\s[^>]*>(.*?)</Method>", tpl_body, re.DOTALL):
            mb = method_match.group(1)
            method_name = re.search(r"<Name>([^<]+)</Name>", mb)
            http_method = re.search(r"<HTTPMethod>([^<]+)</HTTPMethod>", mb)
            handler = re.search(r"<Handler>([^<]+)</Handler>", mb)
            endpoints.append({
                "template": template.group(1).strip() if template else "",
                "method_name": method_name.group(1).strip() if method_name else "",
                "http_method": http_method.group(1).strip() if http_method else "",
                "handler": handler.group(1).strip() if handler else "",
            })
    if endpoints:
        structure["http_endpoints"] = endpoints
    return structure


def attach_predefined_to_structure(object_folder: Path | None, meta: dict) -> None:
    """Добавляет predefined_items в structure, если есть Ext/Predefined.xml."""
    if not object_folder:
        return
    predefined_path = object_folder / "Ext" / "Predefined.xml"
    catalog_name = meta.get("name")
    if not catalog_name:
        return
    items = parse_predefined_file(predefined_path, catalog_name)
    if items:
        meta.setdefault("structure", {})["predefined_items"] = items


# ---- Сканирование подпапок объекта: формы, макеты, команды ----

def scan_object_subitems(object_folder) -> dict:
    """Сканирует подпапки Forms/Templates/Commands объекта на диске.
    Возвращает {"forms": [...], "templates": [...], "commands": [...]}.
    Каждый элемент: {"name": str, "synonym": str, "comment": str}."""
    result = {"forms": [], "templates": [], "commands": []}
    if not object_folder or not Path(object_folder).exists():
        return result

    folder_to_key = {"Forms": "forms", "Templates": "templates", "Commands": "commands"}
    for sub_name, key in folder_to_key.items():
        sub_path = Path(object_folder) / sub_name
        if not sub_path.exists():
            continue
        # XML-файлы прямо в папке (Forms/ФормаДокумента.xml)
        for xml_file in sorted(sub_path.glob("*.xml")):
            try:
                content = read_1c_file(xml_file)
            except Exception:
                continue
            name_match = re.search(r'<Name>([А-Яа-яЁёA-Za-z0-9_]+)</Name>', content)
            synonym_match = re.search(
                r'<Synonym>.*?<v8:content>([^<]*)</v8:content>', content, re.DOTALL)
            comment_match = re.search(r'<Comment>([^<]*)</Comment>', content)
            name = name_match.group(1) if name_match else xml_file.stem
            entry = {
                "name": name,
                "synonym": synonym_match.group(1) if synonym_match else "",
                "comment": comment_match.group(1).strip() if comment_match else ""
            }
            if key == "templates":
                skd_path = sub_path / xml_file.stem / "Ext" / "Template.xml"
                if skd_path.exists():
                    try:
                        skd_content = read_1c_file(skd_path)
                        queries = re.findall(
                            r"<query>(.*?)</query>", skd_content, re.DOTALL | re.IGNORECASE
                        )
                        if queries:
                            entry["skd_queries"] = [q.strip() for q in queries if q.strip()]
                    except Exception:
                        pass
            # Для форм добавим тип формы (Document/List/Choice/...)
            if key == "forms":
                form_type_match = re.search(r'<FormType>([^<]+)</FormType>', content)
                if form_type_match:
                    entry["form_type"] = form_type_match.group(1)
                # Внутренности формы: реквизиты формы, команды, контролы с DataPath
                form_xml_path = sub_path / xml_file.stem / "Ext" / "Form.xml"
                internals = parse_form_internals(form_xml_path)
                if internals:
                    entry["internals"] = internals
            result[key].append({k: v for k, v in entry.items() if v})

    return {k: v for k, v in result.items() if v}


# ---- Подсистемы: индекс object_id → [имена подсистем] ----

def build_subsystems_index(project_paths: dict) -> dict:
    """Сканирует Subsystems/*.xml во всех проектах.
    Возвращает {object_id: [имя_подсистемы, ...]}."""
    index: dict[str, list[str]] = defaultdict(list)
    type_to_prefix = {
        "Document": "Документ",
        "Catalog": "Справочник",
        "Enum": "Перечисление",
        "Report": "Отчет",
        "DataProcessor": "Обработка",
        "InformationRegister": "РегистрСведений",
        "AccumulationRegister": "РегистрНакопления",
        "DocumentJournal": "ЖурналДокументов",
        "ChartOfCharacteristicTypes": "ПланВидовХарактеристик",
        "ChartOfAccounts": "ПланСчетов",
        "BusinessProcess": "БизнесПроцесс",
        "Task": "Задача",
        "CommonModule": "ОбщийМодуль",
        "Constant": "Константа",
        "ExchangePlan": "ПланОбмена",
    }
    item_pattern = re.compile(r'<xr:Item[^>]*>([A-Za-z]+)\.([А-Яа-яЁёA-Za-z0-9_]+)</xr:Item>')
    name_pattern = re.compile(r'<Name>([А-Яа-яЁёA-Za-z0-9_]+)</Name>')

    for project_name, source_dir in project_paths.items():
        sub_dir = Path(source_dir) / "Subsystems"
        if not sub_dir.exists():
            continue
        for xml_file in sorted(sub_dir.glob("*.xml")):
            try:
                content = read_1c_file(xml_file)
            except Exception:
                continue
            name_match = name_pattern.search(content)
            if not name_match:
                continue
            subsystem_name = name_match.group(1)
            for en_type, ru_name in item_pattern.findall(content):
                prefix = type_to_prefix.get(en_type)
                if not prefix:
                    continue
                obj_id = f"{prefix}.{ru_name}"
                if subsystem_name not in index[obj_id]:
                    index[obj_id].append(subsystem_name)

    return dict(index)


# ---- Парсер сигнатур процедур/функций BSL ----

_BSL_SIGNATURE_PATTERN = re.compile(
    r'(?im)^\s*(?:&[A-Za-zА-Яа-яЁё]+\s+)?'                       # директива компиляции (опц.)
    r'(Процедура|Функция|Procedure|Function)\s+'                 # тип
    r'([A-Za-zА-Яа-яЁё][A-Za-zА-Яа-яЁё0-9_]*)\s*'                # имя
    r'\(([^)]*)\)\s*'                                            # параметры
    r'(Экспорт|Export)?'                                         # экспорт
)


def parse_bsl_signatures(bsl_path: Path, max_sigs: int = 60) -> list[dict]:
    """Извлекает сигнатуры процедур/функций модуля.
    Возвращает [{kind: 'Процедура'|'Функция', name, params, exported: bool}]."""
    if not bsl_path or not Path(bsl_path).exists():
        return []
    try:
        text = Path(bsl_path).read_text(encoding='utf-8-sig', errors='ignore')
    except Exception:
        return []

    result: list[dict] = []
    for match in _BSL_SIGNATURE_PATTERN.finditer(text):
        kind, name, params, export = match.groups()
        # Нормализуем kind к русскому
        kind_ru = "Процедура" if kind in ("Процедура", "Procedure") else "Функция"
        # Параметры: убираем многострочность, лишние пробелы
        params_clean = re.sub(r'\s+', ' ', params).strip()
        entry = {
            "kind": kind_ru,
            "name": name,
            "params": params_clean,
            "exported": bool(export),
        }
        handler_kind = METADATA_HANDLER_KINDS.get(name)
        if handler_kind:
            entry["handler"] = True
            entry["handler_kind"] = handler_kind
        result.append(entry)
        if len(result) >= max_sigs:
            break
    return result


# ---- Парсер внутренностей форм (Form.xml) ----

# Контролы формы с биндингом: name + DataPath
_FORM_CONTROL_TAGS = (
    "InputField", "RadioButtonField", "CheckBoxField", "LabelField",
    "PictureField", "TextDocumentField", "SpreadsheetDocumentField",
    "CalendarField", "PlannerField", "ChartField", "GanttChartField",
    "DendrogramField", "FormattedDocumentField", "ProgressBarField",
    "TrackBarField", "Table", "Page", "Pages", "UsualGroup", "ColumnGroup",
    "ContextMenu", "Button"
)
_FORM_CONTROL_PATTERN = re.compile(
    r'<(' + '|'.join(_FORM_CONTROL_TAGS) + r')\s+name="([^"]+)"[^>]*>(.*?)</\1>',
    re.DOTALL
)
_DATA_PATH_PATTERN = re.compile(r'<DataPath>([^<]+)</DataPath>')


def parse_form_internals(form_xml_path: Path) -> dict:
    """Парсит Form.xml: реквизиты формы (Attributes), команды (Commands), элементы с DataPath.
    Возвращает {"controls": [{name, type, data_path}], "commands": [name], "attributes": [name]}.
    Контролы без DataPath (декоративные группы, тултипы) не включаем."""
    if not form_xml_path or not Path(form_xml_path).exists():
        return {}
    try:
        text = Path(form_xml_path).read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return {}

    result: dict = {"controls": [], "commands": [], "attributes": []}

    # Реквизиты формы: <Attributes name="X">...<MainAttribute>true</MainAttribute>?</Attributes>
    for m in re.finditer(r'<Attributes\s+(?:[^>]*\s)?name="([^"]+)"', text):
        result["attributes"].append(m.group(1))

    # Команды формы: <Commands name="X">
    for m in re.finditer(r'<Commands\s+(?:[^>]*\s)?name="([^"]+)"', text):
        result["commands"].append(m.group(1))

    # Контролы с DataPath
    seen = set()
    for control_match in _FORM_CONTROL_PATTERN.finditer(text):
        tag = control_match.group(1)
        name = control_match.group(2)
        body = control_match.group(3)
        if name in seen:
            continue
        # Берём только первый DataPath на уровне (не из вложенных)
        dp_match = _DATA_PATH_PATTERN.search(body)
        if not dp_match:
            continue
        seen.add(name)
        result["controls"].append({
            "name": name,
            "type": tag,
            "data_path": dp_match.group(1)
        })

    return {k: v for k, v in result.items() if v}

def normalize_text(text: str) -> str:
    text = re.sub(r'(?<=[а-яёa-z0-9])(?=[А-ЯЁA-Z])', ' ', text or '')
    text = text.replace('_', ' ').replace('ё', 'е').replace('Ё', 'Е').lower()
    text = re.sub(r'[^а-яa-z0-9]+', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

def compact_path(path: Path):
    return str(path.resolve()) if path and path.exists() else None

def object_id_for(type_ru: str, name: str) -> str:
    return f"{PREFIX_MAP.get(type_ru, 'Объект')}.{name}"

def collect_source_paths(object_folder: Path, xml_path: Path) -> dict:
    paths = {
        "xml": compact_path(xml_path),
        "object_folder": compact_path(object_folder),
        "object_module": None,
        "manager_module": None,
        "module": None,
        "forms": []
    }

    if not object_folder or not object_folder.exists():
        return paths

    paths["object_module"] = compact_path(object_folder / "Ext" / "ObjectModule.bsl")
    paths["manager_module"] = compact_path(object_folder / "Ext" / "ManagerModule.bsl")
    paths["module"] = compact_path(object_folder / "Ext" / "Module.bsl")

    forms_dir = object_folder / "Forms"
    if forms_dir.exists():
        for form_xml in sorted(forms_dir.glob("*.xml")):
            form_name = form_xml.stem
            form_folder = forms_dir / form_name
            paths["forms"].append({
                "name": form_name,
                "form_xml": compact_path(form_folder / "Ext" / "Form.xml"),
                "form_module": compact_path(form_folder / "Ext" / "Form" / "Module.bsl")
            })

    return paths

def module_kind(bsl_file: Path) -> str:
    parts = set(bsl_file.parts)
    if "Forms" in parts:
        return "form"
    if bsl_file.name == "ObjectModule.bsl":
        return "object"
    if bsl_file.name == "ManagerModule.bsl":
        return "manager"
    if bsl_file.name == "Module.bsl":
        return "common"
    return "other"

QUERY_OBJECT_PREFIXES = {
    "Документ",
    "Справочник",
    "Перечисление",
    "РегистрСведений",
    "РегистрНакопления",
    "РегистрБухгалтерии",
    "РегистрРасчета",
    "ПланВидовХарактеристик",
    "ПланСчетов",
    "ПланВидовРасчета",
    "БизнесПроцесс",
    "Задача",
    "ПланОбмена"
}

def extract_query_object_ids(
    content: str,
    known_object_ids: set,
    current_object_id: str,
    *,
    search_mode: str = "quoted",
) -> set:
    if search_mode == "full":
        query_text = content
    else:
        quoted_strings = re.findall(r'"(?:[^"]|"")*"', content, flags=re.DOTALL)
        query_text = "\n".join(quoted_strings)
    pattern = re.compile(r'\b(' + '|'.join(QUERY_OBJECT_PREFIXES) + r')\.([А-Яа-яЁёA-Za-z0-9_]+)\b')

    result = set()
    for prefix, name in pattern.findall(query_text):
        object_id = f"{prefix}.{name}"
        if object_id in known_object_ids and object_id != current_object_id:
            result.add(object_id)
    return result


def build_object_flags(obj: dict, bsl_modules: list[dict]) -> dict[str, bool]:
    """Компактные флаги для graph_index / context-mcp."""
    structure = obj.get("structure") or {}
    signatures = [sig for module in bsl_modules for sig in module.get("signatures", [])]
    handler_names = {sig.get("name") for sig in signatures}
    return {
        "has_predefined": bool(structure.get("predefined_items")),
        "has_forms": bool(structure.get("forms")),
        "has_templates": bool(structure.get("templates")),
        "has_skd_queries": any((t.get("skd_queries") for t in structure.get("templates") or [])),
        "has_register_records": bool(structure.get("register_records")),
        "has_posting_handler": "ОбработкаПроведения" in handler_names,
        "has_http_endpoints": bool(structure.get("http_endpoints")),
        "has_module_flags": bool(structure.get("module_flags")),
    }


def render_structure_block(structure: dict, known_objects: dict | None = None) -> list[str]:
    """Markdown-блок структуры объекта для карточки Obsidian.

    Покрывает: реквизиты, ТЧ (с реквизитами), измерения/ресурсы регистров,
    значения перечислений, регистраторы, формы (с элементами), макеты,
    команды, подсистемы.

    Если известно отображение known_objects (имя → тип_ru), для ссылочных
    типов вместо `СправочникСсылка.X` рендерится викилинк `[[Справочник.X]]`.
    """
    known_objects = known_objects or {}
    lines: list[str] = []

    def _format_type(attr_type: str | None) -> str:
        if not attr_type:
            return ""
        ids = extract_object_ids_from_type(attr_type)
        # Если в типе есть один или несколько ссылок на известные объекты,
        # подменяем их на викилинки [[ObjectId]].
        if ids:
            rendered_parts: list[str] = []
            consumed = False
            for part in attr_type.split("|"):
                part_ids = extract_object_ids_from_type(part)
                linked = [oid for oid in part_ids if oid.split(".", 1)[1] in known_objects]
                if linked:
                    rendered_parts.append(", ".join(f"[[{oid}]]" for oid in sorted(linked)))
                    consumed = True
                else:
                    rendered_parts.append(part)
            if consumed:
                return " \\| ".join(rendered_parts)
        return f"`{attr_type}`"

    def _attr_line(name: str, attr_type: str | None) -> str:
        formatted = _format_type(attr_type)
        return f"  - {name}: {formatted}" if formatted else f"  - {name}"

    attrs = structure.get("attributes") or []
    if attrs:
        lines.append(f"* Реквизиты ({len(attrs)}):")
        for a in attrs[:40]:
            lines.append(_attr_line(a.get("name", "?"), a.get("type")))
        if len(attrs) > 40:
            lines.append(f"  - …(+{len(attrs) - 40})")

    tabs = structure.get("tabular_sections") or []
    for ts in tabs:
        ts_name = ts.get("name", "?")
        ts_attrs = ts.get("attributes") or []
        lines.append(f"* ТЧ.{ts_name} ({len(ts_attrs)}):")
        for a in ts_attrs[:25]:
            lines.append(_attr_line(a.get("name", "?"), a.get("type")))
        if len(ts_attrs) > 25:
            lines.append(f"  - …(+{len(ts_attrs) - 25})")

    dims = structure.get("dimensions") or []
    if dims:
        lines.append(f"* Измерения ({len(dims)}):")
        for d in dims:
            lines.append(_attr_line(d.get("name", "?"), d.get("type")))

    res = structure.get("resources") or []
    if res:
        lines.append(f"* Ресурсы ({len(res)}):")
        for r in res:
            lines.append(_attr_line(r.get("name", "?"), r.get("type")))

    enums = structure.get("enum_values") or []
    if enums:
        names = [e.get("name", "?") if isinstance(e, dict) else str(e) for e in enums]
        lines.append(f"* Значения ({len(enums)}): {', '.join(names)}")

    predefined = structure.get("predefined_items") or []
    if predefined:
        lines.append(f"* Предопределённые ({len(predefined)}):")
        for item in predefined[:30]:
            label = item.get("name", "?")
            desc = item.get("description") or ""
            code = item.get("code") or ""
            extras = []
            if desc and desc != label:
                extras.append(desc)
            if code:
                extras.append(f"код {code}")
            suffix = f" ({', '.join(extras)})" if extras else ""
            bsl = item.get("bsl_access")
            lines.append(f"  - {label}{suffix}" + (f" → `{bsl}`" if bsl else ""))

    rr = structure.get("register_records") or []
    if rr:
        lines.append("* Регистраторы (пишет в):")
        for r in rr:
            lines.append(f"  - [[{r}]]")

    forms = structure.get("forms") or []
    if forms:
        lines.append(f"* Формы ({len(forms)}):")
        for f in forms:
            f_name = f.get("name", "?")
            f_kind = f.get("kind", "")
            lines.append(f"  - {f_name} ({f_kind})" if f_kind else f"  - {f_name}")
            internals = f.get("internals") or {}
            controls = internals.get("controls") or []
            if controls:
                lines.append(f"    - элементы ({len(controls)}):")
                for c in controls[:20]:
                    dp = c.get("data_path") or ""
                    arrow = f" → `{dp}`" if dp else ""
                    lines.append(f"      - {c.get('name', '?')} ({c.get('type', '?')}){arrow}")
                if len(controls) > 20:
                    lines.append(f"      - …(+{len(controls) - 20})")
            cmds = internals.get("commands") or []
            if cmds:
                lines.append(f"    - команды формы: {', '.join(cmds)}")
            f_attrs = internals.get("attributes") or []
            if f_attrs:
                lines.append(f"    - реквизиты формы: {', '.join(f_attrs)}")

    templates = structure.get("templates") or []
    if templates:
        lines.append(f"* Макеты ({len(templates)}):")
        for tpl in templates:
            label = tpl.get("name", "?")
            q_count = len(tpl.get("skd_queries") or [])
            lines.append(f"  - {label}" + (f" (СКД-запросов: {q_count})" if q_count else ""))

    http_endpoints = structure.get("http_endpoints") or []
    if http_endpoints:
        lines.append(f"* HTTP-методы ({len(http_endpoints)}):")
        for ep in http_endpoints[:20]:
            lines.append(
                f"  - {ep.get('http_method', '?')} {ep.get('template', '/')} "
                f"→ {ep.get('handler', '?')}"
            )

    module_flags = structure.get("module_flags") or {}
    if module_flags:
        enabled = [key for key, value in module_flags.items() if value]
        if enabled:
            lines.append(f"* Свойства модуля: {', '.join(enabled)}")

    commands = structure.get("commands") or []
    if commands:
        lines.append(f"* Команды ({len(commands)}): " + ", ".join(c.get("name", "?") for c in commands))

    subsystems = structure.get("subsystems") or []
    if subsystems:
        lines.append(f"* Подсистемы: {', '.join(subsystems)}")

    return lines


# ==========================================
# 🚀 ОСНОВНАЯ ЛОГИКА
# ==========================================
class ObsidianSync:
    def __init__(self):
        self.registry = defaultdict(list)
        self.known_objects = {}
        self.known_object_ids = set()

    def scan_project(self):
        print("🔍 Этап 1: Сканирование метаданных XML...")
        # Сначала строим индекс подсистем (object_id → [подсистемы])
        self.subsystems_index = build_subsystems_index(PROJECT_PATHS)
        for project_name, source_dir in PROJECT_PATHS.items():
            if not source_dir.exists(): continue
            is_extension = (project_name != "Основная")

            for root, dirs, files in os.walk(source_dir):
                root_path = Path(root)
                folder_name = root_path.name
                if folder_name not in TARGET_TYPES: continue
                object_type_ru = TARGET_TYPES[folder_name]

                for file in files:
                    if file.endswith(".xml") and not file.startswith("Ext"): 
                        file_path = root_path / file
                        meta = parse_metadata(read_1c_file(file_path))
                        
                        if meta["name"] != "Неизвестно":
                            object_folder = root_path / file_path.stem
                            if not object_folder.exists():
                                object_folder = root_path / meta["name"]
                            if not object_folder.exists():
                                object_folder = None

                            prefix = PREFIX_MAP.get(object_type_ru, "Объект")
                            meta["object_id"] = object_id_for(object_type_ru, meta["name"])
                            meta["meta_type"] = folder_name
                            meta["type_ru"] = object_type_ru
                            meta["prefix"] = prefix
                            meta["location"] = f"🧩 Расширение: {project_name}" if is_extension else "Основная конфигурация"
                            meta["project_name"] = project_name
                            meta["is_extension"] = is_extension
                            meta["link"] = f"[[{meta['object_id']}]]"
                            meta["xml_path"] = file_path
                            meta["source_folder"] = object_folder
                            meta["calls"] = set()
                            meta["calls_ids"] = set()
                            meta["query_ids"] = set()

                            # Дополняем структуру подэлементами с диска (формы/макеты/команды)
                            subitems = scan_object_subitems(object_folder)
                            if subitems:
                                meta.setdefault("structure", {}).update(subitems)
                            attach_predefined_to_structure(object_folder, meta)
                            if folder_name == "HTTPServices":
                                http_structure = parse_http_service_structure(read_1c_file(file_path))
                                if http_structure:
                                    meta.setdefault("structure", {}).update(http_structure)
                            if folder_name == "CommonModules":
                                module_flags = parse_common_module_flags(read_1c_file(file_path))
                                if module_flags:
                                    meta.setdefault("structure", {})["module_flags"] = module_flags
                            # Подсистемы, в которые включён объект
                            subsystems = self.subsystems_index.get(meta["object_id"], [])
                            if subsystems:
                                meta.setdefault("structure", {})["subsystems"] = subsystems

                            self.registry[object_type_ru].append(meta)
                            self.known_objects[meta["name"]] = object_type_ru
                            self.known_object_ids.add(meta["object_id"])

    def enrich_xml_links_from_structure(self):
        """Пополнить xml_links объектов ссылками, извлечёнными из типов
        реквизитов/ТЧ/измерений/ресурсов. Это закрывает пробел: типы
        вида `СправочникСсылка.X` раньше не превращались в графовые связи."""
        print("🔗 Этап 1.5: Извлечение структурных связей из типов реквизитов...")
        for objects in self.registry.values():
            for obj in objects:
                structure = obj.get("structure") or {}
                struct_links: set[str] = set()
                # Атрибуты верхнего уровня
                for a in structure.get("attributes") or []:
                    struct_links.update(extract_object_ids_from_type(a.get("type")))
                # ТЧ → их атрибуты
                for ts in structure.get("tabular_sections") or []:
                    for a in ts.get("attributes") or []:
                        struct_links.update(extract_object_ids_from_type(a.get("type")))
                # Измерения и ресурсы регистров
                for d in structure.get("dimensions") or []:
                    struct_links.update(extract_object_ids_from_type(d.get("type")))
                for r in structure.get("resources") or []:
                    struct_links.update(extract_object_ids_from_type(r.get("type")))
                # Сохраняем по короткому имени (формат, в котором уже работает xml_links)
                own_id = obj["object_id"]
                for object_id in struct_links:
                    if object_id == own_id:
                        continue
                    if object_id not in self.known_object_ids:
                        continue
                    short_name = object_id.split(".", 1)[1]
                    obj.setdefault("xml_links", set()).add(short_name)

    def enrich_skd_queries(self):
        """Извлекает объекты из текстов СКД-запросов в макетах отчётов/обработок."""
        print("📊 Этап 1.6: Извлечение связей из СКД-запросов...")
        for objects in self.registry.values():
            for obj in objects:
                for template in (obj.get("structure") or {}).get("templates") or []:
                    for query_text in template.get("skd_queries") or []:
                        obj["query_ids"].update(
                            extract_query_object_ids(
                                query_text, self.known_object_ids, obj["object_id"], search_mode="full"
                            )
                        )

    def analyze_code_links(self):
            print("🧠 Этап 2: Анализ связей в коде (BSL)...")
            
            # Паттерн 1: Вызовы процедур (ОбщийМодуль.Метод() или Обработка.Метод())
            pattern_module = re.compile(r'\b([А-Яа-яЁёA-Za-z0-9_]+)\.[А-Яа-яЁёA-Za-z0-9_]+\s*\(')
            
            # Паттерн 2: Вызовы через менеджеры всех возможных классов
            manager_classes = "|".join([
                "Справочники", "Документы", "ЖурналыДокументов", "Перечисления", 
                "Отчеты", "Обработки", "ПланыВидовХарактеристик", "ПланыСчетов", 
                "ПланыВидовРасчета", "РегистрыСведений", "РегистрыНакопления", 
                "РегистрыБухгалтерии", "РегистрыРасчета", "БизнесПроцессы", 
                "Задачи", "ПланыОбмена", "Константы"
            ])
            pattern_manager = re.compile(rf'\b(?:{manager_classes})\.([А-Яа-яЁёA-Za-z0-9_]+)\b')
            pattern_movements = re.compile(r'\bДвижения\.([А-Яа-яЁёA-Za-z0-9_]+)\b')
            pattern_predefined = re.compile(
                r'\bСправочники\.([А-Яа-яЁёA-Za-z0-9_]+)\.([А-Яа-яЁёA-Za-z0-9_]+)\b'
            )

            register_type_ru = {
                "РегистрыСведений", "РегистрыНакопления",
                "РегистрыБухгалтерии", "РегистрыРасчета",
            }

            def _add_code_link(obj: dict, target_id: str) -> None:
                if target_id == obj["object_id"]:
                    return
                obj["calls"].add(f"[[{target_id}]]")
                obj["calls_ids"].add(target_id)

            for obj_type, objects in self.registry.items():
                for obj in objects:
                    folder = obj.get("source_folder")
                    if not folder or not folder.exists(): 
                        continue
                    
                    # Ищем все .bsl файлы внутри папки объекта (модуль объекта, менеджера, формы и т.д.)
                    for bsl_file in folder.rglob("*.bsl"):
                        content = read_1c_file(bsl_file)
                        obj["query_ids"].update(extract_query_object_ids(content, self.known_object_ids, obj["object_id"]))
                        
                        # Собираем все совпадения по обоим паттернам
                        matches = pattern_module.findall(content) + pattern_manager.findall(content)
                        
                        for match in matches:
                            # Если найденное слово реально является объектом нашего проекта и это не вызов самого себя
                            if match in self.known_objects and match != obj['name']:
                                target_type = self.known_objects[match]
                                target_prefix = PREFIX_MAP.get(target_type, "Объект")
                                target_id = f"{target_prefix}.{match}"
                                _add_code_link(obj, target_id)

                        for register_name in pattern_movements.findall(content):
                            if register_name not in self.known_objects or register_name == obj["name"]:
                                continue
                            target_type = self.known_objects[register_name]
                            if target_type not in register_type_ru:
                                continue
                            target_id = f"{PREFIX_MAP.get(target_type, 'Объект')}.{register_name}"
                            _add_code_link(obj, target_id)

                        for catalog_name, _item_name in pattern_predefined.findall(content):
                            if catalog_name in self.known_objects and catalog_name != obj["name"]:
                                target_type = self.known_objects[catalog_name]
                                target_prefix = PREFIX_MAP.get(target_type, "Объект")
                                _add_code_link(obj, f"{target_prefix}.{catalog_name}")

    def cleanup_stale_vault_files(self):
        """Удаляет устаревшие файлы индекса 1С перед регенерацией:
        - Старые индексы XX_Индекс_*.md (счётчик мог измениться)
        - Старые карточки с английскими префиксами (Catalog.*, Document.*, ...)
        - Легаси-артефакты в корне vault (до миграции в 99-Meta/1C-Index)
        """
        english_prefixes = (
            "Catalog.", "Document.", "DataProcessor.", "Report.",
            "InformationRegister.", "AccumulationRegister.", "AccountingRegister.",
            "CalculationRegister.", "Enum.", "DocumentJournal.", "CommonModule.",
            "Constant.", "Subsystem.", "BusinessProcess.", "Task.",
            "ChartOfCharacteristicTypes.", "ChartOfAccounts.", "ChartOfCalculationTypes.",
            "ExchangePlan.", "Role.", "SessionParameter.", "ScheduledJob.",
            "EventSubscription.",
        )
        removed_indexes = 0
        removed_legacy = 0

        def _clean_md_folder(folder: Path) -> None:
            nonlocal removed_indexes, removed_legacy
            if not folder.exists():
                return
            for f in folder.glob("*.md"):
                name = f.name
                if re.match(r"^\d{2}_Индекс_.+\.md$", name):
                    try:
                        f.unlink()
                        removed_indexes += 1
                    except OSError:
                        pass
                    continue
                if any(name.startswith(p) for p in english_prefixes):
                    try:
                        f.unlink()
                        removed_legacy += 1
                    except OSError:
                        pass

        _clean_md_folder(INDEX_ROOT)
        if OBSIDIAN_VAULT.exists():
            _clean_md_folder(OBSIDIAN_VAULT)
        if removed_indexes or removed_legacy:
            print(f"🧹 Очистка индекса 1С: индексов={removed_indexes}, легаси-карточек={removed_legacy}")

    def generate_moc_files(self):
        print("📝 Этап 3: Генерация файлов MOC...")
        INDEX_ROOT.mkdir(parents=True, exist_ok=True)
        self.cleanup_stale_vault_files()
        main_moc_lines = ["# 🗺️ Карта метаданных 1С\n", "Автогенерация из `sync_1c_obsidian.py`. Папка: `99-Meta/1C-Index/`.\n"]

        index_counter = 1
        for obj_type, objects in self.registry.items():
            objects.sort(key=lambda x: x["name"])
            moc_filename = f"{index_counter:02d}_Индекс_{obj_type}.md"
            with open(INDEX_ROOT / moc_filename, "w", encoding="utf-8") as f:
                f.write(f"# 🗂️ Индекс: {obj_type}\n\n| Объект в 1С | Синоним | Расположение | Ссылка |\n| :--- | :--- | :--- | :--- |\n")
                for obj in objects:
                    clean_comment = obj['comment'].replace('\n', ' ').strip()
                    desc = obj['synonym'] if obj['synonym'] else clean_comment
                    f.write(f"| {obj['name']} | {desc} | {obj['location']} | {obj['link']} |\n")
            main_moc_lines.append(f"* 📁 [[{INDEX_PREFIX}/{moc_filename[:-3]}]] — Реестр: {obj_type}")
            index_counter += 1

        with open(INDEX_ROOT / "00_Архитектура_Проекта.md", "w", encoding="utf-8") as f:
            f.write("\n".join(main_moc_lines))

    def generate_object_cards(self):
        print("🗂️ Этап 4: Генерация карточек объектов и связей...")
        for obj_type, objects in self.registry.items():
            folder_path = INDEX_ROOT / obj_type
            folder_path.mkdir(parents=True, exist_ok=True)
            prefix = PREFIX_MAP.get(obj_type, "Объект")
            
            grouped_objects = defaultdict(list)
            for obj in objects: grouped_objects[obj['name']].append(obj)

            for obj_name, versions in grouped_objects.items():
                file_path = folder_path / f"{prefix}.{obj_name}.md"
                sync_block_lines = ["<!-- SYNC-START -->", "## 🔄 Автоматические данные (Не редактировать)"]
                
                for version in versions:
                    icon = "🏢" if version['location'] == "Основная конфигурация" else "🧩"
                    sync_block_lines.append(f"\n### {icon} {version['location']}")
                    if version['synonym']: sync_block_lines.append(f"**Синоним:** {version['synonym']}")
                    if version['comment']: sync_block_lines.append(f"**Комментарий:** {version['comment'].strip()}")
                    
                    # НОВОЕ: Обработка структурных связей (реквизиты)
                    valid_xml_links = set()
                    for link in version.get('xml_links', []):
                        if link in self.known_objects and link != obj_name:
                            t_prefix = PREFIX_MAP.get(self.known_objects[link], "Объект")
                            valid_xml_links.add(f"[[{t_prefix}.{link}]]")
                            
                    if valid_xml_links:
                        sync_block_lines.append("\n**Связи в метаданных (Реквизиты/ТЧ):**")
                        for link in sorted(valid_xml_links):
                            sync_block_lines.append(f"* {link}")

                    # НОВОЕ: Структура объекта (реквизиты, ТЧ, измерения, ресурсы, регистраторы, формы, подсистемы)
                    structure = version.get('structure') or {}
                    if structure:
                        struct_lines = render_structure_block(structure, self.known_objects)
                        if struct_lines:
                            sync_block_lines.append("\n**Структура:**")
                            sync_block_lines.extend(struct_lines)

                    # Обработка связей кода
                    if version['calls']:
                        sync_block_lines.append("\n**Исходящие вызовы (Код):**")
                        for call in sorted(version['calls']):
                            sync_block_lines.append(f"* {call}")

                    if version['query_ids']:
                        sync_block_lines.append("\n**Связи в запросах (BSL):**")
                        for query_link in sorted(version['query_ids']):
                            sync_block_lines.append(f"* [[{query_link}]]")
                
                sync_block_lines.append("<!-- SYNC-END -->")
                sync_content = "\n".join(sync_block_lines)

                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f: content = f.read()
                    pattern = r"<!-- SYNC-START -->.*?<!-- SYNC-END -->"
                    if re.search(pattern, content, flags=re.DOTALL):
                        new_content = re.sub(pattern, sync_content, content, flags=re.DOTALL)
                    else:
                        parts = content.split("---", 2)
                        new_content = f"---{parts[1]}---\n\n{sync_content}\n{parts[2]}" if content.startswith("---") and len(parts) >= 3 else f"{sync_content}\n\n{content}"
                    with open(file_path, 'w', encoding='utf-8') as f: f.write(new_content)
                else:
                    template = f"---\ntype: 1c-{prefix.lower()}\nname: {obj_name}\naliases: [{prefix}.{obj_name}]\n---\n# {prefix}: {obj_name}\n\n{sync_content}\n\n## 📝 Пользовательские заметки\n"
                    with open(file_path, 'w', encoding='utf-8') as f: f.write(template)

    def generate_graph_index(self):
        print("🧭 Этап 5: Генерация компактного graph_index.json...")
        copilot_dir = OBSIDIAN_VAULT / ".copilot"
        copilot_dir.mkdir(parents=True, exist_ok=True)

        index = {
            "schema_version": 2,
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "project": Path.cwd().name,
            "source_config": {name: str(path.resolve()) for name, path in PROJECT_PATHS.items()},
            "stats": {
                "objects": 0,
                "modules": 0,
                "links_metadata": 0,
                "links_code": 0,
                "links_query": 0,
                "links_writers": 0,
                "objects_with_predefined": 0,
                "http_services": 0,
            },
            "objects": {}
        }

        for obj_type, objects in self.registry.items():
            prefix = PREFIX_MAP.get(obj_type, "Объект")
            for obj in objects:
                metadata_links = []
                for link_name in sorted(obj.get("xml_links", [])):
                    target_type = self.known_objects.get(link_name)
                    if target_type and link_name != obj["name"]:
                        metadata_links.append(object_id_for(target_type, link_name))

                bsl_modules = []
                source_folder = obj.get("source_folder")
                if source_folder and source_folder.exists():
                    for bsl_file in sorted(source_folder.rglob("*.bsl")):
                        module_entry = {
                            "kind": module_kind(bsl_file),
                            "path": str(bsl_file.resolve())
                        }
                        signatures = parse_bsl_signatures(bsl_file)
                        if signatures:
                            module_entry["signatures"] = signatures
                        bsl_modules.append(module_entry)

                name_normalized = normalize_text(obj["name"])
                synonym_normalized = normalize_text(obj.get("synonym", ""))
                aliases = [obj["object_id"], obj["name"], obj.get("synonym", ""), name_normalized, synonym_normalized]
                aliases = sorted({alias for alias in aliases if alias})
                tokens = sorted({token for alias in aliases for token in normalize_text(alias).split() if token})

                object_entry = {
                    "object_id": obj["object_id"],
                    "meta_type": obj.get("meta_type"),
                    "type_ru": prefix,
                    "name": obj["name"],
                    "synonym": obj.get("synonym", ""),
                    "comment": obj.get("comment", ""),
                    "location": obj.get("project_name", "Основная"),
                    "is_extension": obj.get("is_extension", False),
                    "search": {
                        "aliases": aliases,
                        "tokens": tokens,
                        "normalized": normalize_text(" ".join(aliases))
                    },
                    "obsidian": {
                        "note_path": f"{INDEX_PREFIX}/{obj_type}/{prefix}.{obj['name']}.md"
                    },
                    "source_paths": collect_source_paths(obj.get("source_folder"), obj.get("xml_path")),
                    "modules": bsl_modules,
                    "links": {
                        "metadata": metadata_links,
                        "code": sorted(obj.get("calls_ids", [])),
                        "query": sorted(obj.get("query_ids", [])),
                        "incoming": [],
                        "writers": [],
                    },
                    "structure": obj.get("structure", {}),
                    "flags": build_object_flags(obj, bsl_modules),
                    "context": {
                        "default_profile": obj.get("meta_type"),
                        "preferred_depth": 1,
                        "risk_flags": []
                    }
                }

                index["objects"][obj["object_id"]] = object_entry
                index["stats"]["objects"] += 1
                index["stats"]["modules"] += len(bsl_modules)
                index["stats"]["links_metadata"] += len(metadata_links)
                index["stats"]["links_code"] += len(object_entry["links"]["code"])
                index["stats"]["links_query"] += len(object_entry["links"]["query"])
                if object_entry["flags"].get("has_predefined"):
                    index["stats"]["objects_with_predefined"] += 1
                if prefix == "HTTPСервис":
                    index["stats"]["http_services"] += 1

        for object_id, obj in index["objects"].items():
            for link_type in ("metadata", "code", "query"):
                for target_id in obj["links"][link_type]:
                    target = index["objects"].get(target_id)
                    if target and object_id not in target["links"]["incoming"]:
                        target["links"]["incoming"].append(object_id)

            if obj.get("type_ru") == "Документ":
                for register_id in obj.get("structure", {}).get("register_records", []):
                    register = index["objects"].get(register_id)
                    if not register:
                        continue
                    if object_id not in register["links"]["writers"]:
                        register["links"]["writers"].append(object_id)
                    if object_id not in register["links"]["incoming"]:
                        register["links"]["incoming"].append(object_id)

        for obj in index["objects"].values():
            obj["links"]["incoming"].sort()
            obj["links"]["writers"].sort()

        index["stats"]["links_writers"] = sum(
            len(obj["links"]["writers"]) for obj in index["objects"].values()
        )

        with open(copilot_dir / "graph_index.json", "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    sync = ObsidianSync()
    sync.scan_project()
    sync.enrich_xml_links_from_structure()
    sync.enrich_skd_queries()
    sync.analyze_code_links()
    sync.generate_moc_files()
    sync.generate_object_cards()
    sync.generate_graph_index()
    print("\n✅ Синхронизация успешно завершена!")