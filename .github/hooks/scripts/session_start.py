# -*- coding: utf-8 -*-
"""
SessionStart hook: напоминание о регламенте при старте сессии.
Инжектирует systemMessage с ключевыми правилами безопасности.
"""
import json
import sys

output = {
    "systemMessage": (
        "[1C GUARDRAIL] Напоминание при старте сессии:\n"
        "1. ПЕРЕД изменениями: mcp_dev-mcp_dev_dump (синхронизация ИБ -> файлы)\n"
        "2. ПЕРЕД изменениями: прочитать Документация/КРИТИЧЕСКИЕ_ОШИБКИ.md\n"
        "3. ПЕРЕД изменениями: mcp_dev-mcp_dev_backup (локальный бэкап)\n"
        "4. ПОСЛЕ изменений BSL/XML: вызвать get_errors\n"
        "5. ПЕРЕД деплоем: mcp_dev-mcp_dev_validate\n"
        "6. Git commit — ТОЛЬКО после подтверждения пользователем"
    )
}

json.dump(output, sys.stdout, ensure_ascii=False)
