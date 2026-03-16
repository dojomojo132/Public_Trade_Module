"""
debug_mcp_server.py — MCP-сервер ptm-debug.

Экспортирует инструменты отладки для агентов Copilot через JSON-RPC stdio:
  debug_connect, debug_disconnect, debug_launch,
  debug_set_breakpoints, debug_clear_breakpoints,
  debug_continue, debug_step_over, debug_step_into, debug_step_out,
  debug_get_stack, debug_get_variables, debug_evaluate, debug_status

Протокол: MCP JSON-RPC 2.0 over stdio (stdin/stdout).
Кодировка: UTF-8 без BOM. Каждое сообщение — отдельная строка JSON.

Запуск:
    python scripts/debug/debug_mcp_server.py [--config scripts/debug/debug_config.json]
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

# Lazy imports to avoid path manipulation at module level (resolved in _bootstrap)
_session_module = None


def _bootstrap() -> None:
    """Добавить scripts/ в sys.path и импортировать модуль сессии (один раз)."""
    global _session_module
    if _session_module is not None:
        return
    scripts_dir = Path(__file__).resolve().parent.parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from debug import session as _sm  # noqa: PLC0415
    _session_module = _sm


def _get_session():
    _bootstrap()
    return _session_module.get_session()


def _create_session(config):
    _bootstrap()
    return _session_module.create_session(config)

logging.basicConfig(
    level=logging.INFO,
    format="[ptm-debug] %(levelname)s %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

_DEFAULT_CONFIG = Path(__file__).parent / "debug_config.json"

# ------------------------------------------------------------------
# Реестр инструментов
# ------------------------------------------------------------------

_TOOLS: list[dict[str, Any]] = [
    {
        "name": "debug_connect",
        "description": (
            "Запустить dbgs.exe, подключить отладчик к ИБ и начать polling. "
            "ВЫЗЫВАТЬ ПЕРВЫМ — без него остальные инструменты не работают."
        ),
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "debug_disconnect",
        "description": "Завершить сессию: detach от ИБ, остановить dbgs.exe и 1cv8c.exe.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "debug_launch",
        "description": "Запустить 1С:Предприятие в режиме отладки (после debug_connect).",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "debug_set_breakpoints",
        "description": "Установить точки останова в BSL-модуле.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Абсолютный путь к .bsl файлу в Конфигурация/",
                },
                "lines": {
                    "type": "array",
                    "items": {"type": "integer"},
                    "description": "Список номеров строк (1-based)",
                },
            },
            "required": ["file_path", "lines"],
        },
    },
    {
        "name": "debug_clear_breakpoints",
        "description": "Очистить точки останова (для файла или все).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Путь к BSL-файлу (пусто → очистить все)",
                },
            },
            "required": [],
        },
    },
    {
        "name": "debug_continue",
        "description": "Продолжить выполнение (F5) после остановки на breakpoint.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "debug_step_over",
        "description": "Шаг через (F10) — выполнить текущую строку без входа в вызовы.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "debug_step_into",
        "description": "Шаг в (F11) — войти внутрь вызываемой процедуры.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "debug_step_out",
        "description": "Шаг из (Shift+F11) — выйти из текущей процедуры.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "debug_get_stack",
        "description": "Получить стек вызовов текущего потока (с путями к BSL).",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "debug_get_variables",
        "description": "Получить локальные переменные текущего фрейма.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "debug_evaluate",
        "description": (
            "Вычислить BSL-выражение. "
            "Работает только при остановке на breakpoint."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "BSL-выражение для вычисления",
                },
            },
            "required": ["expression"],
        },
    },
    {
        "name": "debug_status",
        "description": "Получить полный статус сессии отладки.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    },
]

# ------------------------------------------------------------------
# Диспетчер инструментов
# ------------------------------------------------------------------

def _dispatch(tool_name: str, arguments: dict[str, Any]) -> Any:
    session = _get_session()

    if tool_name == "debug_connect":
        config = _load_config()
        s = _create_session(config)
        return s.connect()

    if session is None:
        return {"ok": False, "message": "Сессия не инициализирована — вызовите debug_connect"}

    if tool_name == "debug_disconnect":
        return session.disconnect()
    if tool_name == "debug_launch":
        return session.launch()
    if tool_name == "debug_set_breakpoints":
        return session.set_breakpoints(
            file_path=arguments["file_path"],
            lines=arguments["lines"],
        )
    if tool_name == "debug_clear_breakpoints":
        return session.clear_breakpoints(
            file_path=arguments.get("file_path") or None,
        )
    if tool_name == "debug_continue":
        return session.continue_execution()
    if tool_name == "debug_step_over":
        return session.step_over()
    if tool_name == "debug_step_into":
        return session.step_into()
    if tool_name == "debug_step_out":
        return session.step_out()
    if tool_name == "debug_get_stack":
        return session.get_call_stack()
    if tool_name == "debug_get_variables":
        return session.get_variables()
    if tool_name == "debug_evaluate":
        return session.evaluate(expression=arguments["expression"])
    if tool_name == "debug_status":
        return session.get_status()

    return {"ok": False, "message": f"Неизвестный инструмент: {tool_name}"}


# ------------------------------------------------------------------
# Конфигурация
# ------------------------------------------------------------------

_config_path: Path = _DEFAULT_CONFIG


def _load_config() -> dict[str, Any]:
    if not _config_path.exists():
        raise FileNotFoundError(
            f"Файл конфигурации не найден: {_config_path}\n"
            "Скопируйте scripts/debug/debug_config.json и заполните пути."
        )
    with open(_config_path, encoding="utf-8") as fh:
        return json.load(fh)


# ------------------------------------------------------------------
# JSON-RPC 2.0 stdio transport
# ------------------------------------------------------------------

def _send(obj: Any) -> None:
    line = json.dumps(obj, ensure_ascii=False)
    sys.stdout.write(line + "\n")
    sys.stdout.flush()


def _error_response(req_id: Any, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def _handle_request(req: dict[str, Any]) -> None:
    req_id = req.get("id")
    method = req.get("method", "")
    params = req.get("params", {})

    # --- MCP lifecycle ---
    if method == "initialize":
        _send({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "ptm-debug", "version": "1.0.0"},
                "capabilities": {"tools": {}},
            },
        })
        return

    if method == "initialized":
        return  # notification, no response

    if method == "tools/list":
        _send({"jsonrpc": "2.0", "id": req_id, "result": {"tools": _TOOLS}})
        return

    if method == "tools/call":
        tool_name: str = params.get("name", "")
        arguments: dict = params.get("arguments", {})
        try:
            result = _dispatch(tool_name, arguments)
            _send({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}],
                    "isError": not result.get("ok", True),
                },
            })
        except Exception as exc:
            logger.exception("Ошибка при вызове %s", tool_name)
            _send(_error_response(req_id, -32603, str(exc)))
        return

    if method == "ping":
        _send({"jsonrpc": "2.0", "id": req_id, "result": {}})
        return

    _send(_error_response(req_id, -32601, f"Метод не найден: {method}"))


def _main() -> None:
    global _config_path

    import argparse
    parser = argparse.ArgumentParser(description="ptm-debug MCP Server")
    parser.add_argument(
        "--config",
        default=str(_DEFAULT_CONFIG),
        help="Путь к debug_config.json",
    )
    args = parser.parse_args()
    _config_path = Path(args.config)

    logger.info("ptm-debug MCP Server запущен (config: %s)", _config_path)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError as exc:
            _send(_error_response(None, -32700, f"Parse error: {exc}"))
            continue
        try:
            _handle_request(req)
        except Exception as exc:
            logger.exception("Необработанная ошибка")
            _send(_error_response(req.get("id"), -32603, str(exc)))


if __name__ == "__main__":
    _main()
