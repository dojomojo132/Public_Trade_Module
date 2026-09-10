# Удалённый переучёт PTM

Телефон работает с кешем этого сервиса (поиск ШК, запись факта).  
1С синхронизируется периодически через `POST/PUT /hs/ptm/v1/inventories`.

Спека: `Документация/Спецификации/2026-09-10-удаленный-переучет.md`  
ADR: `Документация/API/ADR-002-remote-inventory-cache.md`

LAN `/hs/mobile/inv/*` этот сервис **не заменяет**.

## Запуск

```powershell
Set-Location D:\Git\Public_Trade_Module\remote_inventory
..\.venv\Scripts\python.exe -m pip install -e ".[dev]"
copy .env.example .env
..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8091
```

Открыть `http://127.0.0.1:8091/`. Первый логин создаёт учётку.

| Переменная | Смысл |
|------------|--------|
| `INV_SECRET` | Подпись cookie |
| `INV_PORT` | Порт, по умолчанию 8091 |
| `INV_DB` | SQLite, по умолчанию `data/app.db` |
| `PTM_BASE_URL` | `http://host:port/.../hs/ptm/v1` |
| `PTM_API_KEY` | Константа `Апи_Ключ` |
| `INV_PULL_SEC` | Период pull каталога (900) |
| `INV_PUSH_SEC` | Период push черновиков (180) |

## Туннель до 1С

Тот же SSH reverse, что для удалённых отчётов: Apache на ПК с ИБ, порт на VPS только localhost.

Пример `PTM_BASE_URL` в контейнере:

`http://host.docker.internal:18091/DB_MAGAZIN/hs/ptm/v1`

Поддомен/порт отдельные от отчётов (например `:8091` или `inv.example.com`).

## Тесты

```powershell
..\.venv\Scripts\python.exe -m pytest
```

## Docker

```bash
docker build -t ptm-remote-inventory .
docker run --rm -p 8091:8091 --env-file .env ptm-remote-inventory
```
