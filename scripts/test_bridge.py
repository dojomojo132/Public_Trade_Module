# -*- coding: utf-8 -*-
"""
Live test: создание справочника через screenshot + click.
Пошаговый тест Configurator Bridge.

Использование:
    python scripts/test_bridge.py step1   # Screenshot + сохранить
    python scripts/test_bridge.py step2   # Right-click на Справочники
    python scripts/test_bridge.py step3   # Screenshot для контекстного меню
    python scripts/test_bridge.py step4   # Click на "Добавить"
    python scripts/test_bridge.py step5   # Screenshot результата
    python scripts/test_bridge.py click X Y        # Click по координатам
    python scripts/test_bridge.py rclick X Y       # Right-click по координатам
    python scripts/test_bridge.py type TEXT         # Ввести текст
    python scripts/test_bridge.py key KEYS          # Отправить горячую клавишу
    python scripts/test_bridge.py screenshot        # Просто скриншот
    python scripts/test_bridge.py undo              # Ctrl+Z (отмена)
"""

import io
import sys
import pathlib
import json
import base64

# Don't wrap stdout here — configurator_bridge already handles it on import

# Add project root to path
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from scripts.configurator_bridge import (
    handle_configurator_screenshot,
    handle_configurator_click,
    handle_configurator_type_text,
    handle_configurator_hotkey,
    handle_configurator_window_info,
)


LOG_DIR = pathlib.Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
STEP_NUM = [0]


def save_screenshot(result, label=""):
    """Save base64 screenshot to file."""
    if "error" in result and "status" not in result:
        print(f"  ❌ Ошибка: {result['error']}")
        return False

    b64 = result.get("image", "")
    if not b64:
        print("  ⚠️ Нет изображения в ответе")
        return False

    STEP_NUM[0] += 1
    fname = LOG_DIR / f"bridge_test_{STEP_NUM[0]:02d}{'_' + label if label else ''}.png"
    with open(fname, "wb") as f:
        f.write(base64.b64decode(b64))
    print(f"  📸 Скриншот сохранён: {fname}")
    return True


def do_screenshot(label=""):
    print(f"\n--- Screenshot {label} ---")
    result = handle_configurator_screenshot({"window_only": True})
    save_screenshot(result, label)


def do_click(x, y, button="left", double=False):
    action = f"{'double ' if double else ''}{button} click"
    print(f"\n--- {action} at ({x}, {y}) ---")
    result = handle_configurator_click({"x": x, "y": y, "button": button, "double": double})
    if "error" in result and "status" not in result:
        print(f"  ❌ {result['error']}")
    else:
        print(f"  ✅ {result.get('action', 'done')}")


def do_type(text, clear_first=False):
    print(f"\n--- Type: '{text}' ---")
    result = handle_configurator_type_text({"text": text, "clear_first": clear_first})
    if "error" in result and "status" not in result:
        print(f"  ❌ {result['error']}")
    else:
        print(f"  ✅ Typed: {result.get('typed', '')}")


def do_hotkey(keys):
    print(f"\n--- Hotkey: {keys} ---")
    result = handle_configurator_hotkey({"keys": keys})
    if "error" in result and "status" not in result:
        print(f"  ❌ {result['error']}")
    else:
        print(f"  ✅ Keys sent: {result.get('keys_sent', '')}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_bridge.py <command> [args]")
        print("Commands: screenshot, click X Y, rclick X Y, type TEXT, key KEYS, undo")
        print("          step1..step5, info")
        return

    cmd = sys.argv[1].lower()

    if cmd == "info":
        result = handle_configurator_window_info({})
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif cmd == "screenshot":
        do_screenshot("manual")

    elif cmd == "click" and len(sys.argv) >= 4:
        x, y = int(sys.argv[2]), int(sys.argv[3])
        do_click(x, y)
        do_screenshot("after_click")

    elif cmd == "rclick" and len(sys.argv) >= 4:
        x, y = int(sys.argv[2]), int(sys.argv[3])
        do_click(x, y, button="right")
        do_screenshot("after_rclick")

    elif cmd == "dclick" and len(sys.argv) >= 4:
        x, y = int(sys.argv[2]), int(sys.argv[3])
        do_click(x, y, double=True)
        do_screenshot("after_dclick")

    elif cmd == "type" and len(sys.argv) >= 3:
        text = " ".join(sys.argv[2:])
        do_type(text)
        do_screenshot("after_type")

    elif cmd == "key" and len(sys.argv) >= 3:
        keys = sys.argv[2]
        do_hotkey(keys)
        do_screenshot("after_key")

    elif cmd == "undo":
        do_hotkey("^z")
        do_screenshot("after_undo")

    elif cmd == "step1":
        print("=== STEP 1: Initial screenshot ===")
        do_screenshot("step1_initial")
        print("\n  Посмотри скриншот и определи координаты 'Справочники' в дереве.")

    elif cmd == "step2":
        print("=== STEP 2: Right-click on Справочники ===")
        # Coordinates from the initial screenshot analysis
        # The window is at (1913, 0), Справочники is approximately at line 5 from tree top
        # Adjust these based on step1 screenshot!
        x = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
        y = int(sys.argv[3]) if len(sys.argv) > 3 else 208
        do_click(x, y, button="right")
        do_screenshot("step2_context_menu")

    elif cmd == "step3":
        print("=== STEP 3: Screenshot (check context menu) ===")
        do_screenshot("step3_check")

    elif cmd == "step4":
        print("=== STEP 4: Click 'Добавить' in context menu ===")
        x = int(sys.argv[2]) if len(sys.argv) > 2 else 2050
        y = int(sys.argv[3]) if len(sys.argv) > 3 else 230
        do_click(x, y)
        do_screenshot("step4_after_add")

    elif cmd == "step5":
        print("=== STEP 5: Final screenshot ===")
        do_screenshot("step5_final")

    else:
        print(f"Unknown command: {cmd}")
        print("Commands: screenshot, click X Y, rclick X Y, type TEXT, key KEYS, undo")
        print("          step1..step5, info")


if __name__ == "__main__":
    main()
