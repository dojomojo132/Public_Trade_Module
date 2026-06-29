# -*- coding: utf-8 -*-
"""
Agent-scoped PreToolUse hook для closer.
Блокирует опасные операции: CREATEINFOBASE, git push --force, rm -rf, DROP.
"""
import json
import sys

try:
    hook_input = json.load(sys.stdin)
except Exception:
    hook_input = {}

tool_name = hook_input.get("tool_name", hook_input.get("toolName", ""))
tool_input = hook_input.get("tool_input", hook_input.get("toolInput", {}))

output = {}

# Проверяем терминальные команды
if "terminal" in tool_name.lower() or "execute" in tool_name.lower():
    command = ""
    if isinstance(tool_input, dict):
        command = (
            tool_input.get("command", "")
            or tool_input.get("cmd", "")
        ).lower()

    # Блокируемые паттерны
    blocked_patterns = [
        ("createinfobase", "CREATEINFOBASE запрещён без явного разрешения пользователя"),
        ("--force", "git push --force запрещён — используйте обычный push"),
        ("reset --hard", "git reset --hard запрещён — может потерять незакоммиченные изменения"),
        ("rm -rf", "rm -rf запрещён — слишком деструктивна"),
        ("drop table", "DROP TABLE запрещён из хука безопасности"),
        ("format c:", "Форматирование диска заблокировано"),
        ("del /s /q", "Массовое удаление заблокировано"),
    ]

    for pattern, reason in blocked_patterns:
        if pattern in command:
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"[PTM DEPLOYER GUARDRAIL] {reason}"
                }
            }
            json.dump(output, sys.stdout, ensure_ascii=False)
            sys.exit(0)

    # Предупреждение при деплое — напомнить о бэкапе
    deploy_keywords = ["deploy-config", "deploy_config", "-action full", "-action load"]
    if any(kw in command for kw in deploy_keywords):
        output["systemMessage"] = (
            "[PTM DEPLOYER] Деплой запущен. Убедись:\n"
            "1. Бэкап создан (mcp_dev-mcp_dev_backup)\n"
            "2. mcp_dev-mcp_dev_validate прошёл без ошибок\n"
            "3. КРИТИЧЕСКИЕ_ОШИБКИ.md проверен"
        )

json.dump(output, sys.stdout, ensure_ascii=False)
