# -*- coding: utf-8 -*-
"""
PreToolUse hook: мягкое напоминание при редактировании BSL/XML файлов конфигурации.
Не блокирует — только инжектирует systemMessage для .bsl и .xml файлов.
"""
import json
import sys

try:
    hook_input = json.load(sys.stdin)
except Exception:
    hook_input = {}

tool_name = hook_input.get("toolName", "")
tool_input = hook_input.get("toolInput", {})

# Определяем файл, с которым работаем
file_path = ""
if isinstance(tool_input, dict):
    file_path = (
        tool_input.get("filePath", "")
        or tool_input.get("file_path", "")
        or tool_input.get("path", "")
    )

file_lower = file_path.lower()
output = {}

# Напоминание только для операций редактирования BSL/XML файлов конфигурации
is_edit = any(kw in tool_name.lower() for kw in ["edit", "create", "replace", "write"])
is_config_file = any(
    segment in file_lower
    for segment in ["catalogs", "documents", "commonmodules", "dataprocessors",
                     "reports", "enums", "accumulationregisters", "informationregisters",
                     "constants", "subsystems"]
)
is_bsl_or_xml = file_lower.endswith(".bsl") or file_lower.endswith(".xml")

if is_edit and is_config_file and is_bsl_or_xml:
    messages = []
    if file_lower.endswith(".bsl"):
        messages.append(
            "[1C GUARDRAIL] Редактирование BSL в конфигурации. "
            "После завершения: вызови get_errors на этот файл."
        )
    if file_lower.endswith(".xml"):
        messages.append(
            "[1C GUARDRAIL] Редактирование XML конфигурации. "
            "Не забудь: Configuration.xml, ConfigDumpInfo.xml, подсистемы. "
            "После завершения: get_errors + validate-config.ps1."
        )
    if messages:
        output["systemMessage"] = "\n".join(messages)

json.dump(output, sys.stdout, ensure_ascii=False)
