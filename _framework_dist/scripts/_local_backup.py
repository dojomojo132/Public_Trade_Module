# -*- coding: utf-8 -*-
"""
Локальный бэкап конфигурации перед изменениями.
Копирует папки из project-config.yml (config_root + extensions) в _backups/YYYY-MM-DD_HHMMSS/.
Хранит не более MAX_BACKUPS последних бэкапов, старые удаляет автоматически.
Не попадает в git (_backups/ в .gitignore).

Исключения (не копируются в бэкап, восстанавливаются из эталона):
  - {config_root}/CommonTemplates/  (драйверы БПО, хранятся в _backups/_reference/)

Использование:
    python scripts/_local_backup.py "описание задачи"
    python scripts/_local_backup.py  # описание опционально
"""

import pathlib
import shutil
import sys
import datetime

try:
    from _project_config import config_root, backups_dir, extensions, PROJ_ROOT as ROOT
except ImportError:
    # Fallback: определяем ROOT относительно скрипта
    ROOT = pathlib.Path(__file__).resolve().parent.parent

BACKUPS_DIR = backups_dir() if 'backups_dir' in dir() else ROOT / "_backups"
REFERENCE_DIR = BACKUPS_DIR / "_reference"
MAX_BACKUPS = 10

def _build_sources():
    """Собрать список папок для бэкапа из project-config.yml."""
    sources = [config_root()]
    for ext in extensions():
        ext_dir = ext.get("dir") if isinstance(ext, dict) else None
        if ext_dir:
            p = ROOT / ext_dir
            if p.exists():
                sources.append(p)
    return sources

SOURCES = _build_sources() if 'config_root' in dir() else [
    ROOT / "Конфигурация",
]

# Папки внутри Конфигурация/, исключаемые из бэкапа
EXCLUDE_DIRS = {"CommonTemplates"}


def _ignore_excluded(directory, contents):
    """Фильтр для shutil.copytree: исключает EXCLUDE_DIRS из корня config_root"""
    dir_path = pathlib.Path(directory)
    _cfg_root = config_root() if 'config_root' in dir() else ROOT / "Конфигурация"
    if dir_path == _cfg_root or dir_path.name == _cfg_root.name:
        return [c for c in contents if c in EXCLUDE_DIRS]
    return []


def ensure_reference():
    """Создать эталон CommonTemplates если его ещё нет"""
    _cfg_root = config_root() if 'config_root' in dir() else ROOT / "Конфигурация"
    ct_src = _cfg_root / "CommonTemplates"
    ct_ref = REFERENCE_DIR / "CommonTemplates"
    if ct_ref.exists():
        return  # Эталон уже есть
    if not ct_src.exists():
        return
    REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ct_src, ct_ref)
    print(f"  ✓ Эталон CommonTemplates создан: _backups/_reference/CommonTemplates/")


def make_backup(description: str = "") -> pathlib.Path:
    BACKUPS_DIR.mkdir(exist_ok=True)

    stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_dir = BACKUPS_DIR / stamp
    backup_dir.mkdir()

    print(f"=== Локальный бэкап: {stamp} ===")
    if description:
        print(f"    Задача: {description}")

    # Создать эталон CommonTemplates при первом бэкапе
    ensure_reference()

    for src in SOURCES:
        if src.exists():
            dst = backup_dir / src.name
            if src.name == "Конфигурация":
                shutil.copytree(src, dst, ignore=_ignore_excluded)
                print(f"  ✓ {src.name}/  →  _backups/{stamp}/{src.name}/  (без CommonTemplates/)")
            else:
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

    # Восстановить CommonTemplates из эталона
    ct_ref = REFERENCE_DIR / "CommonTemplates"
    ct_dst = ROOT / "Конфигурация" / "CommonTemplates"
    if ct_ref.exists() and not ct_dst.exists():
        shutil.copytree(ct_ref, ct_dst)
        print(f"  ✓ CommonTemplates/ восстановлена из эталона")
    elif not ct_ref.exists():
        print(f"  ⚠ Эталон CommonTemplates не найден в _backups/_reference/")

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
