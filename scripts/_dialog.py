# -*- coding: utf-8 -*-
"""
Интерактивный диалог для Copilot-агентов PTM.
Показывает Quick Pick меню в терминале, блокирует выполнение до ответа пользователя.

Использование:
    python scripts/_dialog.py 1   # ДИАЛОГ 1 (после мониторинга без ошибок)
    python scripts/_dialog.py 2   # ДИАЛОГ 2 (по умолчанию)
    python scripts/_dialog.py 3   # ДИАЛОГ 3 (стартовый)

    # Кастомный диалог через JSON:
    python scripts/_dialog.py --json '{"header":"my_id","question":"Текст?","options":[{"label":"Да"},{"label":"Нет","recommended":true}],"allowFreeformInput":true}'

    # Кастомный диалог через аргументы:
    python scripts/_dialog.py --title "Заголовок" --options "Вариант 1" "Вариант 2"

Формат вывода:
    SELECTED:<header>:<номер>    — выбран вариант (1-based)
    CUSTOM:<header>:<текст>      — введён свободный текст
    CANCELLED                    — отмена
"""

import sys
import json
import argparse
from InquirerPy import inquirer
from InquirerPy.separator import Separator


# ─── Предустановленные диалоги в формате questions[] ───

DIALOGS = {
    "1": {
        "header": "post_monitoring",
        "question": "Обновите страницу (Ctrl+Shift+R) и проверьте результат. Как результат?",
        "options": [
            {"label": "Всё работает корректно ✅", "recommended": True},
            {"label": "Есть ошибка, опишу ниже ❌"},
            {"label": "🔄 Перезапустить сервер"},
            {"label": "🔴 Остановить сессию"},
        ],
        "allowFreeformInput": True,
    },
    "2": {
        "header": "next_action",
        "question": "Что дальше?",
        "options": [
            {"label": "💾 Закоммитить → git commit"},
            {"label": "📝 Новый запрос → описать задачу"},
            {"label": "🔍 Мониторинг → проверить журналы"},
            {"label": "🔴 Остановить сессию"},
        ],
        "allowFreeformInput": True,
    },
    "3": {
        "header": "start_action",
        "question": "Что дальше?",
        "options": [
            {"label": "🔍 Мониторинг → проверить журнал ИБ"},
            {"label": "🧪 Протестировать → запустить тесты"},
            {"label": "📝 Новый запрос → описать задачу"},
            {"label": "🔴 Остановить сессию"},
        ],
        "allowFreeformInput": True,
    },
}


def show_dialog(dialog: dict) -> None:
    """Показать интерактивный диалог и напечатать результат в stdout."""
    header = dialog.get("header", "dialog")
    question = dialog["question"]
    options = dialog["options"]
    allow_freeform = dialog.get("allowFreeformInput", False)

    # Формируем choices: номер + label, recommended помечаем ✓
    choices = []
    default_value = 1
    for i, opt in enumerate(options):
        label = opt["label"]
        is_rec = opt.get("recommended", False)
        display = f"{i+1}  {label}"
        if is_rec:
            display += "  ✓"
            default_value = i + 1
        choices.append({"name": display, "value": i + 1})

    # Freeform ввод — последний пункт
    if allow_freeform:
        choices.append(Separator())
        choices.append({"name": "Ввести свой ответ...", "value": 0})

    result = inquirer.select(
        message=question,
        choices=choices,
        default=default_value,
        pointer="→",
        show_cursor=False,
        cycle=True,
    ).execute()

    if result == 0 and allow_freeform:
        custom = inquirer.text(message="Ваш ответ:").execute()
        if custom:
            print(f"CUSTOM:{header}:{custom}")
        else:
            print("CANCELLED")
            sys.exit(1)
    elif result > 0:
        print(f"SELECTED:{header}:{result}")
    else:
        print("CANCELLED")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="PTM Interactive Dialog")
    parser.add_argument("dialog_type", nargs="?", choices=["1", "2", "3"], help="Тип предустановленного диалога")
    parser.add_argument("--json", type=str, help="JSON-строка с вопросом в формате questions[]")
    parser.add_argument("--title", type=str, help="Заголовок кастомного диалога (legacy)")
    parser.add_argument("--options", nargs="+", type=str, help="Варианты кастомного диалога (legacy)")
    args = parser.parse_args()

    if args.dialog_type:
        # Предустановленный диалог
        dialog = DIALOGS[args.dialog_type]
    elif args.json:
        # JSON-формат questions[]
        dialog = json.loads(args.json)
    elif args.title and args.options:
        # Legacy: --title + --options
        dialog = {
            "header": "custom",
            "question": args.title,
            "options": [{"label": opt} for opt in args.options],
            "allowFreeformInput": True,
        }
    else:
        parser.error("Укажите тип диалога (1/2/3), --json или --title + --options")
        return

    show_dialog(dialog)


if __name__ == "__main__":
    main()
