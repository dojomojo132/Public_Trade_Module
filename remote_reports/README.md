# Отчёты PTM + переучёт — https://reports.dojomyassiste.uno

Полный хост того же сервиса, что уже крутится на VPS: вход (`ptm_session`), Настройки → туннель ИБ, отчёты, **переучёт `/inv`**.

Телефон: `https://reports.dojomyassiste.uno/inv`  
1С: `ib_location` + `X-Api-Key` из Настроек. Отдельный порт 8091 не нужен.

Исходников живого процесса в старом git-снимке не было — этот пакет и есть приложение отчётов с переучётом внутри.

## Запуск

```bash
cd remote_reports
python3 -m pip install -e ".[dev]"
export REPORTS_SECRET=long-random
export REPORTS_DB=data/app.db
python3 -m uvicorn app.main:create_app --factory --host 127.0.0.1 --port 8000
```

Первый логин при пустой базе создаёт учётку (как JSON API тестов). В UI есть `/register`.

| Переменная | Смысл |
|------------|--------|
| `REPORTS_SECRET` | Подпись cookie `ptm_session` |
| `REPORTS_DB` | SQLite |
| `REPORTS_COOKIE_SECURE` | `1` за HTTPS |
| `PORT` | порт uvicorn |

## Деплой на reports.dojomyassiste.uno

Заменить текущий uvicorn этим приложением (тот же домен, тот же reverse-proxy). SQLite пользователей живого сервиса **не совместима автоматически** (другая схема пароля) — либо зарегистрировать учётки заново, либо перенести `users`/`connections` вручную.

Если на VPS остаётся старый `main.py` и его нельзя снять: скопировать `app/inventory/` и вставить хуки:

```python
from app.inventory.schema import init_inventory_schema
from app.inventory.routes import inventory_routes
from app.inventory.ptm import ReportsPtmAdapter

init_inventory_schema(conn)
# routes: *inventory_routes()
app.state.inventory_user = current_user

def inventory_ptm(request, user):
    row = get_connection(conn, user["id"])
    if not row or not row["ib_location"]:
        return None
    return ReportsPtmAdapter(PtmClient(request.app.state.http, row["ib_location"], row["api_key"]))

app.state.inventory_ptm = inventory_ptm
```

На главной — карточка с `href: /inv`.

## Поведение переучёта

- Вход — `/login` отчётов.
- Кеш штрихкодов и черновики на пользователя.
- Скан не ходит в 1С. «Синхронизировать» тянет каталог и пушит dirty-черновики через `POST/PUT /inventories`.

## Тесты

```bash
cd remote_reports
python3 -m pytest
```
