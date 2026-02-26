---
name: 1c-deploy
description: 'Полный workflow деплоя конфигурации 1С: бэкап → валидация → загрузка → обновление БД → конфигуратор. Откат при ошибках.'
---

# Деплой конфигурации 1С

## Защита данных (КРИТИЧНО!)

**Проблема:** Ошибки в XML/BSL могут сломать конфигурацию: пользователей ИБ, настройки MCP, данные.

**Решение:** Двухуровневый бэкап ПЕРЕД каждым изменением:
1. **Локальный бэкап** — копия XML/BSL в `_backups/` (не в git, 10 последних)
2. **DT-бэкап** — .dt копия ИБ через deploy-config.ps1

### Локальный бэкап

```powershell
# Создать бэкап:
python "D:\Git\Public_Trade_Module\scripts\_local_backup.py" "описание задачи"

# Список бэкапов:
python "D:\Git\Public_Trade_Module\scripts\_local_backup.py" --list

# Восстановить:
python "D:\Git\Public_Trade_Module\scripts\_local_backup.py" --restore 2026-02-25_143022
```

**Что копируется:** `Конфигурация/` и `MCP_Extension/`
**Хранение:** `_backups/YYYY-MM-DD_HHMMSS/` (в `.gitignore`, 10 последних)

### Git commit (ТОЛЬКО после подтверждения пользователем в ДИАЛОГЕ 2)

Шаг 1: Написать сообщение в `scripts/_commit_msg.txt` через `create_file`
Шаг 2: `git add -A; python "D:\Git\Public_Trade_Module\scripts\_git_commit.py"`

Формат: `FEAT: <заголовок>\n\n<подробный список>`
НИКОГДА не делать BACKUP-коммиты.

## Команды деплоя

```powershell
# Полный цикл: БЭКАП → валидация → загрузка → синтакс-контроль → обновление БД → конфигуратор
deploy-config.ps1 -Action Full

# Только бэкап
deploy-config.ps1 -Action Backup

# Откат
deploy-config.ps1 -Action Rollback

# Конфигуратор
deploy-config.ps1 -Action Designer

# Информация
deploy-config.ps1 -Action Info
```

## Порядок запуска (из-за PowerShell + кириллица)

```powershell
$script = Get-ChildItem -Path "D:\Git\Public_Trade_Module" -Recurse -Filter "deploy-config.ps1" | Select-Object -First 1
powershell -ExecutionPolicy Bypass -File $script.FullName -Action Full
```

## Пошаговый деплой (если DT-бэкап невозможен)

```powershell
$script = Get-ChildItem -Path "D:\Git\Public_Trade_Module" -Recurse -Filter "deploy-config.ps1" | Select-Object -First 1
powershell -ExecutionPolicy Bypass -File $script.FullName -Action Load -User "Admin"
powershell -ExecutionPolicy Bypass -File $script.FullName -Action Update -User "Admin"
# ОБЯЗАТЕЛЬНО открыть конфигуратор:
powershell -ExecutionPolicy Bypass -File $script.FullName -Action Designer -User "Admin"
```

> Check (синтакс-контроль, ~40 сек) пропускается — BSL проверяется через `get_errors`.

## Обработка ошибок деплоя

При ошибках загрузки агент ОБЯЗАН:
1. Найти блок `=== ОШИБКИ (для Copilot Agent) ===`
2. Прочитать ВСЕ секции: `--- ОШИБКИ ---`, `--- ПОЛНЫЙ ЛОГ 1С ---`
3. Разобрать КАЖДУЮ ошибку
4. Исправить XML/BSL → повторить деплой
5. Если не решается за 2 попытки → **ОТКАТИТЬ**

### Расшифровка типичных ошибок

| Ошибка | Причина | Решение |
|--------|---------|---------|
| `[ДИАЛОГ ЗАБЛОКИРОВАН]` | Критическая ошибка XML | validate-config.ps1, исправить ВСЕ [ОШИБКА] |
| `[ПУСТОЙ ЛОГ]` | Нет доступа к ИБ | Проверить путь, права, наличие 1cv8.exe |
| `[ТАЙМАУТ]` / `EXIT_CODE: -2` | XML критически повреждён | ОТКАТИТЬ немедленно |
| `{Модуль(строка, колонка)}: текст` | Ошибка BSL | Исправить BSL |
| `EXIT_CODE: 1` | Общая ошибка | Читать ПОЛНЫЙ ЛОГ |
| `EXIT_CODE: 10` | Бэкап не удался | Проверить доступ к ИБ |

## Правила отката

1. Деплой провалился и не решается за 2 попытки → ОТКАТИТЬ
2. EXIT_CODE = -2 (таймаут) → ОТКАТИТЬ немедленно
3. После отката:
   - `python scripts/_local_backup.py --restore <метка>`
   - `deploy-config.ps1 -Action Rollback`
   - Проанализировать причину
   - Критическая ошибка → записать в `Документация/КРИТИЧЕСКИЕ_ОШИБКИ.md`
4. НИКОГДА не пересоздавать ИБ (CREATEINFOBASE) без разрешения пользователя

## Схема

```
ЛОКАЛЬНЫЙ БЭКАП → DT-БЭКАП → ДЕПЛОЙ → УСПЕХ? → Маркер стабильности ✔
                                        ↓ НЕТ
                               ОТКАТ → Анализ → Записать в КРИТИЧЕСКИЕ_ОШИБКИ.md
                                        ↓
                               Исправить → ДЕПЛОЙ заново
```
