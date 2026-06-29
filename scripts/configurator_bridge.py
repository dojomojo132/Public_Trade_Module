# -*- coding: utf-8 -*-
"""
1C Configurator Bridge — MCP-сервер для управления окном Конфигуратора 1С.

Предоставляет инструменты для:
  - Скриншотов окна Конфигуратора (для vision-моделей)
  - Навигации по дереву метаданных
  - Клика, ввода текста, горячих клавиш
  - Инспекции UI-элементов (для отладки автоматизации)

Протокол: JSON-RPC 2.0 через stdin/stdout (MCP stdio transport).
Зависимости: pywinauto, Pillow, mss, pywin32

Запуск: python scripts/configurator_bridge.py
"""

import base64
import io
import json
import logging
import pathlib
import sys
import time
from typing import Any, Dict, Optional

# === Force UTF-8 on Windows ===
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stdin, "buffer"):
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="replace")

# === Logging (NOT stdout — occupied by MCP) ===
log_path = pathlib.Path(__file__).parent.parent / "logs" / "configurator_bridge.log"
log_path.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=str(log_path),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("configurator-bridge")

# === Imports ===
import mss
from PIL import Image
from pywinauto.application import Application
import pywinauto.keyboard as kbd
import pywinauto.mouse as mouse

# ============================================================================
# Constants
# ============================================================================

SERVER_INFO = {
    "name": "1c-configurator-bridge",
    "version": "0.1.0",
}

CAPABILITIES = {
    "tools": {},
}

# ============================================================================
# Tool Definitions
# ============================================================================

TOOLS = [
    {
        "name": "configurator_screenshot",
        "description": (
            "Сделать скриншот окна Конфигуратора 1С. "
            "Возвращает base64 PNG. "
            "window_only=true захватывает только окно, false — весь экран. "
            "Используй для проверки текущего состояния и визуальной навигации."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "window_only": {
                    "type": "boolean",
                    "description": "True = только окно Конфигуратора, False = весь экран",
                    "default": True,
                },
            },
        },
    },
    {
        "name": "configurator_inspect",
        "description": (
            "Инспекция UI-элементов окна Конфигуратора. "
            "Возвращает дерево контролов с именами, типами, координатами. "
            "Используй для поиска элементов перед кликом."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "max_depth": {
                    "type": "integer",
                    "description": "Глубина обхода (0-4, по умолчанию 2)",
                    "default": 2,
                },
                "filter_type": {
                    "type": "string",
                    "description": "Фильтр по типу контрола: TreeView, Button, Edit, etc.",
                },
            },
        },
    },
    {
        "name": "configurator_click",
        "description": (
            "Клик мышью по абсолютным экранным координатам. "
            "Сначала сделай screenshot чтобы определить координаты, после клика — ещё один для проверки."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "x": {"type": "integer", "description": "X координата (абсолютная)"},
                "y": {"type": "integer", "description": "Y координата (абсолютная)"},
                "button": {
                    "type": "string",
                    "description": "left | right | middle",
                    "default": "left",
                },
                "double": {
                    "type": "boolean",
                    "description": "True для двойного клика",
                    "default": False,
                },
            },
            "required": ["x", "y"],
        },
    },
    {
        "name": "configurator_type_text",
        "description": (
            "Ввести текст в активный элемент Конфигуратора (через буфер обмена, "
            "поддержка кириллицы). Перед вводом убедись что нужное поле активно."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Текст для ввода"},
                "clear_first": {
                    "type": "boolean",
                    "description": "Очистить поле перед вводом (Ctrl+A → Delete)",
                    "default": False,
                },
            },
            "required": ["text"],
        },
    },
    {
        "name": "configurator_hotkey",
        "description": (
            "Отправить горячую клавишу в Конфигуратор. "
            "Формат pywinauto: ^ = Ctrl, + = Shift, % = Alt. "
            "Примеры: '{F7}', '^s', '{ENTER}', '%{F4}', '^+n'. "
            "Клавиши: {F1}-{F12}, {ENTER}, {TAB}, {DELETE}, {ESCAPE}, "
            "{UP}, {DOWN}, {LEFT}, {RIGHT}, {HOME}, {END}."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "keys": {"type": "string", "description": "Комбинация клавиш"},
            },
            "required": ["keys"],
        },
    },
    {
        "name": "configurator_tree_navigate",
        "description": (
            "Навигация по дереву конфигурации. "
            "path — путь через '/' (напр. 'Справочники/Номенклатура'). "
            "action: select | expand | open (двойной клик) | context_menu (правый клик). "
            "Дерево должно быть видимо."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Путь в дереве через '/'"},
                "action": {
                    "type": "string",
                    "description": "select | expand | open | context_menu",
                    "default": "select",
                },
            },
            "required": ["path"],
        },
    },
    {
        "name": "configurator_window_info",
        "description": (
            "Информация о текущем состоянии окна Конфигуратора: заголовок, размеры, "
            "позиция, список дочерних панелей. Также показывает список всех окон если "
            "Конфигуратор не найден."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
]

# ============================================================================
# Helpers
# ============================================================================


def _find_configurator_window():
    """Find and return (app, win) for the Configurator window."""
    for backend in ("uia", "win32"):
        try:
            app = Application(backend=backend).connect(title_re="Конфигуратор", timeout=5)
            win = app.window(title_re="Конфигуратор")
            if win.exists():
                return app, win
        except Exception as e:
            logger.debug(f"{backend} connect: {e}")
    return None, None


def _capture_screenshot(hwnd=None):
    """Capture window (by hwnd) or primary monitor. Returns base64 PNG."""
    with mss.mss() as sct:
        if hwnd:
            import win32gui
            rect = win32gui.GetWindowRect(hwnd)
            monitor = {
                "left": rect[0], "top": rect[1],
                "width": rect[2] - rect[0], "height": rect[3] - rect[1],
            }
        else:
            monitor = sct.monitors[1]

        img = sct.grab(monitor)
        pil_img = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")

        # Resize if too large to save context tokens
        if pil_img.width > 1920:
            ratio = 1920 / pil_img.width
            pil_img = pil_img.resize((1920, int(pil_img.height * ratio)), Image.LANCZOS)

        buf = io.BytesIO()
        pil_img.save(buf, format="PNG", optimize=True)
        return base64.b64encode(buf.getvalue()).decode("ascii")


def _collect_controls(wrapper, depth=0, max_depth=3):
    """Recursively collect control info."""
    results = []
    try:
        info = {
            "name": wrapper.window_text()[:120] if hasattr(wrapper, "window_text") else "",
            "type": wrapper.friendly_class_name() if hasattr(wrapper, "friendly_class_name") else "",
            "depth": depth,
        }
        try:
            r = wrapper.rectangle()
            info["rect"] = {"l": r.left, "t": r.top, "r": r.right, "b": r.bottom}
        except Exception:
            pass
        results.append(info)

        if depth < max_depth:
            try:
                for child in wrapper.children():
                    results.extend(_collect_controls(child, depth + 1, max_depth))
            except Exception:
                pass
    except Exception:
        pass
    return results


def _focus_configurator(win):
    """Bring Configurator to foreground."""
    try:
        win.set_focus()
        time.sleep(0.3)
    except Exception:
        pass


# ============================================================================
# Tool Handlers
# ============================================================================


def handle_configurator_screenshot(args: Dict) -> Dict:
    window_only = args.get("window_only", True)
    if window_only:
        _, win = _find_configurator_window()
        if win is None:
            return {"error": "Окно Конфигуратора не найдено. Убедитесь что Конфигуратор открыт."}
        b64 = _capture_screenshot(hwnd=win.handle)
    else:
        b64 = _capture_screenshot()

    return {
        "status": "ok",
        "format": "png",
        "encoding": "base64",
        "image": b64,
        "hint": "base64 PNG. Анализируй визуально для определения следующего действия.",
    }


def handle_configurator_inspect(args: Dict) -> Dict:
    _, win = _find_configurator_window()
    if win is None:
        return {"error": "Окно Конфигуратора не найдено."}

    max_depth = min(max(args.get("max_depth", 2), 0), 4)
    filter_type = args.get("filter_type")

    controls = _collect_controls(win, depth=0, max_depth=max_depth)

    if filter_type:
        ft = filter_type.lower()
        controls = [c for c in controls if ft in (c.get("type") or "").lower()]

    truncated = len(controls) > 200
    if truncated:
        controls = controls[:200]

    return {"status": "ok", "count": len(controls), "truncated": truncated, "controls": controls}


def handle_configurator_click(args: Dict) -> Dict:
    x, y = args["x"], args["y"]
    button = args.get("button", "left")
    double = args.get("double", False)

    _, win = _find_configurator_window()
    if win is None:
        return {"error": "Окно Конфигуратора не найдено."}

    _focus_configurator(win)

    if double:
        mouse.double_click(button=button, coords=(x, y))
    else:
        mouse.click(button=button, coords=(x, y))
    time.sleep(0.5)

    return {"status": "ok", "action": f"{'double_' if double else ''}{button}_click", "x": x, "y": y}


def handle_configurator_type_text(args: Dict) -> Dict:
    text = args["text"]
    clear_first = args.get("clear_first", False)

    _, win = _find_configurator_window()
    if win is None:
        return {"error": "Окно Конфигуратора не найдено."}

    _focus_configurator(win)

    if clear_first:
        kbd.send_keys("^a{DELETE}")
        time.sleep(0.2)

    # Clipboard-based typing for Cyrillic support
    import win32clipboard
    import win32con

    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
    finally:
        win32clipboard.CloseClipboard()

    kbd.send_keys("^v")
    time.sleep(0.3)

    return {"status": "ok", "typed": text}


def handle_configurator_hotkey(args: Dict) -> Dict:
    keys = args["keys"]

    _, win = _find_configurator_window()
    if win is None:
        return {"error": "Окно Конфигуратора не найдено."}

    _focus_configurator(win)
    kbd.send_keys(keys)
    time.sleep(0.5)

    return {"status": "ok", "keys_sent": keys}


def handle_configurator_tree_navigate(args: Dict) -> Dict:
    path = args["path"]
    action = args.get("action", "select")

    _, win = _find_configurator_window()
    if win is None:
        return {"error": "Окно Конфигуратора не найдено."}

    _focus_configurator(win)

    # Find TreeView
    tree = None
    try:
        tree = win.child_window(control_type="Tree", found_index=0)
        if not tree.exists(timeout=3):
            tree = None
    except Exception:
        pass

    if tree is None:
        try:
            tree = win.child_window(class_name_re=".*TreeView.*", found_index=0)
            if not tree.exists(timeout=3):
                tree = None
        except Exception:
            pass

    if tree is None:
        return {
            "error": "Дерево конфигурации не найдено.",
            "hint": "Убедитесь что дерево метаданных видимо. Сделай screenshot.",
        }

    # Navigate path
    parts = [p.strip() for p in path.split("/") if p.strip()]
    current = None

    for i, part in enumerate(parts):
        try:
            if current is None:
                current = tree.get_item(part)
            else:
                try:
                    current.expand()
                    time.sleep(0.3)
                except Exception:
                    pass
                current = current.get_child(part)
        except Exception:
            # Fallback: search by text
            found = False
            try:
                candidates = tree.descendants() if i == 0 else (current.children() if current else [])
                for item in candidates:
                    txt = item.window_text() if hasattr(item, "window_text") else ""
                    if part.lower() in txt.lower():
                        current = item
                        found = True
                        break
            except Exception:
                pass

            if not found:
                return {
                    "error": f"Узел '{part}' не найден (шаг {i + 1}/{len(parts)}).",
                    "path_so_far": "/".join(parts[:i]),
                }

    if current is None:
        return {"error": "Навигация не дала результатов."}

    if action == "select":
        current.select()
    elif action == "expand":
        current.expand()
    elif action == "open":
        current.select()
        time.sleep(0.2)
        current.click_input(double=True)
    elif action == "context_menu":
        current.click_input(button="right")
    else:
        return {"error": f"Неизвестное действие: {action}"}

    time.sleep(0.5)

    item_text = current.window_text() if hasattr(current, "window_text") else ""
    return {"status": "ok", "path": path, "action": action, "item": item_text}


def handle_configurator_window_info(args: Dict) -> Dict:
    _, win = _find_configurator_window()
    if win is None:
        # List visible windows to help debugging
        try:
            import win32gui
            windows = []

            def cb(hwnd, res):
                if win32gui.IsWindowVisible(hwnd):
                    t = win32gui.GetWindowText(hwnd)
                    if t.strip():
                        res.append(t[:100])
            win32gui.EnumWindows(cb, windows)
            return {"error": "Конфигуратор не найден.", "visible_windows": windows[:20]}
        except Exception:
            return {"error": "Конфигуратор не найден."}

    rect = win.rectangle()
    info = {
        "status": "ok",
        "title": win.window_text(),
        "rect": {"left": rect.left, "top": rect.top, "w": rect.width(), "h": rect.height()},
        "active": win.is_active(),
        "visible": win.is_visible(),
    }

    try:
        children = win.children()
        info["panels"] = [
            {"name": c.window_text()[:80] if hasattr(c, "window_text") else "",
             "type": c.friendly_class_name() if hasattr(c, "friendly_class_name") else ""}
            for c in children[:30]
        ]
    except Exception:
        info["panels"] = []

    return info


# ============================================================================
# Tool Dispatcher
# ============================================================================

TOOL_HANDLERS = {
    "configurator_screenshot": handle_configurator_screenshot,
    "configurator_inspect": handle_configurator_inspect,
    "configurator_click": handle_configurator_click,
    "configurator_type_text": handle_configurator_type_text,
    "configurator_hotkey": handle_configurator_hotkey,
    "configurator_tree_navigate": handle_configurator_tree_navigate,
    "configurator_window_info": handle_configurator_window_info,
}


def handle_tool(name: str, arguments: Dict) -> Dict:
    handler = TOOL_HANDLERS.get(name)
    if not handler:
        return {"error": f"Unknown tool: {name}"}
    try:
        return handler(arguments)
    except Exception as e:
        logger.exception(f"Tool {name} failed")
        return {"error": str(e)}


# ============================================================================
# MCP Protocol (JSON-RPC 2.0 via stdio)
# ============================================================================


def make_response(req_id: Any, result: Any) -> Dict:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def make_error(req_id: Any, code: int, message: str) -> Dict:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


def handle_request(request: Dict) -> Optional[Dict]:
    method = request.get("method", "")
    params = request.get("params", {})
    req_id = request.get("id")

    logger.info(f"Request: {method} (id={req_id})")

    if method == "initialize":
        return make_response(req_id, {
            "protocolVersion": "2024-11-05",
            "capabilities": CAPABILITIES,
            "serverInfo": SERVER_INFO,
        })

    if method == "notifications/initialized":
        return None

    if method == "ping":
        return make_response(req_id, {})

    if method == "tools/list":
        return make_response(req_id, {"tools": TOOLS})

    if method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        result = handle_tool(tool_name, arguments)

        is_error = "error" in result and "status" not in result
        content_text = json.dumps(result, ensure_ascii=False, indent=2)

        return make_response(req_id, {
            "content": [{"type": "text", "text": content_text}],
            "isError": is_error,
        })

    if req_id is not None:
        return make_error(req_id, -32601, f"Method not found: {method}")

    return None


def run_stdio():
    """Main loop: read JSON-RPC from stdin, write to stdout."""
    logger.info("1C Configurator Bridge MCP server starting (stdio)")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
        except json.JSONDecodeError as e:
            resp = make_error(None, -32700, f"Parse error: {e}")
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
            continue

        response = handle_request(request)
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
            sys.stdout.flush()

    logger.info("1C Configurator Bridge MCP server stopped")


if __name__ == "__main__":
    run_stdio()
