# Миграция существующего проекта на актуальную версию фреймворка

> **Для агента:** Применить все изменения ниже к существующему проекту 1С с ранее установленным фреймворком.
> Каждый раздел описывает конкретный файл, что изменилось и как обновить.

---

## Обзор изменений

| Категория | Файл | Тип изменения |
|-----------|------|---------------|
| Skill | `.github/skills/1c-deploy/SKILL.md` | Исправление hardcoded абсолютных путей → относительные |
| Агенты | `.github/agents/*.agent.md` | Полное обновление содержимого (скопировать из `_framework_dist`) |
| Инструкции | `.github/instructions/*.md` | Полное обновление (скопировать из `_framework_dist`) |
| Скрипты | `scripts/verify_setup.py` | Новый файл (был `_verify_setup.py`) |

---

## 1. КРИТИЧЕСКОЕ: Исправить пути в `1c-deploy` SKILL

**Файл:** `.github/skills/1c-deploy/SKILL.md`

Абсолютные пути `D:\Git\Public_Trade_Module\...` в SKILL.md были PTM-специфичными и ломали портабельность. Заменить на относительные.

### Замена 1: Локальный бэкап (блок команд)

**Найти:**
```
python "D:\Git\Public_Trade_Module\scripts\_local_backup.py" "описание задачи"

# Посмотреть список бэкапов:
python "D:\Git\Public_Trade_Module\scripts\_local_backup.py" --list
```

**Заменить на:**
```
python scripts/_local_backup.py "описание задачи"

# Посмотреть список бэкапов:
python scripts/_local_backup.py --list
```

### Замена 2: Откат файлов

**Найти:**
```
python "D:\Git\Public_Trade_Module\scripts\_local_backup.py" --restore <метка>
```

**Заменить на:**
```
python scripts/_local_backup.py --restore <метка>
```

### Замена 3: Git commit

**Найти:**
```
git add -A; python "D:\Git\Public_Trade_Module\scripts\_git_commit.py"
```

**Заменить на:**
```
git add -A; python scripts/_git_commit.py
```

---

## 2. Обновить агентов (полное обновление)

**Файлы:** `.github/agents/`

Все агенты получили обновления. Скопировать каждый файл из `_framework_dist/.github/agents/`:

```
1c-architect.agent.md
1c-coder.agent.md
1c-deployer.agent.md
1c-form-builder.agent.md
orchestrator.agent.md
```

> **Важно:** После копирования — `project-config.yml` не трогать. Агенты используют `{config.*}` плейсхолдеры которые читаются из `project-config.yml`.

---

## 3. Обновить инструкции

**Файлы:** `.github/instructions/`

Скопировать из `_framework_dist/.github/instructions/`:

```
bsl.instructions.md
xml-1c.instructions.md
agent-bus-worker.instructions.md
```

---

## 4. Обновить skills

**Файлы:** `.github/skills/`

Скопировать из `_framework_dist/.github/skills/` каждую папку:

```
1c-deploy/SKILL.md
1c-deploy/SKILL.md        ← уже обновлён в шаге 1
1c-metadata-check/SKILL.md
1c-bsl-review/SKILL.md
1c-form-generator/SKILL.md
1c-debug/SKILL.md
1c-report/SKILL.md
```

---

## 5. Обновить copilot-instructions.md

**Файл:** `.github/copilot-instructions.md`

> ⚠️ Этот файл **НЕ копируется напрямую** — он содержит проектоспецифичные значения.
> Вместо этого нужно обновить только те секции, которые изменились.

### Изменение 5.1: Section 3, Фаза 5 — Замер производительности (если отсутствует)

Добавить в блок `ФАЗА 5:` после `ФАЗА 4: МОНИТОРИНГ`:
```
ФАЗА 5: ЗАМЕР ПРОИЗВОДИТЕЛЬНОСТИ (ОБЯЗАТЕЛЬНО)
  → Записать в Документация/ЖУРНАЛ_ПРОИЗВОДИТЕЛЬНОСТИ.md:
    - Время каждой фазы (Бэкап, Анализ, Реализация, QC, Деплой, Мониторинг)
    - Метрики деплоя (validate, load, check, update, monitor в секундах)
    - Проблемы: описание, фаза, решение, потерянное время
    - Итоговое время задачи
    - Использование контекста: tool_calls, subagent_calls, files_read,
      lines_read, files_edited, terminal_commands, mcp_calls, searches, by_phase
```

### Изменение 5.2: Section 3, Фаза R — Сверка конфигурации (если отсутствует)

Добавить после Фазы 5:
```
ФАЗА R: СВЕРКА КОНФИГУРАЦИИ (отдельный workflow)
  → Когда: пользователь вручную изменил конфигурацию в конфигураторе
  → Dump ИБ → файлы → Запрос списка объектов у пользователя
  → MCP-анализ каждого объекта (структура, связи, формы)
  → Obsidian: обновить/создать заметки затронутых объектов
  → validate-config.ps1 → ДИАЛОГ 2
  → Подробности → orchestrator.agent.md, Фаза R
```

### Изменение 5.3: Section 3, Фаза 2, блок ДЕПЛОЙ — маршрутизация по типу объекта (если отсутствует)

Обновить блок `ФАЗА 2: ДЕПЛОЙ` до:
```
ФАЗА 2: ДЕПЛОЙ
  ⚡ Если объект в РАСШИРЕНИИ (Reports/DataProcessors/CommonModules расширения):
     → python scripts/deploy_ext.py --ext <ИмяРасширения> --action Full (~15 сек)
  🐢 Если объект в ОСНОВНОЙ КОНФИГУРАЦИИ (Documents/Catalogs/Registers):
     → validate-config.ps1 → deploy-config.ps1 -Action Full (~100 сек)
  → Разбор ошибок → Исправление → Повтор (макс. 2 попытки → ОТКАТ)
```

---

## 6. Обновить scripts/

**Новый файл:** `scripts/verify_setup.py` (был `_verify_setup.py` — переименован)

Скопировать из `_framework_dist/scripts/verify_setup.py`.

Если в старом проекте есть `scripts/_verify_setup.py` — это старая версия, можно удалить.

---

## 7. Обновить hooks

**Файлы:** `.github/hooks/`

Скопировать из `_framework_dist/.github/hooks/`:

```
guardrails.json
scripts/coder_post_edit.py
scripts/deployer_post_check.py
scripts/deployer_pre_check.py
scripts/form_builder_post_create.py
scripts/post_tool_audit.py
scripts/pre_edit_check.py
scripts/session_start.py
```

---

## Чеклист для агента

После применения всех изменений:

```
☐ 1. .github/skills/1c-deploy/SKILL.md — пути исправлены на относительные
☐ 2. .github/agents/*.agent.md — скопированы из _framework_dist
☐ 3. .github/instructions/*.md — скопированы из _framework_dist
☐ 4. .github/skills/*/SKILL.md — скопированы из _framework_dist
☐ 5. .github/copilot-instructions.md — проверены секции §3 (Фазы 5/R/2)
☐ 6. scripts/verify_setup.py — добавлен новый файл
☐ 7. .github/hooks/ — скопированы из _framework_dist
☐ 8. get_errors на все .bsl файлы — 0 ошибок
```
