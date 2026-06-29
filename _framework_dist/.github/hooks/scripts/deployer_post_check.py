# -*- coding: utf-8 -*-
"""
Agent-scoped PostToolUse hook для 1c-deployer.
После терминальных команд анализирует вывод на наличие ошибок деплоя.
"""
import json
import sys

try:
    hook_input = json.load(sys.stdin)
except Exception:
    hook_input = {}

tool_name = hook_input.get("tool_name", hook_input.get("toolName", ""))
tool_input = hook_input.get("tool_input", hook_input.get("toolInput", {}))
tool_response = str(hook_input.get("tool_response", hook_input.get("toolResponse", "")))

output = {}

# Анализируем вывод терминальных команд
if "terminal" in tool_name.lower() or "execute" in tool_name.lower():
    response_lower = tool_response.lower()

    errors_found = []

    # Коды ошибок деплоя
    if "exit_code: 1" in response_lower or "exit code: 1" in response_lower:
        errors_found.append("EXIT_CODE 1 — общая ошибка загрузки, читай ПОЛНЫЙ ЛОГ")
    if "exit_code: -2" in response_lower or "exit code: -2" in response_lower:
        errors_found.append("EXIT_CODE -2 — ТАЙМАУТ! Немедленный ОТКАТ!")
    if "exit_code: 10" in response_lower or "exit code: 10" in response_lower:
        errors_found.append("EXIT_CODE 10 — бэкап не удался, проверь доступ к ИБ")

    # Паттерны ошибок конфигуратора
    error_patterns = [
        ("диалог заблокирован", "ДИАЛОГ ЗАБЛОКИРОВАН — критическая ошибка XML"),
        ("пустой лог", "ПУСТОЙ ЛОГ — проблемы доступа к ИБ"),
        ("ошибка загрузки", "Ошибка загрузки конфигурации"),
        ("ошибка обновления", "Ошибка обновления ИБ"),
    ]

    for pattern, description in error_patterns:
        if pattern in response_lower:
            errors_found.append(description)

    if errors_found:
        output["systemMessage"] = (
            "[PTM DEPLOYER POST-CHECK] Обнаружены проблемы:\n"
            + "\n".join(f"  - {e}" for e in errors_found)
            + "\nДействуй по протоколу маршрутизации ошибок (см. agent.md)"
        )

json.dump(output, sys.stdout, ensure_ascii=False)
