# -*- coding: utf-8 -*-
"""
Workspace-level PostToolUse hook: аудит-лог всех операций агента.
Логирует tool calls в logs/agent_audit.log для отслеживания действий.
"""
import json
import sys
import os
from datetime import datetime

try:
    hook_input = json.load(sys.stdin)
except Exception:
    hook_input = {}

tool_name = hook_input.get("tool_name", hook_input.get("toolName", "unknown"))
session_id = hook_input.get("sessionId", "unknown")
timestamp = hook_input.get("timestamp", datetime.now().isoformat())

# Аудит-лог (не блокирует, только записывает)
log_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "logs")
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, "agent_audit.log")

try:
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} | session={session_id} | tool={tool_name}\n")
except OSError:
    pass  # Если лог недоступен — не блокируем работу

# Пустой output — не влияем на поведение
json.dump({}, sys.stdout, ensure_ascii=False)
