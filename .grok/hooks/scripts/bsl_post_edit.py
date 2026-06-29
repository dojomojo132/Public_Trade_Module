# -*- coding: utf-8 -*-
"""PostToolUse: напоминание о верификации BSL/XML после редактирования."""
from __future__ import annotations

import json
import sys

EDIT_KEYWORDS = (
    "search_replace",
    "strreplace",
    "edit",
    "write",
    "create_file",
    "multi_replace",
    "replace",
)
CONFIG_SEGMENTS = (
    "catalogs", "documents", "commonmodules", "dataprocessors",
    "reports", "enums", "accumulationregisters", "informationregisters",
    "constants", "subsystems", "definedtypes", "roles",
    "справочники", "документы", "общиемодули", "обработки",
    "отчеты", "перечисления", "регистрысведений", "регистрынакопления",
)


def main() -> None:
    try:
        hook_input = json.load(sys.stdin)
    except Exception:
        hook_input = {}

    tool_name = str(
        hook_input.get("tool_name") or hook_input.get("toolName") or ""
    ).lower()
    tool_input = hook_input.get("tool_input") or hook_input.get("toolInput") or {}

    output: dict = {}
    if not any(kw in tool_name for kw in EDIT_KEYWORDS):
        json.dump(output, sys.stdout, ensure_ascii=False)
        return

    if not isinstance(tool_input, dict):
        json.dump(output, sys.stdout, ensure_ascii=False)
        return

    file_path = str(
        tool_input.get("filePath")
        or tool_input.get("file_path")
        or tool_input.get("path")
        or ""
    ).lower()

    messages: list[str] = []
    if file_path.endswith(".bsl"):
        messages.append(
            "BSL изменён → skill 1c-verify: onec-mcp get_errors на файл"
        )
    elif file_path.endswith(".xml") and any(seg in file_path for seg in CONFIG_SEGMENTS):
        messages.append(
            "XML метаданных изменён → dev-mcp dev_validate + проверь ConfigDumpInfo"
        )

    if messages:
        output["systemMessage"] = "[1C] " + "; ".join(messages)

    json.dump(output, sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()