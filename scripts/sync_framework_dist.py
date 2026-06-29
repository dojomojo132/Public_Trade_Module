"""
sync_framework_dist.py
Синхронизирует актуальные файлы фреймворка в папку _framework_dist/.
Запуск: python scripts/sync_framework_dist.py
"""
import shutil
import os
from pathlib import Path

ROOT = Path(__file__).parent.parent
DIST = ROOT / "_framework_dist"

# ── Шаблон project-config.yml (чистый, без PTM-данных) ────────────────────────
BLANK_CONFIG = """\
# ═══════════════════════════════════════════════════════════════════════════════
# Конфигурация проекта 1С для Copilot Agent Framework
# ═══════════════════════════════════════════════════════════════════════════════
# Единственный файл, который нужно заполнить при подключении фреймворка к новому проекту.
# Все агенты, скиллы и скрипты читают настройки отсюда.
#
# Как подключить к новому проекту:
#   1. Скопировать содержимое этой папки в корень нового проекта
#   2. Заполнить ЭТОТ файл (project-config.yml)
#   3. Запустить: python scripts/_ps_wrapper.py deploy -Action Dump
# ═══════════════════════════════════════════════════════════════════════════════

project:
  name: "МойПроект"                             # Короткое имя (для логов, тегов)
  full_name: "Полное название конфигурации"      # Полное название
  platform: "8.3.27"                            # Версия платформы 1С

# ── Пути ──────────────────────────────────────────────────────────────────────
paths:
  infobase: "D:\\\\Bases\\\\МояИБ"               # Путь к файловой ИБ (ОБЯЗАТЕЛЬНО)
  config_root: "Конфигурация"                    # Папка выгрузки (относительно корня проекта)
  backups: "_backups"                            # Папка локальных бэкапов
  docs: "Документация"                           # Папка документации
  validation: "Документация/Валидация"           # PowerShell скрипты деплоя
  standards: "Документация/Технические_стандарты" # Стандарты 1С
  templates: "Документация/Шаблоны"              # XML-шаблоны
  tests: "Тесты"                                 # Папка тестов

# ── MCP серверы ───────────────────────────────────────────────────────────────
# После заполнения этого блока выполни:
#   python scripts/_generate_mcp.py
# Скрипт создаст .vscode/mcp.json с включёнными серверами автоматически.
mcp:

  # 1С HTTP MCP — проверка метаданных ИБ, инспекция объектов
  # Нужен: HTTP-сервис MCP опубликован в ИБ
  # URL: http://localhost/<имя_публикации>/hs/mcp/mcp
  onec:
    prefix: "mcp_1c-mcp"                        # Префикс MCP-инструментов 1С
    health_check: "get_session_info"             # Инструмент для health check
    url: ""                                      # URL SSE-сервера 1С MCP (оставь "" если не используется)

  # Управление Конфигуратором — скриншоты, клики, навигация в окне Конфигуратора
  # Нужен: pip install pywinauto Pillow mss pywin32
  configurator:
    enabled: false                               # true — включить MCP управления Конфигуратором

  # RDBG Отладчик BSL — пошаговая отладка BSL через VS Code
  debug:
    enabled: false                               # true — включить RDBG отладку
    prefix: "mcp_debug"                          # Префикс MCP-инструментов отладки

  # Obsidian Knowledge Graph — заметки объектов конфигурации
  # Нужен: плагин Obsidian Local REST API (https://github.com/coddingtonbear/obsidian-local-rest-api)
  obsidian:
    enabled: false                               # true — включить интеграцию с Obsidian
    prefix: "mcp_obsidian-vaul"                  # Префикс MCP-инструментов Obsidian
    vault: "НазваниеVault"                       # Имя vault в Obsidian
    project_folder: "МойПроект"                  # Папка проекта внутри vault
    url: "http://localhost:3001/mcp"             # URL Obsidian REST API (обычно не меняется)
    token: ""                                    # Bearer токен из настроек плагина

# ── Расширения конфигурации ───────────────────────────────────────────────────
extensions: []
# Пример расширений:
# extensions:
#   - name: "МоёРасширение"
#     dir: "Расширение_Extension"

# ── MCP Resources (опционально) ──────────────────────────────────────────────
resources:
  prefix: "myproject"                            # Протокол для ресурсов: myproject://datamodel
  available:
    - "datamodel"
    - "registers"
    - "business-logic"

# ── Спецификация (опционально) ────────────────────────────────────────────────
spec:
  enabled: false                                 # true — использовать XML-спецификацию
  path: ""                                       # Путь к XML-спецификации (относительно корня)

# ── Мониторинг ────────────────────────────────────────────────────────────────
monitoring:
  backup_prefix: "backup"                        # Префикс DT-бэкапов
  process_filter: ""                             # Фильтр процесса в ТЖ (например "My.Config")
"""

# ── Ядро scripts/ — только эти файлы копируются в дистрибутив ─────────────────
CORE_SCRIPTS = [
    "_project_config.py",
    "_ps_wrapper.py",
    "_local_backup.py",
    "_git_commit.py",
    "_obsidian_sync.py",
    "_generate_form.py",
    "verify_setup.py",
    "_generate_mcp.py",
    "deploy_ext.py",
    "configurator_bridge.py",
]

# ── Корневые файлы (не перезаписываются — только если не существуют) ──────────
ROOT_ONCE_FILES = [
    # Файлы, которые СОЗДАЮТСЯ один раз при первом развёртывании.
    # При повторной синхронизации НЕ перезаписываются (пользователь мог их изменить).
    ".vscode/settings.json",
    ".vscode/mcp.json",
    ".vscode/extensions.json",
    ".vscode/tasks.json",
    ".vscode/launch.json",
    "requirements.txt",
    "package.json",
    "SETUP.bat",
]

CORE_SCRIPT_DIRS = [
    "debug",
]

# Файлы, которые НЕ копируются из debug/ (тестовые/диагностические)
EXCLUDE_FROM_DEBUG = {
    f for f in [
        "_proxy_log.txt", "_test_alias.py", "_test_alias2.py",
        "_test_autoattach.py", "_test_autoattach2.py", "_test_combined.py",
        "_test_correct_path.py", "_test_deep_diag.py", "_test_e2e.py",
        "_test_full_diag.py", "_test_full_response.py", "_test_init2.py",
        "_test_init_variants.py", "_test_keepalive.py", "_test_launch_diag.py",
        "_test_launch_variants.py", "_test_netstat.py", "_test_ping_compare.py",
        "_test_proxy.py", "_test_real_ib.py", "_test_session_life.py",
        "_test_thick_client.py",
    ]
}


def sync_dir(src: Path, dst: Path, exclude_files: set[str] = None):
    """Рекурсивно копирует src -> dst, пропуская __pycache__ и exclude_files."""
    exclude_files = exclude_files or set()
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        if item.name == "__pycache__":
            continue
        if item.name in exclude_files:
            continue
        d = dst / item.name
        if item.is_dir():
            sync_dir(item, d)
        else:
            shutil.copy2(item, d)
            print(f"  COPY {item.relative_to(ROOT)} -> {d.relative_to(ROOT)}")


def post_process_instructions(dist_file: Path):
    """Заменяет PTM-специфичные строки на {config.*} плейсхолдеры в дистрибутиве copilot-instructions.md."""
    if not dist_file.exists():
        return
    text = dist_file.read_text(encoding="utf-8")
    replacements = [
        # Имя анализатора (PTM-специфичное имя -> генеричное)
        ("_ptm_analyze.py", "_1c_analyze.py"),
        # Примеры расширений (заменяем на генеричные)
        ("--ext PTM_Analytics ", "--ext <ИмяРасширения> "),
        ("--ext MCP_\u0421\u0435\u0440\u0432е\u0440 ", "--ext <ИмяРасширения> "),
        # Путь к спецификации (полный путь)
        (
            "Документация/Спецификации/ТЕХНИЧЕСКАЯ СПЕЦИФИКАЦИЯ КОНФИГУРАЦИИ PTM (Public Trade Module).xml",
            "{config.spec.path}",
        ),
        # Obsidian vault и папка проекта
        (
            "Vault `DojoMojo_Obsidian` -> `PTM/` (localhost:3001)",
            "Vault `{config.mcp.obsidian.vault}` -> `{config.mcp.obsidian.project_folder}/` (localhost:3001)",
        ),
        (
            "Vault `DojoMojo_Obsidian` \u2192 `PTM/` (localhost:3001)",
            "Vault `{config.mcp.obsidian.vault}` \u2192 `{config.mcp.obsidian.project_folder}/` (localhost:3001)",
        ),
        # MCP ресурсы
        ("ptm://datamodel", "{config.resources.prefix}://datamodel"),
        ("ptm://registers", "{config.resources.prefix}://registers"),
        ("ptm://business-logic", "{config.resources.prefix}://business-logic"),
        # Финальный чеклист и трекинг сессий
        ("PTM/ \u0432 vault DojoMojo_Obsidian", "{config.mcp.obsidian.project_folder}/ \u0432 vault {config.mcp.obsidian.vault}"),
        ("Obsidian `PTM/\u0421\u0435\u0441\u0441\u0438\u0438/`", "Obsidian `{config.mcp.obsidian.project_folder}/\u0421\u0435\u0441\u0441\u0438\u0438/`"),
    ]
    changed = False
    for old, new in replacements:
        if old in text:
            text = text.replace(old, new)
            changed = True
    if changed:
        dist_file.write_text(text, encoding="utf-8")
        print(f"  PATCH {dist_file.relative_to(ROOT)} (PTM -> config placeholders)")


def main():
    print("=" * 60)
    print("sync_framework_dist.py — синхронизация дистрибутива")
    print("=" * 60)

    # 1. Синхронизировать .github/ -> _framework_dist/.github/
    #    Кроме project-config.yml (заменяем чистым шаблоном)
    print("\n[1/4] Синхронизация .github/ ...")
    src_github = ROOT / ".github"
    dst_github = DIST / ".github"
    sync_dir(src_github, dst_github, exclude_files={"project-config.yml"})

    # Пост-обработка: заменить PTM-специфику на {config.*} плейсхолдеры
    post_process_instructions(dst_github / "copilot-instructions.md")

    # 2. Записать чистый шаблон project-config.yml
    print("\n[2/4] Записываю чистый project-config.yml ...")
    config_path = dst_github / "project-config.yml"
    config_path.write_text(BLANK_CONFIG, encoding="utf-8")
    print(f"  WRITE {config_path.relative_to(ROOT)}")

    # 3. Синхронизировать ядро scripts/
    print("\n[3/4] Синхронизация ядра scripts/ ...")
    src_scripts = ROOT / "scripts"
    dst_scripts = DIST / "scripts"
    dst_scripts.mkdir(parents=True, exist_ok=True)

    for name in CORE_SCRIPTS:
        src = src_scripts / name
        if src.exists():
            dst = dst_scripts / name
            shutil.copy2(src, dst)
            print(f"  COPY scripts/{name}")
        else:
            print(f"  SKIP scripts/{name} (не найден)")

    for dir_name in CORE_SCRIPT_DIRS:
        src = src_scripts / dir_name
        exclude = EXCLUDE_FROM_DEBUG if dir_name == "debug" else None
        if src.exists():
            sync_dir(src, dst_scripts / dir_name, exclude_files=exclude)
        else:
            print(f"  SKIP scripts/{dir_name}/ (не найдена)")

    # 4. Убедиться что структура папок существует
    print("\n[4/4] Проверка структуры папок ...")
    for folder in [
        DIST / "Конфигурация",
        DIST / "Документация" / "Спецификации",
        DIST / "Тесты",
        DIST / "_backups",
    ]:
        folder.mkdir(parents=True, exist_ok=True)
        keeper = folder / ".gitkeep"
        if not keeper.exists():
            keeper.touch()
            print(f"  MKDIR {folder.relative_to(ROOT)}")

    # .gitignore из шаблона
    gi_src = DIST / ".gitignore.template"
    gi_dst = DIST / ".gitignore"
    if gi_src.exists() and not gi_dst.exists():
        shutil.copy2(gi_src, gi_dst)
        print(f"  COPY .gitignore.template -> .gitignore")

    # .vscode/ и прочие однократные файлы — обновляются всегда из текущего проекта
    # (пользователь в _framework_dist их редактирует вручную; мы не перезаписываем)
    vscode_src = ROOT / ".vscode"
    vscode_dst = DIST / ".vscode"
    VSCODE_ONLY = {"settings.json", "extensions.json", "tasks.json", "launch.json", "mcp.json"}
    if vscode_src.exists():
        vscode_dst.mkdir(parents=True, exist_ok=True)
        for f in VSCODE_ONLY:
            src = vscode_src / f
            dst = vscode_dst / f
            # Не перезаписываем если уже есть в dist (пользователь мог настроить)
            if src.exists() and not dst.exists():
                shutil.copy2(src, dst)
                print(f"  INIT  .vscode/{f}")
            elif not dst.exists():
                print(f"  SKIP  .vscode/{f} (нет в источнике)")

    print("\n" + "=" * 60)
    print("Готово! Папка _framework_dist/ синхронизирована.")
    print()
    print("Что делать дальше:")
    print("  1. Скопируй _framework_dist/ в корень нового проекта")
    print("  2. Открой .github/project-config.yml и заполни:")
    print("       project.name, paths.infobase")
    print("  3. Запусти: python scripts/_ps_wrapper.py deploy -Action Dump")
    print("  4. В VS Code Chat напиши: /1c-new-task Запустить настройку")
    print("=" * 60)


if __name__ == "__main__":
    main()
