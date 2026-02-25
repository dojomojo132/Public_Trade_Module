# -*- coding: utf-8 -*-
"""
Локальный бэкап конфигурации перед изменениями.
Копирует Конфигурация/ и MCP_Extension/ в папку _backups/YYYY-MM-DD_HHMMSS/.
Хранит не более MAX_BACKUPS последних бэкапов, старые удаляет автоматически.
Не попадает в git (_backups/ в .gitignore).

Использование:
    python scripts/_local_backup.py "описание задачи"
    python scripts/_local_backup.py  # описание опционально
"""

import pathlib
import shutil
import sys
import datetime

ROOT = pathlib.Path(r"D:\Git\Public_Trade_Module")
BACKUPS_DIR = ROOT / "_backups"
MAX_BACKUPS = 10

SOURCES = [
    ROOT / "Конфигурация",
    ROOT / "MCP_Extension",
]


def make_backup(description: str = "") -> pathlib.Path:
    BACKUPS_DIR.mkdir(exist_ok=True)

    stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_dir = BACKUPS_DIR / stamp
    backup_dir.mkdir()

    print(f"=== Локальный бэкап: {stamp} ===")
    if description:
        print(f"    Задача: {description}")

    for src in SOURCES:
        if src.exists():
            dst = backup_dir / src.name
            shutil.copytree(src, dst)
            print(f"  ✓ {src.name}/  →  _backups/{stamp}/{src.name}/")
        else:
            print(f"  - {src.name}/ (не найдена)")

    # Записать info.txt
    info = backup_dir / "info.txt"
    info.write_text(
        f"Дата: {stamp}\nЗадача: {description}\n",
        encoding="utf-8"
    )

    # Удалить старые бэкапы (оставить MAX_BACKUPS)
    all_backups = sorted(BACKUPS_DIR.iterdir())
    while len(all_backups) > MAX_BACKUPS:
        old = all_backups.pop(0)
        shutil.rmtree(old)
        print(f"  🗑  Удалён старый бэкап: {old.name}")

    print(f"\n✓ Бэкап создан: _backups/{stamp}/")
    print(f"  Всего бэкапов: {len(sorted(BACKUPS_DIR.iterdir()))}/{MAX_BACKUPS}")
    return backup_dir


def list_backups():
    if not BACKUPS_DIR.exists():
        print("Бэкапов нет.")
        return
    backups = sorted(BACKUPS_DIR.iterdir(), reverse=True)
    print(f"Доступные бэкапы ({len(backups)}):")
    for b in backups:
        info_file = b / "info.txt"
        task = ""
        if info_file.exists():
            for line in info_file.read_text(encoding="utf-8").splitlines():
                if line.startswith("Задача:"):
                    task = line.replace("Задача:", "").strip()
        print(f"  {b.name}  {task}")


def restore_backup(stamp: str):
    backup_dir = BACKUPS_DIR / stamp
    if not backup_dir.exists():
        print(f"Бэкап {stamp} не найден.")
        return

    print(f"=== Восстановление из бэкапа: {stamp} ===")
    for src_name in ["Конфигурация", "MCP_Extension"]:
        src = backup_dir / src_name
        dst = ROOT / src_name
        if src.exists():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"  ✓ {src_name}/ восстановлена")
        else:
            print(f"  - {src_name}/ отсутствует в бэкапе")
    print("\n✓ Восстановление завершено.")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--list":
        list_backups()
    elif args and args[0] == "--restore":
        stamp = args[1] if len(args) > 1 else ""
        if stamp:
            restore_backup(stamp)
        else:
            print("Укажите метку бэкапа: python _local_backup.py --restore 2026-02-25_143022")
            list_backups()
    else:
        description = " ".join(args) if args else ""
        make_backup(description)
