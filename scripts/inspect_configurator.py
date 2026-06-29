# -*- coding: utf-8 -*-
"""
Инспектор UI-элементов Конфигуратора 1С.

Утилита для разведки: сканирует окно Конфигуратора и выводит дерево
контролов с именами, типами, координатами и automation ID.

Использование:
    python scripts/inspect_configurator.py                # Базовый скан (глубина 2)
    python scripts/inspect_configurator.py --depth 3      # Глубже
    python scripts/inspect_configurator.py --filter Tree   # Только TreeView
    python scripts/inspect_configurator.py --screenshot    # + скриншот в файл
    python scripts/inspect_configurator.py --list-windows  # Список всех окон
"""

import argparse
import json
import sys
import time

# Force UTF-8
import io
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


def list_all_windows():
    """List all visible top-level windows."""
    import win32gui

    print("\n=== Все видимые окна ===\n")
    results = []

    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title.strip():
                rect = win32gui.GetWindowRect(hwnd)
                results.append({
                    "hwnd": hwnd,
                    "title": title,
                    "rect": f"({rect[0]}, {rect[1]}) - ({rect[2]}, {rect[3]})",
                })

    win32gui.EnumWindows(callback, None)

    for i, w in enumerate(results, 1):
        is_1c = "1С" in w["title"] or "1C" in w["title"] or "Конфигуратор" in w["title"]
        marker = " <<<< 1С" if is_1c else ""
        print(f"  {i:3d}. [{w['hwnd']:08X}] {w['title'][:80]}{marker}")
        print(f"       rect: {w['rect']}")

    print(f"\n  Всего окон: {len(results)}")
    return results


def inspect_window(max_depth=2, filter_type=None, do_screenshot=False):
    """Inspect the Configurator window controls."""
    from pywinauto.application import Application

    print("\n=== Поиск окна Конфигуратора ===\n")

    app = None
    win = None

    for backend in ("uia", "win32"):
        try:
            app = Application(backend=backend).connect(title_re="Конфигуратор", timeout=5)
            win = app.window(title_re="Конфигуратор")
            if win.exists():
                print(f"  Найдено ({backend} backend): {win.window_text()}")
                rect = win.rectangle()
                print(f"  Позиция: ({rect.left}, {rect.top}) - ({rect.right}, {rect.bottom})")
                print(f"  Размер: {rect.width()} x {rect.height()}")
                break
            else:
                win = None
        except Exception as e:
            print(f"  {backend}: не найдено ({e})")

    if win is None:
        print("\n  ❌ Окно Конфигуратора не найдено!")
        print("  Убедитесь, что Конфигуратор 1С открыт.\n")
        list_all_windows()
        return

    # Screenshot
    if do_screenshot:
        try:
            import mss
            from PIL import Image
            import win32gui

            hwnd = win.handle
            rect = win32gui.GetWindowRect(hwnd)
            with mss.mss() as sct:
                monitor = {
                    "left": rect[0], "top": rect[1],
                    "width": rect[2] - rect[0], "height": rect[3] - rect[1],
                }
                img = sct.grab(monitor)
                pil_img = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")
                out_path = "logs/configurator_screenshot.png"
                import pathlib
                pathlib.Path("logs").mkdir(exist_ok=True)
                pil_img.save(out_path)
                print(f"\n  📸 Скриншот сохранён: {out_path}")
        except Exception as e:
            print(f"\n  ⚠️ Скриншот не удался: {e}")

    # Control tree
    print(f"\n=== Дерево контролов (глубина {max_depth}) ===\n")

    count = [0]

    def print_tree(ctrl, depth=0):
        if depth > max_depth:
            return

        try:
            name = ctrl.window_text() if hasattr(ctrl, "window_text") else ""
            ctype = ctrl.friendly_class_name() if hasattr(ctrl, "friendly_class_name") else "?"
            
            # Apply filter
            if filter_type and filter_type.lower() not in ctype.lower():
                # Still recurse into children
                if depth < max_depth:
                    try:
                        for child in ctrl.children():
                            print_tree(child, depth + 1)
                    except Exception:
                        pass
                return

            indent = "  " + "│ " * depth
            rect_str = ""
            try:
                r = ctrl.rectangle()
                rect_str = f" [{r.left},{r.top} {r.width()}x{r.height()}]"
            except Exception:
                pass

            auto_id = ""
            try:
                aid = ctrl.automation_id()
                if aid:
                    auto_id = f" (aid={aid})"
            except Exception:
                pass

            # Truncate long names
            display_name = name[:60] + "..." if len(name) > 60 else name
            display_name = display_name.replace("\n", "↵")

            print(f"{indent}├─ {ctype}: \"{display_name}\"{auto_id}{rect_str}")
            count[0] += 1

            if depth < max_depth:
                try:
                    children = ctrl.children()
                    for child in children:
                        print_tree(child, depth + 1)
                except Exception:
                    pass

        except Exception as e:
            indent = "  " + "│ " * depth
            print(f"{indent}├─ ⚠️ Ошибка: {e}")

    print_tree(win)
    print(f"\n  Всего элементов: {count[0]}")


def main():
    parser = argparse.ArgumentParser(description="Инспектор UI-элементов Конфигуратора 1С")
    parser.add_argument("--depth", type=int, default=2, help="Глубина обхода дерева (0-5)")
    parser.add_argument("--filter", type=str, default=None, help="Фильтр по типу контрола")
    parser.add_argument("--screenshot", action="store_true", help="Сделать скриншот")
    parser.add_argument("--list-windows", action="store_true", help="Список всех видимых окон")
    parser.add_argument("--json", action="store_true", help="Вывод в JSON")
    args = parser.parse_args()

    if args.list_windows:
        list_all_windows()
    else:
        inspect_window(
            max_depth=args.depth,
            filter_type=args.filter,
            do_screenshot=args.screenshot,
        )


if __name__ == "__main__":
    main()
