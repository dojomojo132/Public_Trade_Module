# -*- coding: utf-8 -*-
"""
Статический анализатор BSL для проекта AdminReport.

Запуск:
    python _ptm_analyze.py                     # все файлы
    python _ptm_analyze.py Конфигурация/CommonModules/ВВП.bsl  # один файл
    python _ptm_analyze.py --critical-only     # только критические ошибки
    python _ptm_analyze.py --summary           # только итоговая статистика

Возвращает код 0 если нет критических ошибок, 1 если есть.
"""

import pathlib
import re
import sys
from dataclasses import dataclass, field
from typing import List, Optional

ROOT = pathlib.Path(__file__).resolve().parent
CONFIG_DIR = ROOT / "Конфигурация"

# ═══════════════════════════════════════════════════════════════════════════════
# Правила анализа
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Issue:
    level: str        # CRITICAL | WARN | INFO
    file: str
    line: int
    message: str

    def __str__(self):
        icon = {"CRITICAL": "❌", "WARN": "⚠️", "INFO": "ℹ️"}.get(self.level, "?")
        return f"  {icon} [{self.level}] {self.file}:{self.line} — {self.message}"


# Антипаттерны: (паттерн, сообщение, уровень)
ANTIPATTERNS = [
    # Устаревшие конструкторы
    (r'\bНовая\s+Структура\b',        "Использовать 'Новый Структура' вместо 'Новая Структура'",      "CRITICAL"),
    (r'\bНовое\s+Соответствие\b',     "Использовать 'Новый Соответствие' вместо 'Новое Соответствие'","CRITICAL"),
    (r'\bНовый\s+Массив\b',           "Использовать 'Новый Массив' — ок, но проверь синтаксис",       "INFO"),
    # Устаревшие методы
    (r'\bЗначениеВСтроку\s*\(',       "Использовать 'ЗначениеВСтрокуВнутр()'",                       "CRITICAL"),
    (r'\bСтрокаВЗначение\s*\(',       "Использовать 'ЗначениеИзСтрокиВнутр()'",                      "CRITICAL"),
    (r'\bТекущаяДата\s*\(',           "Использовать 'ТекущаяДатаСеанса()'",                           "CRITICAL"),
    (r'\bНайти\s*\(',                 "Использовать 'СтрНайти()'",                                    "WARN"),
    (r'\bЭтаФорма\b',                 "Использовать 'ЭтотОбъект'",                                    "WARN"),
    # Модальные вызовы
    (r'\bВопрос\s*\(',                "Использовать 'ВопросАсинх()'",                                 "CRITICAL"),
    (r'\bПредупреждение\s*\(',        "Использовать 'ПредупреждениеАсинх()'",                         "CRITICAL"),
    (r'\bОткрытьФормуМодально\s*\(',  "Использовать 'ОткрытьФормуАсинх()'",                           "CRITICAL"),
    # Безопасность
    (r'\bВыполнить\s*\(',             "Возможная инъекция кода через Выполнить()",                     "WARN"),
    (r'\bВычислить\s*\(',             "Возможная инъекция через Вычислить()",                          "WARN"),
    (r'\bУстановитьПривилегированныйРежим\s*\(\s*Истина',
                                      "Привилегированный режим — требует обоснования",                  "WARN"),
    # Запросы в циклах (упрощённо)
    (r'(Пока|Для)\s+.+?\s+Цикл.*Новый Запрос',
                                      "Запрос внутри цикла — перенести запрос за пределы цикла",       "CRITICAL"),
    # Сообщить без привязки
    (r'\bСообщить\s*\(',              "Использовать 'СообщениеПользователю' с привязкой к полю",       "INFO"),
]

# Паттерны для проверки транзакций
TRANSACTION_PATTERNS = {
    "begin":    re.compile(r'\bНачатьТранзакцию\s*\('),
    "commit":   re.compile(r'\bЗафиксироватьТранзакцию\s*\('),
    "rollback": re.compile(r'\bОтменитьТранзакцию\s*\('),
    "try":      re.compile(r'\bПопытка\b'),
    "except":   re.compile(r'\bИсключение\b'),
}


def analyze_file(bsl_path: pathlib.Path) -> List[Issue]:
    issues: List[Issue] = []
    try:
        text = bsl_path.read_text(encoding="utf-8-sig", errors="replace")
    except Exception as e:
        issues.append(Issue("WARN", str(bsl_path.relative_to(ROOT)), 0, f"Не удалось прочитать файл: {e}"))
        return issues

    lines = text.splitlines()
    rel = str(bsl_path.relative_to(ROOT))

    # ── Антипаттерны построчно ─────────────────────────────────────────────
    for lineno, line in enumerate(lines, 1):
        stripped = line.strip()
        # Пропускаем комментарии
        if stripped.startswith("//"):
            continue
        # Убираем inline комментарии
        code = re.sub(r'//.*$', '', line)

        for pattern, message, level in ANTIPATTERNS:
            if re.search(pattern, code, re.IGNORECASE):
                issues.append(Issue(level, rel, lineno, message))

    # ── Транзакции: НачатьТранзакцию без Попытка/Отменить ─────────────────
    full = "\n".join(lines)
    if TRANSACTION_PATTERNS["begin"].search(full):
        has_try      = bool(TRANSACTION_PATTERNS["try"].search(full))
        has_rollback = bool(TRANSACTION_PATTERNS["rollback"].search(full))
        if not has_try:
            issues.append(Issue("CRITICAL", rel, 0, "НачатьТранзакцию() без блока Попытка/Исключение"))
        if not has_rollback:
            issues.append(Issue("CRITICAL", rel, 0, "НачатьТранзакцию() без ОтменитьТранзакцию() в блоке Исключение"))

    # ── Директивы в форм-модуле ────────────────────────────────────────────
    if "Forms" in str(bsl_path) or "Module.bsl" in str(bsl_path):
        proc_func_pattern = re.compile(
            r'^\s*(Процедура|Функция|Procedure|Function)\s+\w+', re.IGNORECASE | re.MULTILINE
        )
        directive_pattern = re.compile(
            r'^\s*&(НаКлиенте|НаСервере|НаСервереБезКонтекста|НаКлиентеНаСервереБезКонтекста)',
            re.IGNORECASE | re.MULTILINE
        )
        procs = list(proc_func_pattern.finditer(full))
        directives = set(m.start() for m in directive_pattern.finditer(full))
        # Считаем процедуры без директивы (проверяем предыдущие ~3 строки)
        missing_directive = 0
        for m in procs:
            prev_pos = max(0, m.start() - 200)
            prev_block = full[prev_pos:m.start()]
            if not re.search(r'&(НаКлиенте|НаСервере|НаСервереБезКонтекста|НаКлиентеНаСервереБезКонтекста)', prev_block, re.IGNORECASE):
                missing_directive += 1
        if missing_directive > 0:
            lineno_approx = full[:procs[0].start()].count("\n") + 1 if procs else 0
            issues.append(Issue("WARN", rel, lineno_approx,
                f"{missing_directive} процедур(а/ы) без директивы (&НаКлиенте/&НаСервере)"))

    return issues


def collect_bsl_files(root: pathlib.Path) -> List[pathlib.Path]:
    return sorted(root.rglob("*.bsl"))


def main():
    args = sys.argv[1:]
    critical_only  = "--critical-only" in args
    summary_only   = "--summary" in args
    args = [a for a in args if not a.startswith("--")]

    if args:
        files = [pathlib.Path(a).resolve() for a in args if pathlib.Path(a).exists()]
        if not files:
            print(f"Файл(ы) не найдены: {args}")
            sys.exit(1)
    else:
        files = collect_bsl_files(CONFIG_DIR)

    if not files:
        print("BSL-файлы не найдены.")
        sys.exit(0)

    all_issues: List[Issue] = []
    for f in files:
        all_issues.extend(analyze_file(f))

    if critical_only:
        all_issues = [i for i in all_issues if i.level == "CRITICAL"]

    # ── Вывод ──────────────────────────────────────────────────────────────
    by_file: dict = {}
    for issue in all_issues:
        by_file.setdefault(issue.file, []).append(issue)

    if not summary_only:
        for filepath, issues in sorted(by_file.items()):
            print(f"\n📄 {filepath}")
            for issue in sorted(issues, key=lambda x: x.line):
                print(str(issue))

    # ── Статистика ─────────────────────────────────────────────────────────
    critical = sum(1 for i in all_issues if i.level == "CRITICAL")
    warnings = sum(1 for i in all_issues if i.level == "WARN")
    infos    = sum(1 for i in all_issues if i.level == "INFO")

    print(f"\n{'='*60}")
    print(f"Проверено файлов: {len(files)}")
    print(f"❌ Критических: {critical}")
    print(f"⚠️  Предупреждений: {warnings}")
    print(f"ℹ️  Замечаний: {infos}")

    if critical == 0 and warnings == 0:
        print("✅ Нарушений не найдено")
    elif critical == 0:
        print("⚠️  Есть предупреждения — рекомендуется исправить")
    else:
        print("❌ Есть критические ошибки — исправить перед деплоем!")

    sys.exit(1 if critical > 0 else 0)


if __name__ == "__main__":
    main()
