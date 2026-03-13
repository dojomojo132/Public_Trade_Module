# -*- coding: utf-8 -*-
"""
Agent-scoped PostToolUse hook для 1c-coder.
После редактирования BSL/XML файлов — напоминает запустить get_errors и обновить multi-file.
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

# Проверяем операции редактирования файлов
is_edit = any(kw in tool_name.lower() for kw in [
    "edit", "create_file", "replace", "write", "multi_replace"
])

if is_edit and isinstance(tool_input, dict):
    file_path = (
        tool_input.get("filePath", "")
        or tool_input.get("file_path", "")
        or tool_input.get("path", "")
    ).lower()

    messages = []

    if file_path.endswith(".bsl"):
        messages.append(
            "BSL файл изменён → запусти get_errors для проверки синтаксиса"
        )
    elif file_path.endswith(".xml"):
        # Проверяем, это файл конфигурации?
        config_segments = [
            "catalogs", "documents", "commonmodules", "dataprocessors",
            "reports", "enums", "accumulationregisters", "informationregisters",
            "constants", "subsystems", "definedtypes", "roles"
        ]
        if any(seg in file_path for seg in config_segments):
            messages.append(
                "XML конфигурации изменён → проверь Configuration.xml + ConfigDumpInfo.xml"
            )

    if messages:
        output["systemMessage"] = "[PTM CODER] " + "; ".join(messages)

json.dump(output, sys.stdout, ensure_ascii=False)
