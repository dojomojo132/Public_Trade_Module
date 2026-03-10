# -*- coding: utf-8 -*-
"""
Smart Sync — синхронизация только изменённых файлов между папками конфигурации.

Использует git diff для определения изменённых файлов и копирует
ТОЛЬКО их из Конфигурация/ в Конфигурация/Проверка/.

Значительно ускоряет деплой при мелких правках (BSL, XML).

Использование:
    python scripts/_smart_sync.py              # синхронизировать изменённые
    python scripts/_smart_sync.py --all        # полная синхронизация (как раньше)
    python scripts/_smart_sync.py --dry-run    # показать что будет скопировано
    python scripts/_smart_sync.py --status     # показать статус файлов
"""

import argparse
import pathlib
import shutil
import subprocess
import sys
import time

PROJECT_ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")
CONFIG_DIR = PROJECT_ROOT / "Конфигурация"
CHECK_DIR = CONFIG_DIR / "Проверка"


def get_changed_files_git():
    """Получить список изменённых файлов через git diff (staged + unstaged + untracked)."""
    changed = set()

    # Unstaged changes
    result = subprocess.run(
        ["git", "diff", "--name-only", "--", "Конфигурация/"],
        capture_output=True, text=True, cwd=str(PROJECT_ROOT), encoding="utf-8"
    )
    if result.returncode == 0:
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                changed.add(line.strip())

    # Staged changes
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--", "Конфигурация/"],
        capture_output=True, text=True, cwd=str(PROJECT_ROOT), encoding="utf-8"
    )
    if result.returncode == 0:
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                changed.add(line.strip())

    # Untracked new files
    result = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "--", "Конфигурация/"],
        capture_output=True, text=True, cwd=str(PROJECT_ROOT), encoding="utf-8"
    )
    if result.returncode == 0:
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                changed.add(line.strip())

    return changed


def filter_config_files(changed_files):
    """
    Фильтрует только файлы из Конфигурация/ (исключая Конфигурация/Проверка/).
    Возвращает список (src_path, dst_path) кортежей.
    """
    pairs = []
    for rel_path in changed_files:
        p = pathlib.PurePosixPath(rel_path)
        parts = list(p.parts)

        # Нас интересуют файлы из Конфигурация/ но НЕ из Конфигурация/Проверка/
        if len(parts) < 2:
            continue
        if parts[0] != "Конфигурация":
            continue
        if parts[1] == "Проверка":
            continue

        # Конфигурация/X/Y → Конфигурация/Проверка/X/Y
        src = PROJECT_ROOT / pathlib.Path(*parts)
        # Убираем "Конфигурация/" и добавляем "Конфигурация/Проверка/"
        dst = CHECK_DIR / pathlib.Path(*parts[1:])

        pairs.append((src, dst))
    return pairs


def sync_files(pairs, dry_run=False):
    """Копировать файлы из src в dst."""
    copied = 0
    skipped = 0
    errors = 0

    for src, dst in pairs:
        if not src.exists():
            # Файл удалён — удаляем и в Проверка
            if dst.exists():
                if dry_run:
                    print(f"  🗑  УДАЛИТЬ: {dst.relative_to(PROJECT_ROOT)}")
                else:
                    dst.unlink()
                    print(f"  🗑  {dst.relative_to(PROJECT_ROOT)}")
                copied += 1
            continue

        try:
            if dry_run:
                size = src.stat().st_size
                print(f"  →  {src.relative_to(PROJECT_ROOT)} ({size} байт)")
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(str(src), str(dst))
                print(f"  ✓  {src.relative_to(PROJECT_ROOT)}")
            copied += 1
        except Exception as e:
            print(f"  ✗  {src.relative_to(PROJECT_ROOT)}: {e}")
            errors += 1

    return copied, skipped, errors


def full_sync(dry_run=False):
    """Полная синхронизация Конфигурация/ → Конфигурация/Проверка/."""
    pairs = []
    for src in CONFIG_DIR.rglob("*"):
        if not src.is_file():
            continue
        # Пропускаем саму папку Проверка
        try:
            src.relative_to(CHECK_DIR)
            continue
        except ValueError:
            pass

        rel = src.relative_to(CONFIG_DIR)
        dst = CHECK_DIR / rel
        pairs.append((src, dst))

    return sync_files(pairs, dry_run)


def show_status():
    """Показать статус: какие файлы изменены и требуют синхронизации."""
    changed = get_changed_files_git()
    pairs = filter_config_files(changed)

    if not pairs:
        print("✓ Нет изменённых файлов для синхронизации.")
        return

    print(f"Изменённых файлов конфигурации: {len(pairs)}")
    print()

    bsl_count = sum(1 for s, _ in pairs if s.suffix == ".bsl")
    xml_count = sum(1 for s, _ in pairs if s.suffix == ".xml")
    other_count = len(pairs) - bsl_count - xml_count

    print(f"  BSL: {bsl_count}  |  XML: {xml_count}  |  Другие: {other_count}")
    print()

    for src, dst in sorted(pairs, key=lambda x: str(x[0])):
        exists_in_check = dst.exists()
        status = "ЕСТЬ" if exists_in_check else "НОВЫЙ"
        marker = "📝" if exists_in_check else "🆕"
        print(f"  {marker} [{status}] {src.relative_to(PROJECT_ROOT)}")


def main():
    parser = argparse.ArgumentParser(description="Smart Sync — синхронизация изменённых файлов конфигурации")
    parser.add_argument("--all", action="store_true", help="Полная синхронизация (все файлы)")
    parser.add_argument("--dry-run", action="store_true", help="Показать что будет скопировано, не копировать")
    parser.add_argument("--status", action="store_true", help="Показать статус изменений")
    args = parser.parse_args()

    print("=" * 60)
    print("=== Smart Sync: Конфигурация/ → Конфигурация/Проверка/ ===")
    print("=" * 60)
    print()

    if args.status:
        show_status()
        return

    start = time.time()

    if args.all:
        print("Режим: ПОЛНАЯ синхронизация")
        if args.dry_run:
            print("(dry-run — файлы НЕ копируются)")
        print()
        copied, skipped, errors = full_sync(args.dry_run)
    else:
        # Smart sync — только изменённые
        changed = get_changed_files_git()
        pairs = filter_config_files(changed)

        if not pairs:
            print("✓ Нет изменённых файлов для синхронизации.")
            print("  Используйте --all для полной синхронизации.")
            return

        print(f"Режим: SMART (только изменённые — {len(pairs)} файлов)")
        if args.dry_run:
            print("(dry-run — файлы НЕ копируются)")
        print()
        copied, skipped, errors = sync_files(pairs, args.dry_run)

    elapsed = time.time() - start
    print()
    print(f"{'[DRY-RUN] ' if args.dry_run else ''}Готово за {elapsed:.1f} сек:")
    print(f"  Скопировано: {copied}")
    if errors:
        print(f"  Ошибок: {errors}")
        sys.exit(1)


if __name__ == "__main__":
    main()
