import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = PROJECT_ROOT / "config.json"

sys.path.insert(0, str(PROJECT_ROOT))
try:
    from token_counter import count_tokens
except ImportError:
    def count_tokens(text: str, model: str = "gpt-4o") -> int:
        return max(1, len(text) // 4)


TYPE_HINTS = {
    "документ": "Документ",
    "док": "Документ",
    "справочник": "Справочник",
    "спр": "Справочник",
    "перечисление": "Перечисление",
    "регистр": "Регистр",
    "регистрсведений": "РегистрСведений",
    "регистрнакопления": "РегистрНакопления",
    "общий": "ОбщийМодуль",
    "общиймодуль": "ОбщийМодуль",
    "модуль": "ОбщийМодуль",
    "обработка": "Обработка",
    "отчет": "Отчет",
    "отчёт": "Отчет",
    "форма": "Форма"
}

TYPE_FILTERS = {
    "документ": {"Документ"},
    "окумент": {"Документ"},
    "documents": {"Документ"},
    "справочник": {"Справочник"},
    "правочник": {"Справочник"},
    "catalogs": {"Справочник"},
    "перечисление": {"Перечисление"},
    "enums": {"Перечисление"},
    "регистр": {"РегистрСведений", "РегистрНакопления", "РегистрБухгалтерии", "РегистрРасчета"},
    "регистрсведений": {"РегистрСведений"},
    "informationregisters": {"РегистрСведений"},
    "регистрнакопления": {"РегистрНакопления"},
    "accumulationregisters": {"РегистрНакопления"},
    "общиймодуль": {"ОбщийМодуль"},
    "бщиймодуль": {"ОбщийМодуль"},
    "бщийодуль": {"ОбщийМодуль"},
    "модуль": {"ОбщийМодуль"},
    "commonmodules": {"ОбщийМодуль"},
    "обработка": {"Обработка"},
    "бработка": {"Обработка"},
    "dataprocessors": {"Обработка"},
    "отчет": {"Отчет"},
    "отчёт": {"Отчет"},
    "reports": {"Отчет"},
    "форма": {"Форма"}
}

TOKEN_EXPANSIONS = {
    "загрузка": {"заполнение", "импорт"},
    "загрузки": {"заполнение", "импорт"},
    "загрузить": {"заполнение", "импорт"},
    "товар": {"номенклатура", "тмц"},
    "товары": {"номенклатура", "тмц"},
    "накладная": {"накладных"},
    "накладные": {"накладных"}
}

TRANSLIT_RU_EN = str.maketrans({
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e", "ж": "zh", "з": "z",
    "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r",
    "с": "s", "т": "t", "у": "u", "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh",
    "щ": "sch", "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya"
})

DATA_TYPES = {
    "Справочник",
    "Документ",
    "Перечисление",
    "РегистрСведений",
    "РегистрНакопления",
    "РегистрБухгалтерии",
    "РегистрРасчета",
    "Константа"
}

LOGIC_TYPES = {"ОбщийМодуль", "Обработка", "Отчет"}

# Каталог типовых stage-лейблов. Используется для подсказки агенту, чтобы
# обеспечить единообразную маркировку context-запросов (агрегация в report).
# Агент НЕ ограничен этим списком — может вводить свои, но рекомендуется выбирать
# отсюда. При новом лейбле — добавить сюда и закоммитить, чтобы накапливать словарь.
STAGE_CATALOG = {
    # --- Документы ---
    "doc.fields":      "посмотреть реквизиты и ТЧ документа",
    "doc.posting":     "проверить движения документа по регистрам",
    "doc.form":        "найти обработчики формы документа",
    "doc.refs":        "найти где документ используется (incoming)",
    "doc.queries":     "найти запросы к документу из других модулей",
    # --- Справочники ---
    "cat.fields":      "посмотреть реквизиты и ТЧ справочника",
    "cat.refs":        "найти где справочник используется как ссылка",
    "cat.predefined":  "посмотреть предопределённые элементы",
    # --- Регистры ---
    "reg.structure":   "измерения/ресурсы/реквизиты регистра",
    "reg.writers":     "найти все объекты, пишущие в регистр",
    "reg.readers":     "найти запросы к регистру из отчётов/модулей",
    # --- Общие модули / процедуры ---
    "module.api":      "посмотреть экспортные методы общего модуля",
    "module.callers":  "найти вызовы метода общего модуля",
    "module.deps":     "карта зависимостей общего модуля",
    # --- Отчёты / обработки ---
    "report.queries":  "посмотреть запросы и источники данных отчёта",
    "report.layout":   "посмотреть макеты и СКД отчёта",
    "proc.flow":       "посмотреть основной алгоритм обработки",
    # --- Сквозные ---
    "attr.usages":     "найти все места использования реквизита",
    "type.usages":     "найти все места использования типа/перечисления",
    "form.controls":   "посмотреть элементы и команды формы",
    "schema.overview": "общий обзор объекта (первое знакомство)",
    "bug.repro":       "собрать минимум для воспроизведения бага",
}

# Переопределения PROFILE_RULES при явном --stage / stage= в MCP.
# Пустой dict = оставить профиль task без изменений (schema.overview).
STAGE_OVERRIDES: dict[str, dict] = {
    "schema.overview": {},
    "bug.repro": {
        "depth": 1,
        "logic_limit": 6,
        "data_limit": 20,
        "incoming_limit": 6,
        "data_brief_limit": 2,
        "include_incoming_briefs": False,
    },
    "doc.fields": {"depth": 0, "target_links": (), "include_target_api": False},
    "doc.posting": {
        "depth": 1,
        "target_links": ("metadata",),
        "dependency_link_types": ("metadata", "code"),
        "logic_limit": 6,
        "data_limit": 40,
        "data_brief_limit": 6,
        "focus_types": ("РегистрНакопления", "РегистрСведений", "РегистрБухгалтерии"),
        "include_target_api": False,
        "include_incoming_briefs": False,
    },
    "doc.form": {
        "depth": 0,
        "target_links": ("code",),
        "include_target_api": True,
        "dependency_link_types": (),
    },
    "form.controls": {
        "depth": 0,
        "target_links": (),
        "include_target_api": True,
        "dependency_link_types": (),
    },
    "doc.refs": {
        "depth": 1,
        "target_links": ("metadata", "incoming"),
        "include_target_api": False,
        "include_incoming_briefs": True,
        "logic_limit": 8,
        "data_limit": 0,
        "data_brief_limit": 0,
        "dependency_link_types": ("incoming",),
    },
    "doc.queries": {
        "depth": 1,
        "target_links": ("query", "code"),
        "include_target_api": False,
        "logic_limit": 12,
        "data_limit": 20,
        "dependency_link_types": ("code", "query"),
        "include_incoming_briefs": True,
    },
    "cat.fields": {"depth": 0, "target_links": (), "include_target_api": False},
    "cat.refs": {
        "depth": 1,
        "target_links": ("metadata", "incoming"),
        "include_target_api": False,
        "include_incoming_briefs": True,
        "logic_limit": 6,
        "data_limit": 0,
        "data_brief_limit": 0,
        "dependency_link_types": ("incoming",),
    },
    "cat.predefined": {
        "depth": 0,
        "target_links": (),
        "include_target_api": False,
        "include_predefined_only": True,
    },
    "reg.structure": {"depth": 0, "target_links": (), "include_target_api": False},
    "reg.writers": {
        "depth": 1,
        "target_links": ("writers", "incoming"),
        "include_target_api": False,
        "include_incoming_briefs": True,
        "logic_limit": 10,
        "data_limit": 0,
        "dependency_link_types": ("incoming",),
    },
    "reg.readers": {
        "depth": 1,
        "target_links": ("query", "code"),
        "include_target_api": False,
        "logic_limit": 12,
        "data_limit": 10,
        "dependency_link_types": ("code", "query"),
        "include_incoming_briefs": True,
    },
    "module.api": {
        "depth": 0,
        "target_links": ("code",),
        "include_target_api": True,
        "dependency_link_types": (),
    },
    "module.callers": {
        "depth": 1,
        "target_links": ("incoming",),
        "include_target_api": True,
        "include_incoming_briefs": True,
        "logic_limit": 12,
        "data_limit": 0,
        "dependency_link_types": ("incoming",),
    },
    "module.deps": {
        "depth": 1,
        "target_links": ("code", "query", "metadata", "incoming"),
        "dependency_link_types": ("code", "query", "metadata", "incoming"),
        "logic_limit": 16,
        "data_limit": 40,
        "include_incoming_briefs": True,
        "include_target_api": True,
    },
    "report.queries": {
        "depth": 1,
        "target_links": ("query", "metadata"),
        "include_target_api": False,
        "logic_limit": 8,
        "data_limit": 30,
        "dependency_link_types": ("query", "metadata"),
    },
    "report.layout": {"depth": 0, "target_links": (), "include_target_api": False},
    "proc.flow": {
        "depth": 1,
        "target_links": ("code", "query"),
        "include_target_api": True,
        "logic_limit": 8,
        "data_limit": 20,
        "dependency_link_types": ("code", "query"),
    },
    "attr.usages": {
        "depth": 1,
        "target_links": ("metadata", "incoming", "query"),
        "include_target_api": False,
        "include_incoming_briefs": True,
        "logic_limit": 8,
        "data_limit": 40,
        "data_brief_limit": 4,
        "dependency_link_types": ("incoming", "query"),
    },
    "type.usages": {
        "depth": 1,
        "target_links": ("metadata", "incoming"),
        "include_target_api": False,
        "include_incoming_briefs": True,
        "logic_limit": 8,
        "data_limit": 20,
        "data_brief_limit": 4,
        "dependency_link_types": ("incoming",),
    },
}

DEPTH_LEVELS = {
    "shallow": 0,
    "medium": 1,
    "deep": 2,
}


def list_stage_catalog() -> str:
    width = max(len(key) for key in STAGE_CATALOG)
    return "\n".join(f"  {key.ljust(width)} — {desc}" for key, desc in STAGE_CATALOG.items())


PROFILE_RULES = {
    "bugfix": {
        "depth": 1,
        "target_links": ("metadata", "code", "query", "incoming"),
        "dependency_link_types": ("code", "query", "metadata"),
        "logic_limit": 12,
        "data_limit": 60,
        "incoming_limit": 12,
        "include_incoming_briefs": False,
        "include_target_api": True,
        "data_brief_limit": 0,
        "focus_types": ()
    },
    "posting": {
        "depth": 1,
        "target_links": ("metadata", "code", "query", "incoming"),
        "dependency_link_types": ("code", "query", "metadata"),
        "logic_limit": 8,
        "data_limit": 80,
        "incoming_limit": 8,
        "include_incoming_briefs": False,
        "include_target_api": True,
        "data_brief_limit": 4,
        "focus_types": ("РегистрНакопления", "РегистрСведений")
    },
    "form-change": {
        "depth": 0,
        "target_links": ("metadata", "code"),
        "dependency_link_types": ("code",),
        "logic_limit": 4,
        "data_limit": 20,
        "incoming_limit": 5,
        "include_incoming_briefs": False,
        "include_target_api": True,
        "data_brief_limit": 0,
        "focus_types": ()
    },
    "attribute-change": {
        "depth": 0,
        "target_links": ("metadata", "query", "incoming"),
        "dependency_link_types": (),
        "logic_limit": 4,
        "data_limit": 80,
        "incoming_limit": 20,
        "include_incoming_briefs": False,
        "include_target_api": False,
        "data_brief_limit": 0,
        "focus_types": ()
    },
    "common-module-change": {
        "depth": 1,
        "target_links": ("code", "query", "incoming"),
        "dependency_link_types": ("code", "query", "incoming"),
        "logic_limit": 12,
        "data_limit": 40,
        "incoming_limit": 8,
        "include_incoming_briefs": True,
        "include_target_api": True,
        "data_brief_limit": 0,
        "focus_types": ("ОбщийМодуль", "Обработка", "Отчет")
    },
    "review": {
        "depth": 1,
        "target_links": ("metadata", "code", "query", "incoming"),
        "dependency_link_types": ("code", "query", "metadata", "incoming"),
        "logic_limit": 16,
        "data_limit": 100,
        "incoming_limit": 8,
        "include_incoming_briefs": True,
        "include_target_api": True,
        "data_brief_limit": 4,
        "focus_types": ()
    },
    "report": {
        "depth": 1,
        "target_links": ("metadata", "query", "incoming"),
        "dependency_link_types": ("query", "metadata"),
        "logic_limit": 4,
        "data_limit": 40,
        "incoming_limit": 8,
        "include_incoming_briefs": False,
        "include_target_api": False,
        "data_brief_limit": 6,
        "focus_types": ("РегистрНакопления", "РегистрСведений", "Документ", "Справочник")
    },
    "integration": {
        "depth": 1,
        "target_links": ("metadata", "code", "query", "incoming"),
        "dependency_link_types": ("code", "query", "metadata"),
        "logic_limit": 8,
        "data_limit": 40,
        "incoming_limit": 10,
        "include_incoming_briefs": False,
        "include_target_api": True,
        "data_brief_limit": 8,
        "focus_types": ("HTTPСервис", "HTTPService", "ОбщийМодуль", "Обработка", "Справочник", "Перечисление")
    },
    "query": {
        "depth": 1,
        "target_links": ("metadata", "query"),
        "dependency_link_types": ("query", "metadata"),
        "logic_limit": 6,
        "data_limit": 60,
        "incoming_limit": 8,
        "include_incoming_briefs": False,
        "include_target_api": False,
        "data_brief_limit": 6,
        "focus_types": ("РегистрНакопления", "РегистрСведений", "Документ", "Справочник")
    }
}


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Не найден {CONFIG_FILE}")
    return json.loads(CONFIG_FILE.read_text(encoding="utf-8-sig"))


def copilot_dir() -> Path:
    vault_path = Path(load_config()["obsidian_vault_path"])
    result = vault_path / ".copilot"
    result.mkdir(parents=True, exist_ok=True)
    return result


def graph_index_path() -> Path:
    return copilot_dir() / "graph_index.json"


def load_graph() -> dict:
    path = graph_index_path()
    if not path.exists():
        raise FileNotFoundError(f"Не найден {path}. Сначала запустите: python sync_1c_obsidian.py")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def normalize_text(text: str) -> str:
    text = re.sub(r"(?<=[а-яёa-z0-9])(?=[А-ЯЁA-Z])", " ", text or "")
    text = text.replace("_", " ").replace("ё", "е").replace("Ё", "Е").lower()
    text = re.sub(r"[^а-яa-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text: str) -> set:
    result = set()
    for token in normalize_text(text).split():
        if not token:
            continue
        result.add(token)
        translit = token.translate(TRANSLIT_RU_EN)
        if translit and translit != token:
            result.add(translit)
        result.update(TOKEN_EXPANSIONS.get(token, set()))
    return result


def get_type_hint(query_tokens: set) -> str | None:
    compact_query = "".join(sorted(query_tokens))
    for token in query_tokens:
        if token in TYPE_HINTS:
            return TYPE_HINTS[token]
    for key, value in TYPE_HINTS.items():
        if key in compact_query:
            return value
    return None


def resolve_type_filter(type_query: str | None) -> set[str] | None:
    if not type_query:
        return None
    normalized = normalize_text(type_query).replace(" ", "")
    return TYPE_FILTERS.get(normalized, {type_query})


def important_tokens(query_tokens: set) -> set:
    service_tokens = set(TYPE_HINTS)
    service_tokens.update(token.translate(TRANSLIT_RU_EN) for token in TYPE_HINTS)
    return {token for token in query_tokens if token not in service_tokens and len(token) > 1}


def load_alias_history() -> list[dict]:
    path = copilot_dir() / "alias_history.jsonl"
    if not path.exists():
        return []

    rows = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def append_jsonl(file_name: str, row: dict) -> None:
    path = copilot_dir() / file_name
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(row, ensure_ascii=False) + "\n")


def remember_alias(query: str, selected: str, task_type: str) -> None:
    append_jsonl("alias_history.jsonl", {
        "datetime": datetime.now().isoformat(timespec="seconds"),
        "phrase": query,
        "normalized_phrase": normalize_text(query),
        "selected": selected,
        "task_type": task_type,
        "was_correct": True
    })


def alias_history_bonus(normalized_query: str, query_tokens: set, object_id: str) -> tuple[float, list[str]]:
    bonus = 0.0
    reasons = []
    for row in load_alias_history():
        if row.get("selected") != object_id or row.get("was_correct") is False:
            continue

        history_phrase = row.get("normalized_phrase") or normalize_text(row.get("phrase", ""))
        history_tokens = tokenize(history_phrase)
        if history_phrase == normalized_query:
            bonus = max(bonus, 0.15)
            reasons.append("точное совпадение с alias_history")
        elif history_tokens and len(history_tokens & query_tokens) >= max(1, len(query_tokens) // 2):
            bonus = max(bonus, 0.07)
            reasons.append("похожий выбор в alias_history")
    return bonus, reasons


def score_object(query: str, object_id: str, obj: dict) -> dict:
    normalized_query = normalize_text(query)
    query_tokens = tokenize(query)
    required_tokens = important_tokens(query_tokens)
    object_tokens = set(obj.get("search", {}).get("tokens", []))
    object_normalized = obj.get("search", {}).get("normalized", "")
    aliases = {normalize_text(alias) for alias in obj.get("search", {}).get("aliases", [])}
    type_hint = get_type_hint(query_tokens)
    score = 0.0
    reasons = []

    if type_hint:
        object_type = obj.get("type_ru")
        if object_type == type_hint or (type_hint == "Регистр" and object_type.startswith("Регистр")):
            score += 0.40
            reasons.append(f"тип {object_type} совпал с запросом")
        elif type_hint == "Форма" and obj.get("source_paths", {}).get("forms"):
            score += 0.10
            reasons.append("запрос про форму, у объекта есть формы")
        elif object_type != "Форма":
            score -= 0.20
            reasons.append(f"тип {object_type} не совпал с подсказкой {type_hint}")

    if normalized_query in aliases:
        score += 0.35
        reasons.append("точное совпадение с именем/синонимом/alias")

    if required_tokens and required_tokens <= object_tokens:
        score += 0.25
        reasons.append("все важные слова найдены в объекте")
    elif required_tokens:
        overlap = required_tokens & object_tokens
        if overlap:
            score += min(0.20, 0.07 * len(overlap))
            reasons.append("частичное совпадение слов: " + ", ".join(sorted(overlap)))

    if required_tokens and all(token in object_normalized for token in required_tokens):
        score += 0.10
        reasons.append("все важные слова найдены в нормализованном описании")

    history_bonus, history_reasons = alias_history_bonus(normalized_query, query_tokens, object_id)
    score += history_bonus
    reasons.extend(history_reasons)

    if obj.get("is_extension"):
        score += 0.02

    if required_tokens:
        has_content_match = bool(required_tokens & object_tokens) or any(token in object_normalized for token in required_tokens)
        if not has_content_match:
            score = 0.0
            reasons = []

    score = max(0.0, min(1.0, score))
    return {
        "object_id": object_id,
        "score": round(score, 3),
        "type_ru": obj.get("type_ru"),
        "name": obj.get("name"),
        "synonym": obj.get("synonym"),
        "note_path": obj.get("obsidian", {}).get("note_path"),
        "reasons": reasons
    }


def resolve_query(query: str, limit: int = 5) -> dict:
    graph = load_graph()
    candidates = [score_object(query, object_id, obj) for object_id, obj in graph["objects"].items()]
    candidates = [candidate for candidate in candidates if candidate["score"] > 0]
    candidates.sort(key=lambda item: item["score"], reverse=True)
    candidates = candidates[:limit]

    status = "not_found"
    if candidates:
        top_score = candidates[0]["score"]
        second_score = candidates[1]["score"] if len(candidates) > 1 else 0.0
        if len(candidates) == 1 and top_score >= 0.45:
            status = "resolved"
        elif top_score >= 0.90 and top_score - second_score >= 0.15:
            status = "resolved"
        else:
            status = "ambiguous"

    return {
        "query": query,
        "normalized_query": normalize_text(query),
        "status": status,
        "selected": candidates[0]["object_id"] if status == "resolved" else None,
        "candidates": candidates
    }


def print_resolve(result: dict) -> None:
    print(f"Resolve: {result['query']}")
    print(f"Status: {result['status']}")
    for index, candidate in enumerate(result["candidates"], start=1):
        print(f"{index}. {candidate['object_id']} | score={candidate['score']} | {candidate.get('synonym') or ''}")
        for reason in candidate["reasons"][:4]:
            print(f"   - {reason}")


def source_flags(obj: dict) -> list[str]:
    paths = obj.get("source_paths", {})
    flags = []
    for key in ("xml", "object_module", "manager_module", "module"):
        if paths.get(key):
            flags.append(key)
    forms = paths.get("forms", [])
    if forms:
        flags.append(f"forms={len(forms)}")
    return flags


def moc_rows(type_query: str | None, filter_text: str | None, limit: int) -> list[dict]:
    graph = load_graph()
    type_filter = resolve_type_filter(type_query)
    filter_tokens = important_tokens(tokenize(filter_text or ""))
    rows = []

    for object_id, obj in graph["objects"].items():
        object_type = obj.get("type_ru")
        if type_filter:
            if "Форма" in type_filter:
                if not obj.get("source_paths", {}).get("forms"):
                    continue
            elif object_type not in type_filter:
                continue

        object_tokens = set(obj.get("search", {}).get("tokens", []))
        object_normalized = obj.get("search", {}).get("normalized", "")
        if filter_tokens:
            has_match = bool(filter_tokens & object_tokens) or any(token in object_normalized for token in filter_tokens)
            if not has_match:
                continue

        links = obj.get("links", {})
        rows.append({
            "object_id": object_id,
            "type_ru": object_type,
            "name": obj.get("name"),
            "synonym": obj.get("synonym"),
            "note_path": obj.get("obsidian", {}).get("note_path"),
            "source_flags": source_flags(obj),
            "links": {
                "metadata": len(links.get("metadata", [])),
                "code": len(links.get("code", [])),
                "query": len(links.get("query", [])),
                "incoming": len(links.get("incoming", []))
            }
        })

    rows.sort(key=lambda row: (row["type_ru"] or "", row["object_id"]))
    return rows[:limit]


def print_moc(rows: list[dict], type_query: str | None, filter_text: str | None) -> None:
    print(f"MOC type={type_query or '*'} filter={filter_text or '*'} count={len(rows)}")
    for index, row in enumerate(rows, start=1):
        print(f"{index}. {row['object_id']} | {row.get('synonym') or ''}")
        print("   files: " + (", ".join(row["source_flags"]) if row["source_flags"] else "xml-only"))
        links = row["links"]
        print(f"   links: metadata={links['metadata']} code={links['code']} query={links['query']} incoming={links['incoming']}")


def profile_for(task_type: str, stage: str | None = None) -> dict:
    profile = dict(PROFILE_RULES.get(task_type, PROFILE_RULES["bugfix"]))
    if stage and stage in STAGE_OVERRIDES:
        profile.update(STAGE_OVERRIDES[stage])
    return profile


def depth_for(task_type: str, requested_depth: str) -> int:
    if requested_depth == "auto":
        return PROFILE_RULES.get(task_type, PROFILE_RULES["bugfix"])["depth"]
    if requested_depth in DEPTH_LEVELS:
        return DEPTH_LEVELS[requested_depth]
    try:
        return int(requested_depth)
    except (TypeError, ValueError):
        return PROFILE_RULES.get(task_type, PROFILE_RULES["bugfix"])["depth"]


def resolve_depth(task_type: str, requested_depth: str, profile: dict) -> int:
    if requested_depth != "auto":
        return depth_for(task_type, requested_depth)
    return int(profile.get("depth", PROFILE_RULES["bugfix"]["depth"]))


def sort_by_focus(object_ids: list[str], graph: dict, focus_types: tuple[str, ...]) -> list[str]:
    def sort_key(object_id: str):
        object_type = graph["objects"].get(object_id, {}).get("type_ru", "")
        is_focus = object_type in focus_types or any(object_type.startswith(focus_type) for focus_type in focus_types)
        return (0 if is_focus else 1, object_type, object_id)

    return sorted(set(object_ids), key=sort_key)


def format_structure_lines(structure: dict, max_attrs: int = 40, max_ts_attrs: int = 25) -> list[str]:
    """Компактное представление реквизитов/ТЧ/измерений/ресурсов/значений перечислений."""
    if not structure:
        return []
    lines: list[str] = []

    def _attrs_to_inline(attrs: list[dict], cap: int) -> str:
        items = []
        for attr in attrs[:cap]:
            tp = attr.get("type") or "?"
            items.append(f"{attr['name']}:{tp}")
        suffix = f" …(+{len(attrs) - cap})" if len(attrs) > cap else ""
        return ", ".join(items) + suffix

    if structure.get("attributes"):
        lines.append("Реквизиты: " + _attrs_to_inline(structure["attributes"], max_attrs))

    for ts in structure.get("tabular_sections", []):
        head = f"ТЧ.{ts['name']}"
        if ts.get("synonym"):
            head += f" ({ts['synonym']})"
        lines.append(head + ": " + _attrs_to_inline(ts.get("attributes", []), max_ts_attrs))

    if structure.get("dimensions"):
        lines.append("Измерения: " + _attrs_to_inline(structure["dimensions"], max_attrs))
    if structure.get("resources"):
        lines.append("Ресурсы: " + _attrs_to_inline(structure["resources"], max_attrs))
    if structure.get("enum_values"):
        values = [v["name"] for v in structure["enum_values"]]
        cap = 50
        suffix = f" …(+{len(values) - cap})" if len(values) > cap else ""
        lines.append("Значения: " + ", ".join(values[:cap]) + suffix)

    predefined = structure.get("predefined_items") or []
    if predefined:
        items = []
        for item in predefined[:30]:
            label = item.get("name", "?")
            desc = item.get("description") or ""
            code = item.get("code") or ""
            bsl = item.get("bsl_access") or ""
            extra = desc if desc and desc != label else ""
            if code:
                extra = f"{extra}, код {code}".strip(", ")
            piece = label + (f" ({extra})" if extra else "")
            if bsl:
                piece += f" [{bsl}]"
            items.append(piece)
        suffix = f" …(+{len(predefined) - 30})" if len(predefined) > 30 else ""
        lines.append("Предопределённые: " + ", ".join(items) + suffix)

    if structure.get("forms"):
        form_items = []
        for form in structure["forms"]:
            label = form["name"]
            if form.get("form_type"):
                label += f"({form['form_type']})"
            form_items.append(label)
        lines.append("Формы: " + ", ".join(form_items))
        # Внутренности форм: контролы с DataPath
        for form in structure["forms"]:
            internals = form.get("internals", {})
            controls = internals.get("controls", [])
            if controls:
                cap = 20
                items = [f"{c['name']}→{c['data_path']}" for c in controls[:cap]]
                suffix = f" …(+{len(controls) - cap})" if len(controls) > cap else ""
                lines.append(f"  Форма.{form['name']}.элементы: " + ", ".join(items) + suffix)
            cmds = internals.get("commands", [])
            if cmds:
                lines.append(f"  Форма.{form['name']}.команды: " + ", ".join(cmds))
            attrs = internals.get("attributes", [])
            if attrs:
                lines.append(f"  Форма.{form['name']}.реквизиты: " + ", ".join(attrs))

    if structure.get("templates"):
        tpl_labels = []
        for tpl in structure["templates"]:
            label = tpl.get("name", "?")
            q_count = len(tpl.get("skd_queries") or [])
            tpl_labels.append(label + (f"(СКД:{q_count})" if q_count else ""))
        lines.append("Макеты: " + ", ".join(tpl_labels))

    if structure.get("http_endpoints"):
        eps = structure["http_endpoints"][:15]
        items = [
            f"{ep.get('http_method', '?')} {ep.get('template', '/')}"
            for ep in eps
        ]
        suffix = f" …(+{len(structure['http_endpoints']) - 15})" if len(structure["http_endpoints"]) > 15 else ""
        lines.append("HTTP: " + ", ".join(items) + suffix)
        if structure.get("root_url"):
            lines.append(f"RootURL: {structure['root_url']}")

    module_flags = structure.get("module_flags") or {}
    if module_flags:
        enabled = [key for key, value in module_flags.items() if value]
        if enabled:
            lines.append("Модуль: " + ", ".join(enabled))

    if structure.get("commands"):
        lines.append("Команды: " + ", ".join(c["name"] for c in structure["commands"]))

    if structure.get("subsystems"):
        lines.append("Подсистемы: " + ", ".join(structure["subsystems"]))

    if structure.get("register_records"):
        lines.append("Регистраторы (пишет в): " + ", ".join(structure["register_records"]))

    return lines


def object_brief(
    object_id: str,
    obj: dict,
    include_paths: bool = False,
    include_links: tuple[str, ...] = ("metadata", "code", "query", "incoming"),
    max_links: int = 30
) -> list[str]:
    lines = [f"### {object_id}"]
    synonym = obj.get("synonym")
    if synonym:
        lines.append(f"Синоним: {synonym}")

    links = obj.get("links", {})
    if include_paths:
        source_paths = obj.get("source_paths", {})
        lines.append("Файлы исходников:")
        for key in ("xml", "object_module", "manager_module", "module"):
            if source_paths.get(key):
                lines.append(f"- {key}: {source_paths[key]}")
        for form in source_paths.get("forms", []):
            if form.get("form_xml") or form.get("form_module"):
                lines.append(f"- form {form['name']}: {form.get('form_xml') or ''} {form.get('form_module') or ''}".strip())

    for link_type in include_links:
        values = links.get(link_type, [])
        if values:
            lines.append(f"{link_type}: " + ", ".join(values[:max_links]))
            if len(values) > max_links:
                lines.append(f"{link_type}_truncated: +{len(values) - max_links}")
    return lines


def build_context(
    target_id: str,
    task_type: str,
    depth: int,
    budget_tokens: int,
    stage: str | None = None,
) -> tuple[str, dict]:
    graph = load_graph()
    if target_id not in graph["objects"]:
        raise KeyError(f"Объект не найден в graph_index: {target_id}")

    profile = profile_for(task_type, stage)
    target = graph["objects"][target_id]

    sections: list[dict] = []

    def add_section(name: str, kind: str, body_lines: list[str], items: list[str] | None = None,
                    title: str | None = None) -> None:
        body = "\n".join(body_lines).rstrip()
        if not body:
            return
        sections.append({
            "name": name,
            "kind": kind,
            "title": title or name,
            "items": items or [],
            "body": body,
            "tokens": count_tokens(body),
            "lines": body.count("\n") + 1
        })

    # --- target sections ---
    target_paths = target.get("source_paths", {})
    target_links = target.get("links", {})

    add_section(
        "target.header",
        kind="target",
        title="Основной объект",
        items=[target_id],
        body_lines=[
            f"### {target_id}",
            f"Синоним: {target.get('synonym', '')}".rstrip(": "),
            f"Тип: {target.get('type_ru', '')}"
        ]
    )

    src_lines = []
    for key in ("xml", "object_module", "manager_module", "module"):
        if target_paths.get(key):
            src_lines.append(f"- {key}: {target_paths[key]}")
    for form in target_paths.get("forms", []):
        if form.get("form_xml") or form.get("form_module"):
            src_lines.append(f"- form {form['name']}: {form.get('form_xml') or ''} {form.get('form_module') or ''}".strip())
    if src_lines:
        add_section("target.source_paths", kind="paths",
                    title="Файлы исходников основного объекта",
                    items=[target_id], body_lines=["Файлы:"] + src_lines)

    target_structure = target.get("structure", {})
    if profile.get("include_predefined_only"):
        predefined = target_structure.get("predefined_items") or []
        if predefined:
            body_lines = format_structure_lines({"predefined_items": predefined})
            struct_items = [item.get("name", "?") for item in predefined]
            add_section(
                "target.predefined",
                kind="predefined",
                title="Предопределённые элементы",
                items=struct_items,
                body_lines=body_lines,
            )
        else:
            add_section(
                "target.predefined",
                kind="predefined",
                title="Предопределённые элементы",
                items=[],
                body_lines=["Предопределённые элементы: отсутствуют в конфигурации"],
            )
    else:
        structure_lines = format_structure_lines(target_structure)
        if structure_lines:
            struct_items = [a["name"] for a in target_structure.get("attributes", [])]
            struct_items += [f"ТЧ.{ts['name']}" for ts in target_structure.get("tabular_sections", [])]
            struct_items += [d["name"] for d in target_structure.get("dimensions", [])]
            struct_items += [r["name"] for r in target_structure.get("resources", [])]
            struct_items += [f"Предопр.{item['name']}" for item in target_structure.get("predefined_items", [])]
            struct_items += [f"Форма.{f['name']}" for f in target_structure.get("forms", [])]
            struct_items += [f"Макет.{t['name']}" for t in target_structure.get("templates", [])]
            struct_items += [f"Команда.{c['name']}" for c in target_structure.get("commands", [])]
            struct_items += [f"Подсистема.{s}" for s in target_structure.get("subsystems", [])]
            add_section("target.structure", kind="structure",
                        title="Структура основного объекта (реквизиты, ТЧ, измерения, ресурсы)",
                        items=struct_items, body_lines=structure_lines)

    # --- API: сигнатуры процедур/функций модулей объекта ---
    if profile.get("include_target_api", True):
        api_lines: list[str] = []
        api_items: list[str] = []
        for module in target.get("modules", []):
            sigs = module.get("signatures", [])
            if not sigs:
                continue
            kind = module.get("kind") or "module"
            # Сначала экспортные, потом локальные
            exported = [s for s in sigs if s.get("exported")]
            if exported:
                api_lines.append(f"{kind} (экспортные):")
                for s in exported:
                    handler = f" [{s['handler_kind']}]" if s.get("handler") else ""
                    api_lines.append(f"  {s['kind']} {s['name']}({s['params']}){handler}")
                    api_items.append(f"{kind}.{s['name']}")
            local = [s for s in sigs if not s.get("exported")]
            if local:
                cap = 15
                api_lines.append(f"{kind} (локальные, {len(local)} шт.):")
                for s in local[:cap]:
                    handler = f" [{s['handler_kind']}]" if s.get("handler") else ""
                    api_lines.append(f"  {s['kind']} {s['name']}({s['params']}){handler}")
                    api_items.append(f"{kind}.{s['name']}")
                if len(local) > cap:
                    api_lines.append(f"  …(+{len(local) - cap})")
        if api_lines:
            add_section("target.api", kind="api",
                        title="API основного объекта (сигнатуры процедур/функций)",
                        items=api_items, body_lines=api_lines)

    for link_type in profile["target_links"]:
        values = target_links.get(link_type, [])
        if not values:
            continue
        cap = profile["incoming_limit"]
        title_map = {
            "writers": "Документы-регистраторы (writers)",
        }
        body = [f"{link_type}: " + ", ".join(values[:cap])]
        if len(values) > cap:
            body.append(f"{link_type}_truncated: +{len(values) - cap}")
        add_section(
            f"target.links.{link_type}",
            kind=f"links.{link_type}",
            title=title_map.get(link_type, f"Связи основного объекта: {link_type}"),
            items=values[:cap],
            body_lines=body,
        )

    # --- dependencies ---
    if depth >= 1:
        logic_ids: list[str] = []
        data_ids: list[str] = []
        incoming_ids: list[str] = []
        for link_type in profile["dependency_link_types"]:
            for linked_id in target_links.get(link_type, []):
                linked_object = graph["objects"].get(linked_id)
                if not linked_object:
                    continue
                if link_type == "incoming":
                    incoming_ids.append(linked_id)
                elif linked_object.get("type_ru") in LOGIC_TYPES:
                    logic_ids.append(linked_id)
                elif linked_object.get("type_ru") in DATA_TYPES:
                    data_ids.append(linked_id)

        logic_ids = sort_by_focus(logic_ids, graph, profile["focus_types"])[:profile["logic_limit"]]
        data_ids = sort_by_focus(data_ids, graph, profile["focus_types"])[:profile["data_limit"]]
        incoming_ids = sort_by_focus(incoming_ids or target_links.get("incoming", []),
                                     graph, profile["focus_types"])[:profile["incoming_limit"]]

        for logic_id in logic_ids:
            body = object_brief(
                logic_id, graph["objects"][logic_id],
                include_paths=True,
                include_links=("code", "query", "incoming"),
                max_links=profile["incoming_limit"]
            )
            add_section(f"dep.logic:{logic_id}", kind="dep.logic",
                        title=f"Логическая зависимость: {logic_id}",
                        items=[logic_id], body_lines=body)

        if profile["include_incoming_briefs"]:
            for incoming_id in incoming_ids:
                incoming_object = graph["objects"][incoming_id]
                body = object_brief(
                    incoming_id, incoming_object,
                    include_paths=incoming_object.get("type_ru") in LOGIC_TYPES,
                    include_links=("code", "query"),
                    max_links=profile["incoming_limit"]
                )
                add_section(f"dep.incoming:{incoming_id}", kind="dep.incoming",
                            title=f"Входящая зависимость: {incoming_id}",
                            items=[incoming_id], body_lines=body)

        if data_ids:
            add_section("dep.data", kind="dep.data",
                        title="Данные и структуры (имена)",
                        items=data_ids, body_lines=[", ".join(data_ids)])

        data_brief_limit = int(profile.get("data_brief_limit", 0) or 0)
        for data_id in data_ids[:data_brief_limit]:
            data_obj = graph["objects"][data_id]
            body = object_brief(
                data_id, data_obj,
                include_paths=False,
                include_links=("metadata", "incoming"),
                max_links=profile["incoming_limit"]
            )
            structure = format_structure_lines(data_obj.get("structure", {}), max_attrs=20, max_ts_attrs=12)
            if structure:
                body.append("Структура:")
                body.extend(structure)
            add_section(f"dep.data.detail:{data_id}", kind="dep.data.detail",
                        title=f"Структура связанного объекта данных: {data_id}",
                        items=[data_id], body_lines=body)

    # --- assemble text with section markers ---
    header_lines = [
        f"# Контекст задачи: {target_id}",
        f"task_type: {task_type}",
        f"profile: {task_type if task_type in PROFILE_RULES else 'bugfix'}",
        f"stage: {stage or ''}".rstrip(": "),
        f"depth: {depth}",
        ""
    ]
    body_chunks = [
        f"<!-- section:{section['name']} kind={section['kind']} items={len(section['items'])} tokens={section['tokens']} -->\n"
        f"## {section['title']}\n{section['body']}\n<!-- /section:{section['name']} -->"
        for section in sections
    ]
    context_text = "\n".join(header_lines) + "\n\n".join(body_chunks)
    token_count = count_tokens(context_text)
    if token_count > budget_tokens:
        context_text += f"\n\n[INFO] Контекст превышает бюджет: {token_count}/{budget_tokens} токенов (не блокирует)."

    included = {
        "objects": 1 + sum(1 for section in sections if section["kind"] in ("dep.logic", "dep.incoming")),
        "logic_summaries": sum(1 for section in sections if section["kind"] == "dep.logic"),
        "data_refs": sum(len(section["items"]) for section in sections if section["kind"] == "dep.data"),
        "source_files": len([value for value in target_paths.values() if isinstance(value, str) and value]),
        "query_refs": len(target_links.get("query", []))
    }

    request_id = "ctx-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    metadata = {
        "id": request_id,
        "datetime": datetime.now().isoformat(timespec="seconds"),
        "task_type": task_type,
        "target": target_id,
        "stage": stage or None,
        "stage_in_catalog": stage in STAGE_CATALOG if stage else None,
        "stage_profile_applied": bool(stage and stage in STAGE_OVERRIDES),
        "depth": depth,
        "budget_tokens": budget_tokens,
        "actual_tokens": token_count,
        "over_budget": token_count > budget_tokens,
        "included": included,
        "sections": [
            {"name": s["name"], "kind": s["kind"], "items": s["items"],
             "tokens": s["tokens"], "lines": s["lines"]}
            for s in sections
        ],
        "graph_generated_at": graph.get("generated_at")
    }
    return context_text, metadata


def command_resolve(args: argparse.Namespace) -> int:
    result = resolve_query(args.query, args.limit)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_resolve(result)
    return 0 if result["status"] != "not_found" else 1


def command_moc(args: argparse.Namespace) -> int:
    rows = moc_rows(args.type, args.filter, args.limit)
    if args.json:
        print(json.dumps({"type": args.type, "filter": args.filter, "rows": rows}, ensure_ascii=False, indent=2))
    else:
        print_moc(rows, args.type, args.filter)
    return 0 if rows else 1


def command_context(args: argparse.Namespace) -> int:
    resolve_result = resolve_query(args.query, args.limit)
    selected = args.select or resolve_result.get("selected")
    if not selected and args.candidate:
        candidate_index = args.candidate - 1
        if 0 <= candidate_index < len(resolve_result["candidates"]):
            selected = resolve_result["candidates"][candidate_index]["object_id"]
    if not selected and args.accept_first and resolve_result["candidates"]:
        selected = resolve_result["candidates"][0]["object_id"]

    if not selected:
        print_resolve(resolve_result)
        print("\nНеоднозначный объект. Повторите с --select <object_id> или --accept-first.")
        return 2

    stage = (args.stage or "").strip() or None
    profile = profile_for(args.task, stage)
    resolved_depth = resolve_depth(args.task, args.depth, profile)
    context_text, metadata = build_context(
        selected, args.task, resolved_depth, args.budget, stage=stage
    )
    metadata["resolve"] = {
        "query": args.query,
        "status": resolve_result["status"],
        "selected": selected,
        "candidates": resolve_result.get("candidates", []),
        "top_score": (resolve_result.get("candidates", [{}]) or [{}])[0].get("score", 0.0),
        "candidate_count": len(resolve_result.get("candidates", [])),
        "needed_user_clarification": resolve_result["status"] != "resolved"
    }
    metadata["intent"] = (args.intent or "").strip() or None
    stage_in_catalog = metadata.get("stage_in_catalog")
    append_jsonl("context_requests.jsonl", metadata)
    if stage:
        append_jsonl("stages.jsonl", {
            "datetime": metadata["datetime"],
            "context_id": metadata["id"],
            "task_type": args.task,
            "target": selected,
            "stage": stage,
            "intent": metadata["intent"],
            "in_catalog": stage_in_catalog
        })
    if args.select or args.accept_first or args.candidate:
        remember_alias(args.query, selected, args.task)

    if args.json:
        print(json.dumps({"metadata": metadata, "context": context_text}, ensure_ascii=False, indent=2))
    else:
        print(context_text)
        print("\n---")
        print(f"context_id: {metadata['id']}")
        print(f"tokens: {metadata['actual_tokens']} / {metadata['budget_tokens']}"
              + (" [over]" if metadata.get("over_budget") else ""))
        if metadata.get("stage"):
            mark = "OK" if metadata.get("stage_in_catalog") else "NEW (рассмотрите добавить в STAGE_CATALOG)"
            print(f"stage: {metadata['stage']} [{mark}]")
        else:
            print("stage: <не задан> — добавьте --stage <ключ> (см. python scripts/get_context.py stages)")
        print("sections (name | kind | items | tokens):")
        for section in metadata["sections"]:
            print(f"  - {section['name']} | {section['kind']} | items={len(section['items'])} | tok={section['tokens']}")
        print("\nFeedback подсказка:")
        print(f"  python scripts/get_context.py feedback --context-id {metadata['id']} \\\n"
              f"      --result enough --rating 4 \\\n"
              f"      --section target.header=used --section dep.data=unused")
    return 0


SECTION_USAGE_LEVELS = {"used", "partial", "unused"}


def parse_section_usage(values: list[str] | None) -> list[dict]:
    """Принимает 'name=used' или 'name:partial' или 'name'."""
    result = []
    for raw in values or []:
        token = raw.strip()
        if not token:
            continue
        if "=" in token:
            name, level = token.split("=", 1)
        elif ":" in token:
            name, level = token.split(":", 1)
        else:
            name, level = token, "used"
        level = level.strip().lower()
        if level not in SECTION_USAGE_LEVELS:
            level = "used"
        result.append({"name": name.strip(), "usage": level})
    return result


def lookup_context_metadata(context_id: str) -> dict | None:
    path = copilot_dir() / "context_requests.jsonl"
    if not path.exists():
        return None
    found = None
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("id") == context_id:
            found = row
    return found


def command_feedback(args: argparse.Namespace) -> int:
    section_usage = parse_section_usage(args.section)
    metadata = lookup_context_metadata(args.context_id)

    section_stats = {"used": 0, "partial": 0, "unused": 0,
                     "wasted_tokens": 0, "used_tokens": 0, "total_tokens": 0,
                     "unmarked": []}

    if metadata:
        usage_map = {item["name"]: item["usage"] for item in section_usage}
        for section in metadata.get("sections", []):
            tokens = section.get("tokens", 0)
            section_stats["total_tokens"] += tokens
            usage = usage_map.get(section["name"])
            if usage is None:
                section_stats["unmarked"].append(section["name"])
                continue
            section_stats[usage] = section_stats.get(usage, 0) + 1
            if usage == "unused":
                section_stats["wasted_tokens"] += tokens
            elif usage == "used":
                section_stats["used_tokens"] += tokens
            elif usage == "partial":
                section_stats["used_tokens"] += tokens // 2
                section_stats["wasted_tokens"] += tokens - tokens // 2
        if section_stats["total_tokens"]:
            section_stats["waste_ratio"] = round(
                section_stats["wasted_tokens"] / section_stats["total_tokens"], 3)
        else:
            section_stats["waste_ratio"] = 0.0
    else:
        section_stats["context_metadata_missing"] = True

    resolve_meta = metadata.get("resolve", {}) if metadata else {}
    no_target = bool(metadata.get("no_target")) if metadata else args.context_id.startswith("ctx-no-target-")
    row = {
        "datetime": datetime.now().isoformat(timespec="seconds"),
        "context_id": args.context_id,
        "task_type": metadata.get("task_type") if metadata else None,
        "target": metadata.get("target") if metadata else None,
        "stage": metadata.get("stage") if metadata else None,
        "intent": metadata.get("intent") if metadata else None,
        "actual_tokens": metadata.get("actual_tokens") if metadata else None,
        "no_target": no_target,
        "resolve_status": resolve_meta.get("status"),
        "resolve_top_score": resolve_meta.get("top_score"),
        "resolve_candidate_count": resolve_meta.get("candidate_count"),
        "needed_user_clarification": resolve_meta.get("needed_user_clarification"),
        "result": args.result,
        "rating": args.rating,
        "was_excessive": args.result == "excessive",
        "was_insufficient": args.result == "insufficient",
        "was_wrong": args.result == "wrong",
        "missing": args.missing or [],
        "excess": args.excess or [],
        "section_usage": section_usage,
        "section_stats": section_stats,
        "extra_searches": args.extra_searches,
        "extra_files_read": args.extra_files_read,
        "extra_mcp_calls": args.extra_mcp_calls,
        "lost_time_minutes": args.lost_time_minutes,
        "notes": args.notes or ""
    }
    append_jsonl("context_feedback.jsonl", row)
    print(json.dumps(row, ensure_ascii=False, indent=2))
    return 0


def command_report(args: argparse.Namespace) -> int:
    feedback_path = copilot_dir() / "context_feedback.jsonl"
    if not feedback_path.exists():
        print("Нет записей context_feedback.jsonl")
        return 0

    rows = []
    for line in feedback_path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    if not rows:
        print("context_feedback.jsonl пуст")
        return 0

    # 1) Распределение исходов
    by_result: dict[str, int] = {}
    by_task: dict[str, dict[str, int]] = {}
    waste_ratios: list[float] = []
    total_wasted = 0
    total_used = 0
    total_tokens = 0

    # 2) Статистика по типам секций (kind агрегируем через name prefix)
    section_kind_stats: dict[str, dict] = {}

    # 3) Статистика по этапам/паттернам задач
    by_stage: dict[str, dict] = {}
    rating_counts: dict[str, int] = {}
    ratings: list[int] = []
    resolve_status_counts: dict[str, int] = {}
    metadata_missing_feedback = 0
    no_target_feedback = 0
    feedback_with_unmarked_sections = 0
    unmarked_sections_total = 0
    needed_user_clarification = 0
    low_confidence_feedback = 0
    extra_searches_total = 0
    extra_files_total = 0
    extra_mcp_total = 0

    for row in rows:
        result = row.get("result", "?")
        by_result[result] = by_result.get(result, 0) + 1
        task = row.get("task_type") or "?"
        by_task.setdefault(task, {})
        by_task[task][result] = by_task[task].get(result, 0) + 1

        rating = row.get("rating")
        if isinstance(rating, int):
            ratings.append(rating)
            rating_counts[str(rating)] = rating_counts.get(str(rating), 0) + 1

        if row.get("no_target") or str(row.get("context_id", "")).startswith("ctx-no-target-"):
            no_target_feedback += 1
        if row.get("needed_user_clarification"):
            needed_user_clarification += 1
        resolve_status = row.get("resolve_status") or "?"
        resolve_status_counts[resolve_status] = resolve_status_counts.get(resolve_status, 0) + 1
        top_score = row.get("resolve_top_score")
        if isinstance(top_score, (int, float)) and top_score < 0.20:
            low_confidence_feedback += 1

        extra_searches_total += row.get("extra_searches", 0) or 0
        extra_files_total += row.get("extra_files_read", 0) or 0
        extra_mcp_total += row.get("extra_mcp_calls", 0) or 0

        stats = row.get("section_stats") or {}
        if stats.get("context_metadata_missing"):
            metadata_missing_feedback += 1
        unmarked = stats.get("unmarked") or []
        if unmarked:
            feedback_with_unmarked_sections += 1
            unmarked_sections_total += len(unmarked)
        if "waste_ratio" in stats:
            waste_ratios.append(stats["waste_ratio"])
            total_wasted += stats.get("wasted_tokens", 0)
            total_used += stats.get("used_tokens", 0)
            total_tokens += stats.get("total_tokens", 0)

        for usage_row in row.get("section_usage", []):
            name = usage_row["name"]
            kind = name.split(":", 1)[0]
            bucket = section_kind_stats.setdefault(
                kind, {"used": 0, "partial": 0, "unused": 0, "total": 0})
            bucket["total"] += 1
            bucket[usage_row["usage"]] = bucket.get(usage_row["usage"], 0) + 1

        stage = row.get("stage")
        if stage:
            stage_bucket = by_stage.setdefault(stage, {
                "count": 0, "ratings": [], "waste_ratios": [],
                "extra_searches": 0, "extra_files_read": 0, "extra_mcp_calls": 0,
                "results": {}, "task_types": {}, "tokens_total": 0
            })
            stage_bucket["count"] += 1
            if isinstance(row.get("rating"), int):
                stage_bucket["ratings"].append(row["rating"])
            if "waste_ratio" in stats:
                stage_bucket["waste_ratios"].append(stats["waste_ratio"])
                stage_bucket["tokens_total"] += stats.get("total_tokens", 0)
            stage_bucket["extra_searches"] += row.get("extra_searches", 0) or 0
            stage_bucket["extra_files_read"] += row.get("extra_files_read", 0) or 0
            stage_bucket["extra_mcp_calls"] += row.get("extra_mcp_calls", 0) or 0
            stage_bucket["results"][result] = stage_bucket["results"].get(result, 0) + 1
            stage_bucket["task_types"][task] = stage_bucket["task_types"].get(task, 0) + 1

    summary = {
        "feedback_count": len(rows),
        "by_result": by_result,
        "result_rates": {
            key: round(value / len(rows), 3) if rows else 0.0
            for key, value in sorted(by_result.items())
        },
        "by_task_type": by_task,
        "ratings": {
            "avg": round(sum(ratings) / len(ratings), 2) if ratings else None,
            "distribution": rating_counts,
        },
        "tokens": {
            "total": total_tokens,
            "used": total_used,
            "wasted": total_wasted,
            "used_ratio": round(total_used / total_tokens, 3) if total_tokens else None,
            "wasted_ratio": round(total_wasted / total_tokens, 3) if total_tokens else None,
            "waste_ratio_avg": round(sum(waste_ratios) / len(waste_ratios), 3) if waste_ratios else None
        },
        "quality": {
            "metadata_missing_feedback": metadata_missing_feedback,
            "no_target_feedback": no_target_feedback,
            "feedback_with_unmarked_sections": feedback_with_unmarked_sections,
            "unmarked_sections_total": unmarked_sections_total,
            "needed_user_clarification": needed_user_clarification,
            "low_confidence_feedback": low_confidence_feedback,
            "extra_actions_total": extra_searches_total + extra_files_total + extra_mcp_total,
            "extra_actions_avg": round((extra_searches_total + extra_files_total + extra_mcp_total) / len(rows), 2) if rows else 0.0,
            "extra_searches": extra_searches_total,
            "extra_files_read": extra_files_total,
            "extra_mcp_calls": extra_mcp_total,
        },
        "resolve": {
            "by_status": resolve_status_counts,
            "low_confidence_threshold": 0.20,
        },
        "section_kinds": {
            kind: {
                **stats,
                "unused_ratio": round(stats["unused"] / stats["total"], 3) if stats["total"] else 0.0
            }
            for kind, stats in sorted(section_kind_stats.items())
        }
    }

    # Топ кандидатов на «выкидывание»: kind с высоким unused_ratio и заметной выборкой
    candidates_to_trim = sorted(
        [
            {"kind": kind, **stats}
            for kind, stats in summary["section_kinds"].items()
            if stats["total"] >= 3 and stats["unused_ratio"] >= 0.5
        ],
        key=lambda item: item["unused_ratio"],
        reverse=True
    )
    summary["trim_candidates"] = candidates_to_trim

    # Сводка по этапам/паттернам задач
    stages_summary = {}
    for stage_name, bucket in by_stage.items():
        ratings = bucket["ratings"]
        wastes = bucket["waste_ratios"]
        stages_summary[stage_name] = {
            "count": bucket["count"],
            "avg_rating": round(sum(ratings) / len(ratings), 2) if ratings else None,
            "avg_waste_ratio": round(sum(wastes) / len(wastes), 3) if wastes else None,
            "tokens_total": bucket["tokens_total"],
            "extra_searches": bucket["extra_searches"],
            "extra_files_read": bucket["extra_files_read"],
            "extra_mcp_calls": bucket["extra_mcp_calls"],
            "results": bucket["results"],
            "task_types": bucket["task_types"]
        }
    summary["stages"] = dict(sorted(stages_summary.items(),
                                    key=lambda kv: kv[1]["count"], reverse=True))

    # Этапы-проблемы: низкий rating ИЛИ высокий waste ИЛИ много extra-работы
    problem_stages = []
    for stage_name, info in stages_summary.items():
        if info["count"] < 2:
            continue
        signals = []
        if info["avg_rating"] is not None and info["avg_rating"] < 3:
            signals.append(f"rating={info['avg_rating']}")
        if info["avg_waste_ratio"] is not None and info["avg_waste_ratio"] >= 0.4:
            signals.append(f"waste={info['avg_waste_ratio']}")
        per_call_extra = (info["extra_searches"] + info["extra_files_read"] + info["extra_mcp_calls"]) / info["count"]
        if per_call_extra >= 2:
            signals.append(f"extra/call={round(per_call_extra, 1)}")
        if signals:
            problem_stages.append({"stage": stage_name, "count": info["count"], "signals": signals})
    summary["problem_stages"] = sorted(problem_stages, key=lambda item: item["count"], reverse=True)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Compact context helper for 1C + Obsidian graph")
    subparsers = parser.add_subparsers(dest="command", required=True)

    resolve_parser = subparsers.add_parser("resolve", help="Найти точный объект по неточному запросу")
    resolve_parser.add_argument("query")
    resolve_parser.add_argument("--limit", type=int, default=5)
    resolve_parser.add_argument("--json", action="store_true")
    resolve_parser.set_defaults(func=command_resolve)

    moc_parser = subparsers.add_parser("moc", help="Компактный список объектов для agent-assisted resolve")
    moc_parser.add_argument("--type")
    moc_parser.add_argument("--filter")
    moc_parser.add_argument("--limit", type=int, default=40)
    moc_parser.add_argument("--json", action="store_true")
    moc_parser.set_defaults(func=command_moc)

    context_parser = subparsers.add_parser("context", help="Сформировать компактный контекст задачи")
    context_parser.add_argument("query")
    context_parser.add_argument("--task", default="bugfix")
    context_parser.add_argument("--depth", default="auto")
    context_parser.add_argument("--budget", type=int, default=3000)
    context_parser.add_argument("--limit", type=int, default=5)
    context_parser.add_argument("--select")
    context_parser.add_argument("--candidate", type=int, help="Выбрать N-го кандидата из resolve")
    context_parser.add_argument("--accept-first", action="store_true")
    context_parser.add_argument("--stage",
                                help="Короткий лейбл этапа/паттерна задачи (3-5 слов), напр. 'проверить ТЧ документа'")
    context_parser.add_argument("--intent",
                                help="Развёрнутая фраза цели запроса (свободный текст, для последующего кластеринга)")
    context_parser.add_argument("--json", action="store_true")
    context_parser.set_defaults(func=command_context)

    feedback_parser = subparsers.add_parser("feedback", help="Записать оценку качества полученного контекста")
    feedback_parser.add_argument("--context-id", required=True)
    feedback_parser.add_argument("--result", required=True, choices=["perfect", "enough", "excessive", "insufficient", "wrong"])
    feedback_parser.add_argument("--rating", type=int, choices=range(1, 6), required=True)
    feedback_parser.add_argument("--missing", action="append")
    feedback_parser.add_argument("--excess", action="append")
    feedback_parser.add_argument("--section", action="append",
                                 help="Оценка секции: name=used|partial|unused (повторяемо)")
    feedback_parser.add_argument("--extra-searches", type=int, default=0)
    feedback_parser.add_argument("--extra-files-read", type=int, default=0)
    feedback_parser.add_argument("--extra-mcp-calls", type=int, default=0)
    feedback_parser.add_argument("--lost-time-minutes", type=int, default=0)
    feedback_parser.add_argument("--notes")
    feedback_parser.set_defaults(func=command_feedback)

    report_parser = subparsers.add_parser("report", help="Краткая статистика context_feedback")
    report_parser.set_defaults(func=command_report)

    stages_parser = subparsers.add_parser("stages", help="Каталог типовых stage-лейблов для --stage")
    stages_parser.set_defaults(func=lambda a: (print("Доступные stage-лейблы (используйте --stage <ключ>):\n"
                                                     + list_stage_catalog()
                                                     + "\n\nМожно ввести свой лейбл — он попадёт в stages.jsonl с in_catalog=false."),
                                               0)[1])

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())