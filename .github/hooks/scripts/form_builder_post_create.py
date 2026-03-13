# -*- coding: utf-8 -*-
"""
Agent-scoped PostToolUse hook для 1c-form-builder.
После создания Form.xml — напоминает про BOM, дескриптор и dual-folder sync.
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

is_create = any(kw in tool_name.lower() for kw in ["create_file", "write"])

if is_create and isinstance(tool_input, dict):
    file_path = (
        tool_input.get("filePath", "")
        or tool_input.get("file_path", "")
        or tool_input.get("path", "")
    ).lower()

    if "form.xml" in file_path or "form/" in file_path:
        output["systemMessage"] = (
            "[PTM FORM-BUILDER] Form.xml создан. Чеклист:\n"
            "1. BOM (EF BB BF) — проверь кодировку\n"
            "2. Module.bsl — создан с BOM\n"
            "3. Дескриптор — без BOM\n"
            "4. XML владельца — <Form>ИмяФормы</Form> в <ChildObjects>\n"
            "5. ConfigDumpInfo.xml — запись формы"
        )
    elif file_path.endswith("module.bsl") and ("form" in file_path or "форм" in file_path):
        output["systemMessage"] = (
            "[PTM FORM-BUILDER] Module.bsl формы создан. "
            "Проверь: BOM (EF BB BF), CRLF, директивы компиляции."
        )

json.dump(output, sys.stdout, ensure_ascii=False)
