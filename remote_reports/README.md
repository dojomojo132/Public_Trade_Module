# Переучёт внутри https://reports.dojomyassiste.uno

Исходников отчётов в этом git-снимке нет: живой сервис уже на VPS (`uvicorn`, cookie `ptm_session`, Настройки → `ib_location` + ключ). Сюда кладётся **модуль**, который копируется в тот же процесс.

Телефон: `https://reports.dojomyassiste.uno/inv`  
1С: та же ссылка и ключ, что в **Настройки** отчётов (SSH-туннель). Новых URL ИБ в интернет не нужно. Отдельный порт 8091 не поднимаем.

## Что вставить в приложение отчётов

1. Скопировать каталог `app/inventory/` в корень приложения отчётов (рядом с `app/main.py`, клиентом PTM).

2. В старте (рядом с инициализацией SQLite):

```python
from app.inventory.schema import init_inventory_schema
init_inventory_schema(conn)
```

3. В список `routes` Starlette:

```python
from app.inventory.routes import inventory_routes
# ...
routes=[
    # существующие /login /settings /ib-status …
    *inventory_routes(),
]
```

4. После создания `app` — те же учётки и то же подключение к ИБ:

```python
from app.inventory.ptm import ReportsPtmAdapter

app.state.conn = conn
app.state.inventory_user = current_user  # cookie ptm_session, как на /settings

def inventory_ptm(request, user):
    row = get_connection(conn, user["id"])  # ib_location + api_key
    if not row or not row["ib_location"]:
        return None
    client = PtmClient(request.app.state.http, row["ib_location"], row["api_key"])
    return ReportsPtmAdapter(client)

app.state.inventory_ptm = inventory_ptm
```

`PtmClient` отчётов уже умеет `fetch_all_pages` / `ping_health`. Адаптер добавляет `POST/PUT /inventories`.

5. На главной — карточка в каталоге отчётов:

```python
{
    "id": "inventory",
    "title": "Переучёт",
    "blurb": "Скан в кеш, периодическая выгрузка черновика в 1С.",
    "href": "/inv",
}
```

6. В шапке ссылка «Переучёт» на `/inv` рядом с «Настройки».

Деплой: тот же контейнер/uvicorn, что уже отдаёт отчёты.

## Поведение

- Вход — `/login` отчётов (`username` / `password`), не отдельная учётка зала.
- Кеш штрихкодов и черновики **на пользователя** (у каждого своя ИБ из Настроек).
- Скан не ходит в 1С. Кнопка «Синхронизировать» тянет каталог и пушит dirty-черновики.
- Если ссылка на ИБ не задана: `/inv/status` → `ibConfigured: false`, `/inv/sync` → 503.

## Тесты модуля (без VPS)

```bash
cd remote_reports
python3 -m pip install -e ".[dev]"
python3 -m pytest
```

Демо-хост (`app.inventory.demo_app`) повторяет cookie `ptm_session` и JSON/form POST `/login` живого сервиса.
