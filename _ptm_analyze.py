# -*- coding: utf-8 -*-
"""
PTM Static Analyzer — проверка BSL-кода на антипаттерны из СписокИсправлений.
Работает без Java/BSL LS — чистый Python grep+анализ.

Проверяет:
  Кат.1: ТекущаяДата() → ТекущаяДатаСеанса()
  Кат.2: ПоказатьВопрос() → ВопросАсинх()
  Кат.3: Сообщить() без привязки к полям
  Кат.4: ЭтаФорма → ЭтотОбъект
  Кат.5: ИмяПользователя() + НайтиПоНаименованию — ненадёжный поиск
"""

import pathlib
import re
import sys

# Корень конфигурации
CONFIG_ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация")

# Исключаем БПО-модули (начинаются с _)
def is_ptm_path(path: pathlib.Path) -> bool:
    """Проверяет что файл принадлежит PTM (не БПО/демо)"""
    parts = path.parts
    for part in parts:
        if part.startswith("_") or part.startswith("Демо") or part.startswith("_Демо"):
            return False
    return True

# Категории проверок
CHECKS = [
    {
        "id": 1,
        "name": "ТекущаяДата() → ТекущаяДатаСеанса()",
        "pattern": re.compile(r'\bТекущаяДата\s*\(\s*\)', re.IGNORECASE),
        "severity": "ВЫСОКИЙ",
        "description": "Устаревший метод. Возвращает время ОС сервера, а не сеанса.",
    },
    {
        "id": 2,
        "name": "ПоказатьВопрос() → ВопросАсинх()",
        "pattern": re.compile(r'\bПоказатьВопрос\s*\(', re.IGNORECASE),
        "severity": "СРЕДНИЙ",
        "description": "Устаревший паттерн с колбэком. Использовать Ждать ВопросАсинх().",
    },
    {
        "id": 3,
        "name": "Сообщить() без привязки к полям",
        "pattern": re.compile(r'\bСообщить\s*\(', re.IGNORECASE),
        "severity": "НИЗКИЙ", 
        "description": "Не привязывает сообщение к полю формы. Использовать СообщениеПользователю.",
    },
    {
        "id": 4,
        "name": "ЭтаФорма → ЭтотОбъект",
        "pattern": re.compile(r'\bЭтаФорма\b', re.IGNORECASE),
        "severity": "НИЗКИЙ",
        "description": "Устаревшее свойство. Использовать ЭтотОбъект.",
        "ptm_only": True,  # В БПО тоже есть, но трогать не надо
    },
    {
        "id": 5,
        "name": "ИмяПользователя() + НайтиПоНаименованию — ненадёжный поиск",
        "pattern": re.compile(r'НайтиПоНаименованию\s*\(\s*ИмяПользователя\s*\(\s*\)', re.IGNORECASE),
        "severity": "ВЫСОКИЙ",
        "description": "Поиск по наименованию ненадёжен. Нужен справочник Пользователи с привязкой к ПользователиИБ.",
    },
    {
        "id": "2b",
        "name": "Предупреждение() → ПредупреждениеАсинх()",
        "pattern": re.compile(r'(?<!\w)Предупреждение\s*\(', re.IGNORECASE),
        "severity": "СРЕДНИЙ",
        "description": "Модальный вызов. Использовать ПредупреждениеАсинх().",
    },
    {
        "id": "2c",
        "name": "Вопрос() → ВопросАсинх()",
        "pattern": re.compile(r'(?<!\w)Вопрос\s*\(', re.IGNORECASE),
        "severity": "СРЕДНИЙ",
        "description": "Модальный вызов. Использовать ВопросАсинх().",
    },
    {
        "id": "1b",
        "name": "Найти() → СтрНайти()",
        "pattern": re.compile(r'(?<!\w)Найти\s*\(', re.IGNORECASE),
        "severity": "НИЗКИЙ",
        "description": "Устаревший метод строк. Использовать СтрНайти().",
        "skip_bpo": True,  # Много вхождений в БПО
    },
]


def scan_file(filepath: pathlib.Path, checks, ptm_only_filter=False):
    """Сканирует BSL-файл на антипаттерны"""
    try:
        content = filepath.read_text(encoding="utf-8-sig")
    except Exception:
        try:
            content = filepath.read_text(encoding="cp1251")
        except Exception:
            return []
    
    lines = content.split("\n")
    findings = []
    
    for check in checks:
        if check.get("ptm_only") and not ptm_only_filter:
            continue
        if check.get("skip_bpo") and not ptm_only_filter:
            continue
            
        for line_num, line in enumerate(lines, 1):
            # Пропускаем комментарии
            stripped = line.strip()
            if stripped.startswith("//"):
                continue
            
            if check["pattern"].search(line):
                findings.append({
                    "check_id": check["id"],
                    "check_name": check["name"],
                    "severity": check["severity"],
                    "file": filepath,
                    "line": line_num,
                    "text": stripped[:100],
                })
    
    return findings


def get_relative_path(filepath: pathlib.Path) -> str:
    """Получить путь относительно Конфигурация/"""
    try:
        return str(filepath.relative_to(CONFIG_ROOT))
    except ValueError:
        return str(filepath)


def main():
    print("=" * 70)
    print("  PTM STATIC ANALYZER v0.1")
    print("  Проверка BSL-кода на антипаттерны из СписокИсправлений")
    print("=" * 70)
    print()
    
    if not CONFIG_ROOT.exists():
        print(f"ОШИБКА: Папка не найдена: {CONFIG_ROOT}")
        sys.exit(1)
    
    # Собираем все BSL файлы
    all_bsl = list(CONFIG_ROOT.rglob("*.bsl"))
    ptm_bsl = [f for f in all_bsl if is_ptm_path(f)]
    
    print(f"  Всего BSL-файлов: {len(all_bsl)}")
    print(f"  PTM-модулей (без БПО): {len(ptm_bsl)}")
    print()
    
    # Сканируем  
    all_findings = []
    
    # PTM-модули — все проверки
    for filepath in ptm_bsl:
        findings = scan_file(filepath, CHECKS, ptm_only_filter=True)
        all_findings.extend(findings)
    
    # Все модули — только основные проверки (без ptm_only)  
    for filepath in all_bsl:
        if filepath not in ptm_bsl:
            basic_checks = [c for c in CHECKS if not c.get("ptm_only") and not c.get("skip_bpo")]
            findings = scan_file(filepath, basic_checks, ptm_only_filter=False)
            all_findings.extend(findings)
    
    # === ОТЧЁТ ===
    
    # Группировка по категориям
    categories = {}
    for f in all_findings:
        cid = f["check_id"]
        if cid not in categories:
            categories[cid] = {
                "name": f["check_name"],
                "severity": f["severity"],
                "findings": [],
            }
        categories[cid]["findings"].append(f)
    
    # Только PTM-находки (для основного отчёта)
    ptm_findings = [f for f in all_findings if is_ptm_path(f["file"])]
    ptm_categories = {}
    for f in ptm_findings:
        cid = f["check_id"]
        if cid not in ptm_categories:
            ptm_categories[cid] = {
                "name": f["check_name"],
                "severity": f["severity"],
                "findings": [],
            }
        ptm_categories[cid]["findings"].append(f)
    
    
    # Вывод по категориям (только PTM)
    print("=" * 70)
    print("  РЕЗУЛЬТАТЫ: PTM-модули (ваш код)")
    print("=" * 70)
    print()
    
    severity_order = {"ВЫСОКИЙ": 0, "СРЕДНИЙ": 1, "НИЗКИЙ": 2}
    
    total_ptm = 0
    total_high = 0
    total_medium = 0
    total_low = 0
    
    for cid in sorted(ptm_categories.keys(), key=lambda x: severity_order.get(ptm_categories[x]["severity"], 9)):
        cat = ptm_categories[cid]
        count = len(cat["findings"])
        total_ptm += count
        
        if cat["severity"] == "ВЫСОКИЙ":
            total_high += count
        elif cat["severity"] == "СРЕДНИЙ":
            total_medium += count
        else:
            total_low += count
        
        severity_icon = {"ВЫСОКИЙ": "🔴", "СРЕДНИЙ": "🟡", "НИЗКИЙ": "🔵"}.get(cat["severity"], "⚪")
        print(f"  {severity_icon} Категория {cid}: {cat['name']}")
        print(f"     Серьёзность: {cat['severity']} | Найдено: {count}")
        print()
        
        # Показываем детали (максимум 15 на категорию)
        shown = 0
        for f in cat["findings"]:
            if shown >= 15:
                remaining = count - shown
                print(f"     ... и ещё {remaining} вхождений")
                break
            rel_path = get_relative_path(f["file"])
            print(f"     [{cid}.{shown+1}] {rel_path}:{f['line']}")
            print(f"           {f['text']}")
            shown += 1
        print()
    
    if not ptm_categories:
        print("  ✅ Проблем не найдено в PTM-модулях!")
        print()
    
    # Итого
    print("=" * 70)
    print("  ИТОГО (PTM-код)")
    print("=" * 70)
    print(f"  🔴 ВЫСОКИЙ: {total_high} проблем")
    print(f"  🟡 СРЕДНИЙ: {total_medium} проблем")
    print(f"  🔵 НИЗКИЙ:  {total_low} проблем")
    print(f"  ─────────────────────")
    print(f"  ВСЕГО: {total_ptm} проблем в PTM-коде")
    print()
    
    # Сводка по всей конфигурации (включая БПО)  
    if len(all_findings) > total_ptm:
        bpo_count = len(all_findings) - total_ptm
        print(f"  ℹ️  В БПО-модулях (не трогаем): дополнительно {bpo_count} вхождений")
        print()
    
    # Сравнение с СписокИсправлений
    print("=" * 70)
    print("  СРАВНЕНИЕ С СписокИсправлений")
    print("=" * 70)
    print()
    
    expected = {
        1: {"name": "ТекущаяДата()", "expected": 7},
        2: {"name": "ПоказатьВопрос()", "expected": 18},
        3: {"name": "Сообщить()", "expected": 10},
        4: {"name": "ЭтаФорма (PTM)", "expected": 3},
        5: {"name": "ИмяПользователя()", "expected": 1},
    }
    
    for cid, exp in expected.items():
        found = len(ptm_categories.get(cid, {}).get("findings", []))
        ok = "✅" if found == exp["expected"] else ("⚠️" if found > 0 else "❌")
        print(f"  {ok} Кат.{cid} {exp['name']}: найдено {found} (ожидалось ~{exp['expected']})")
    
    print()
    print("=" * 70)
    
    # Exit code
    if total_high > 0:
        print("  РЕЗУЛЬТАТ: ЕСТЬ КРИТИЧЕСКИЕ ПРОБЛЕМЫ")
        print("=" * 70)
        sys.exit(1)
    elif total_ptm > 0:
        print("  РЕЗУЛЬТАТ: ЕСТЬ ПРЕДУПРЕЖДЕНИЯ")
        print("=" * 70)
        sys.exit(0)
    else:
        print("  РЕЗУЛЬТАТ: ВСЁ ЧИСТО")
        print("=" * 70)
        sys.exit(0)


if __name__ == "__main__":
    main()
