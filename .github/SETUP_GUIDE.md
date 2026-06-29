# Инструкция развёртывания 1С Copilot Agent Framework

> **Для агента:** Следуй этой инструкции шаг за шагом.  
> **Результат:** Новый проект 1С с полностью настроенным агентным фреймворком.

---

## Обзор

Фреймворк состоит из двух слоёв:
1. **`.github/`** — агенты, скиллы, инструкции, промпты, хуки (Copilot-интеграция)
2. **`scripts/`** — Python-утилиты (деплой, бэкап, валидация, мониторинг)

Для нового проекта настраивается **ОДИН файл** — `.github/project-config.yml`.
Всё остальное параметризовано через `{config.*}` ссылки.

---

## Предварительные требования

| Компонент | Минимальная версия | Проверка |
|-----------|-------------------|----------|
| 1С:Предприятие | 8.3.24+ | `"C:\Program Files\1cv8\*\bin\1cv8.exe" /version` |
| Python | 3.10+ | `python --version` |
| VS Code | 1.100+ | `code --version` |
| GitHub Copilot | Agent mode активен | Настройки → Features → Chat Agent |
| Git | 2.30+ | `git --version` |

### Опционально (для расширенных функций)
- **1С MCP-сервер** — для проверки метаданных ИБ (без него работа по файлам на диске)
- **Obsidian + MCP** — для Knowledge Graph (без него граф не обновляется)
- **RDBG Debug MCP** — для отладки BSL через VS Code

---

## Шаг 1. Создать структуру проекта

```
<корень_проекта>/
├── .github/                 ← Копировать целиком из фреймворка
│   ├── project-config.yml   ← Заполнить для нового проекта (Шаг 2)
│   ├── copilot-instructions.md
│   ├── agents/              (5 агентов)
│   ├── skills/              (6 скиллов)
│   ├── instructions/        (3 инструкции)
│   ├── prompts/             (8 промптов)
│   └── hooks/               (guardrails.json + 7 Python-скриптов)
├── scripts/                 ← Копировать ядро из фреймворка (Шаг 3)
├── <Конфигурация>/          ← Папка выгрузки конфигурации 1С
├── <Документация>/          ← Документация проекта
│   ├── Валидация/           ← PowerShell-скрипты деплоя
│   ├── Шаблоны/             ← XML-шаблоны объектов 1С
│   ├── Технические_стандарты/
│   └── КРИТИЧЕСКИЕ_ОШИБКИ.md
├── <Тесты>/                 ← YAxUnit тесты
├── _backups/                ← Локальные бэкапы (.gitignore)
└── .gitignore
```

---

## Шаг 2. Заполнить `project-config.yml`

Это **единственный файл**, который нужно настроить. Открой `.github/project-config.yml` и замени значения:

```yaml
project:
  name: "МойПроект"                              # Короткое имя (для логов)
  full_name: "Полное название проекта"           # Полное название
  platform: "8.3.27"                             # Версия платформы 1С

paths:
  infobase: "D:\\Bases\\МояБаза"                 # Путь к файловой ИБ
  config_root: "Конфигурация"                    # Папка выгрузки (относительно корня)
  backups: "_backups"                            # Папка бэкапов
  docs: "Документация"                           # Папка документации
  validation: "Документация/Валидация"           # PowerShell-скрипты
  standards: "Документация/Технические_стандарты" # Стандарты 1С
  templates: "Документация/Шаблоны"              # XML-шаблоны
  tests: "Тесты"                                 # Тесты

mcp:
  onec:
    prefix: "mcp_1c-mcp"                        # Префикс 1С MCP-инструментов
    health_check: "get_session_info"             # Инструмент health check
  obsidian:
    enabled: false                               # true если используется Obsidian
    prefix: "mcp_obsidian-vaul"                  # Префикс Obsidian MCP
    vault: "НазваниеVault"                       # Имя vault
    project_folder: "МойПроект"                  # Папка в vault
  debug:
    enabled: false                               # true если используется RDBG
    prefix: "mcp_debug"                          # Префикс Debug MCP

extensions: []                                   # Расширения конфигурации (если есть)
# Пример:
# extensions:
#   - name: "МоёРасширение"
#     dir: "МоёРасширение_Extension"

resources:
  prefix: "myproject"                            # Протокол MCP ресурсов
  available:
    - "datamodel"
    - "registers"
    - "business-logic"

spec:
  enabled: false                                 # true если ведётся спецификация
  path: ""                                       # Путь к XML-спецификации

monitoring:
  backup_prefix: "backup"                        # Префикс DT-бэкапов
  process_filter: ""                             # Фильтр процесса в ТЖ
```

### Обязательные поля (минимум для работы)

| Поле | Описание | Пример |
|------|----------|--------|
| `project.name` | Имя проекта | `"ERP"` |
| `paths.infobase` | Путь к файловой ИБ | `"D:\\Bases\\ERP"` |
| `paths.config_root` | Папка выгрузки | `"Конфигурация"` |
| `mcp.onec.prefix` | Префикс MCP (из settings.json) | `"mcp_1c-mcp"` |

### Как узнать MCP-префикс

1. Открой `.vscode/settings.json` или глобальные настройки
2. Найди секцию `mcp.servers`
3. Имя сервера + `mcp_` = префикс. Пример: сервер `1c-mcp` → префикс `mcp_1c-mcp`

---

## Шаг 3. Скопировать скрипты

### Обязательные скрипты (ядро фреймворка)

Скопируй из `scripts/` в целевой проект:

| Файл | Назначение |
|------|-----------|
| `_project_config.py` | Читатель конфига (все скрипты зависят от него) |
| `_ps_wrapper.py` | Python-обёртка для PowerShell (решает кириллицу) |
| `_local_backup.py` | Локальный бэкап XML/BSL файлов |
| `_git_commit.py` | Git commit через Python (обход кириллицы) |
| `deploy_ext.py` | Деплой расширений конфигурации |
| `_generate_form.py` | Генератор форм (fallback, если не через Конфигуратор) |

### Обязательные PowerShell-скрипты

Скопируй в `<docs>/Валидация/`:

| Файл | Назначение |
|------|-----------|
| `deploy-config.ps1` | Основной деплой (Load + Check + UpdateDB) |
| `validate-config.ps1` | Валидация XML перед деплоем |
| `monitor-errors.ps1` | Мониторинг ошибок (ТЖ + ЖР) |

### ⚠️ Настройка PowerShell-скриптов

В каждом `.ps1` скрипте найди и обнови:
- **Путь к ИБ** (`$InfoBasePath`)
- **Путь к конфигурации** (`$ConfigPath`)
- **Путь к бэкапам** (`$BackupPath`)

Или, если скрипты уже поддерживают `_ps_wrapper.py`, все пути определяются автоматически.

---

## Шаг 4. Создать документацию

Создай обязательные файлы:

```bash
# Создать структуру папок
mkdir <docs>
mkdir <docs>/Валидация
mkdir <docs>/Шаблоны
mkdir <docs>/Технические_стандарты
mkdir <docs>/Спецификации  # если spec.enabled = true
mkdir _backups
mkdir <тесты>
```

### Обязательные документы

| Файл | Содержимое |
|------|-----------|
| `<docs>/КРИТИЧЕСКИЕ_ОШИБКИ.md` | Пустой файл с заголовком. Фреймворк будет дописывать правила-предохранители |
| `<docs>/WORKFLOW_КОНФИГУРАТОР_ПЛЮС_АГЕНТ.md` | Описание workflow «Конфигуратор + Агент» |

> **Метрики выполнения задач** фиксируются парсером в `<vault>/99-Meta/Sessions/<datetime>__<agent>__<task>.md` (frontmatter `duration_min`, `task_link`). Карта vault: `.github/VAULT_STRUCTURE.md`.

### Шаблоны XML (рекомендуется)

Размести в `<docs>/Шаблоны/`:
- `template-catalog.xml` — шаблон справочника
- `template-document.xml` — шаблон документа
- `template-report.xml` — шаблон отчёта
- `template-dataprocessor.xml` — шаблон обработки
- `template-enum.xml` — шаблон перечисления

---

## Шаг 5. Настроить `.gitignore`

Добавь в `.gitignore`:

```gitignore
# Бэкапы
_backups/

# 1С выгрузки
*.dt
*.cf
*.log

# Временные файлы скриптов
_*_out.txt
_*_err.txt
_commit_msg.txt

# Python
__pycache__/
*.pyc

# Логи
logs/
```

---

## Шаг 6. Первый запуск — выгрузка конфигурации

```bash
# 1. Выгрузить конфигурацию из ИБ в файлы
python scripts/_ps_wrapper.py deploy -Action Dump

# 2. Проверить валидность
python scripts/_ps_wrapper.py validate

# 3. Убедиться что файлы появились
ls <config_root>/
```

---

## Шаг 7. Проверка работоспособности

### 7.1 Проверить конфиг-ридер
```bash
python -c "import sys; sys.path.insert(0,'scripts'); from _project_config import *; print('OK:', get('project.name'), '| IB:', infobase_path())"
```
Ожидается: `OK: МойПроект | IB: D:\Bases\МояБаза`

### 7.2 Проверить бэкап
```bash
python scripts/_local_backup.py "тестовый бэкап"
python scripts/_local_backup.py --list
```

### 7.3 Проверить MCP (если настроен)
В VS Code Chat:
```
@1c-metadata-check Проверь существование любого справочника
```

### 7.4 Проверить агента
В VS Code Chat:
```
/1c-new-task Привет, покажи статус
```

---

## Шаг 8. Опциональные настройки

### MCP-серверы

Настройка в `.vscode/settings.json` (или глобально):

```jsonc
{
  "mcp": {
    "servers": {
      "1c-mcp": {
        "type": "stdio",
        "command": "python",
        "args": ["путь/к/mcp_server.py"],
        "env": {
          "INFOBASE_PATH": "D:\\Bases\\МояБаза"
        }
      }
    }
  }
}
```

### Obsidian Knowledge Graph

1. Установить Obsidian + MCP-плагин
2. В `project-config.yml` → `mcp.obsidian.enabled: true`
3. Создать папку проекта в vault
4. Агент будет автоматически обновлять заметки

### RDBG-отладка

1. Настроить `scripts/debug/debug_config.json`
2. В `project-config.yml` → `mcp.debug.enabled: true`

### Расширения конфигурации

Добавить в `project-config.yml`:
```yaml
extensions:
  - name: "МоёРасширение"
    dir: "Расширение_Extension"
```
Папка будет автоматически бэкапиться и деплоиться.

### Agent Bus (параллельная разработка)

Если используется шина задач для нескольких агентов — см. `instructions/agent-bus-worker.instructions.md`.

---

## Манифест файлов фреймворка

### `.github/` (копировать целиком)

```
.github/
├── project-config.yml           ★ НАСТРОИТЬ
├── copilot-instructions.md      автоматически
├── agents/
│   ├── orchestrator.agent.md    координатор задач
│   ├── 1c-coder.agent.md       BSL-разработчик
│   ├── 1c-architect.agent.md   проектировщик
│   ├── 1c-form-builder.agent.md формы (BSL)
│   └── 1c-deployer.agent.md    деплой + диагностика
├── skills/
│   ├── 1c-deploy/SKILL.md      деплой, бэкап, откат
│   ├── 1c-metadata-check/SKILL.md MCP-проверки
│   ├── 1c-bsl-review/SKILL.md  ревью BSL
│   ├── 1c-form-generator/SKILL.md генерация форм (fallback)
│   ├── 1c-debug/SKILL.md       RDBG-отладка
│   └── 1c-report/SKILL.md      создание отчётов
├── instructions/
│   ├── bsl.instructions.md      → автоматически при *.bsl
│   ├── xml-1c.instructions.md   → автоматически при *.xml
│   └── agent-bus-worker.instructions.md
├── prompts/
│   ├── 1c-new-task.prompt.md    полный цикл задачи
│   ├── 1c-create-document.prompt.md
│   ├── 1c-create-catalog.prompt.md
│   ├── 1c-create-form.prompt.md
│   ├── 1c-fix-errors.prompt.md
│   ├── 1c-fix-deploy.prompt.md
│   ├── 1c-review.prompt.md
│   └── 1c-validate-config.prompt.md
└── hooks/
    ├── guardrails.json          конфигурация хуков
    └── scripts/                 7 Python-скриптов guardrails
```

### `scripts/` (копировать ядро)

```
scripts/
├── _project_config.py    ★ ЯДРО — читатель конфига
├── _ps_wrapper.py        ★ ЯДРО — обёртка PowerShell
├── _local_backup.py      ★ ЯДРО — локальный бэкап
├── _git_commit.py        ★ ЯДРО — git commit helper
├── deploy_ext.py         ★ ЯДРО — деплой расширений
└── _generate_form.py     опционально — генератор форм
```

### `<docs>/Валидация/` (копировать)

```
<docs>/Валидация/
├── deploy-config.ps1     ★ ЯДРО — основной деплой
├── validate-config.ps1   ★ ЯДРО — валидация XML
└── monitor-errors.ps1    ★ ЯДРО — мониторинг ошибок
```

---

## Troubleshooting

| Проблема | Решение |
|----------|---------|
| `_project_config.py` не находит конфиг | Проверь что `.github/project-config.yml` существует |
| Кириллица ломается в путях | Используй `python scripts/_ps_wrapper.py` вместо прямого `.ps1` |
| MCP не отвечает | Проверь `mcp.onec.prefix` в конфиге, перезапусти MCP-сервер |
| Деплой заканчивается таймаутом | ИБ заблокирована — закрой Конфигуратор и 1С:Предприятие |
| `get_errors` не находит ошибки | Убедись что файлы на диске актуальны (Dump) |
| Агент не читает конфиг | `{config.*}` — это placeholder для агента, не Python-переменная |

---

## Чеклист развёртывания

- [ ] `.github/` скопирован целиком
- [ ] `project-config.yml` заполнен (минимум: name, infobase, config_root, mcp.onec.prefix)
- [ ] `scripts/` — 6 файлов ядра скопированы
- [ ] `<docs>/Валидация/` — 3 PowerShell-скрипта скопированы и настроены
- [ ] `<docs>/КРИТИЧЕСКИЕ_ОШИБКИ.md` создан
- [ ] `.gitignore` обновлён
- [ ] `python scripts/_ps_wrapper.py deploy -Action Dump` выполнен успешно
- [ ] `python scripts/_ps_wrapper.py validate` → 0 ошибок
- [ ] Конфиг-ридер работает: `python -c "from scripts._project_config import *; print(get('project.name'))"`
- [ ] Первый бэкап создан: `python scripts/_local_backup.py "initial"`
