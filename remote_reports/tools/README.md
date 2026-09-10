# tools/ — локальные утилиты для разработки

## `ptm_api_emulator.py` — эмулятор 1С PTM_API

Поднимает HTTP-сервер, повторяющий контракт публикации 1С `/hs/ptm/v1`
(см. `Документация/API/openapi-v1.yaml`), чтобы `remote_reports` можно было
тестировать **без живой информационной базы**:

- авторизация по заголовку `X-Api-Key` (кроме `/health`);
- оболочка списков `items/count/limit/offset/total` с пагинацией;
- обязательный период на `/sales` (иначе `400 period_required`);
- идемпотентный `POST /inventories` (upsert по `externalId`) и `PUT /inventories/{id}`;
- демо-каталог: 3 товара, 2 склада, штрихкоды, цены, остатки, продажи.

### Запуск

```bash
cd remote_reports
python3 -m venv .venv && . .venv/bin/activate     # если ещё не создан
pip install -e ".[dev]"
PTM_API_KEY=demo-key-123 PORT=18091 \
  python -m uvicorn tools.ptm_api_emulator:build --factory --host 127.0.0.1 --port 18091
```

Проверка: `curl -s http://127.0.0.1:18091/hs/ptm/v1/health`

### Подключение приложения отчётов к эмулятору

Запустить сам сервис отчётов и в **Настройках** указать:

| Поле | Значение |
|------|----------|
| Адрес PTM_API (`ib_location`) | `http://127.0.0.1:18091/hs/ptm/v1` |
| Ключ API (`X-Api-Key`) | `demo-key-123` |

После этого статус ИБ станет «1С» (online), отчёты и переучёт (`/inv`)
работают по реальному HTTP: «Синхронизировать» тянет каталог, а черновик
уходит `POST /inventories`.

### Подключение к РЕАЛЬНОЙ 1С вместо эмулятора

Вместо адреса эмулятора укажите URL публикации PTM_API вашей ИБ
(`http://<host>/<БД>/hs/ptm/v1`) и значение константы `Апи_Ключ` из 1С.
Если 1С и сервис отчётов на разных машинах — публикацию 1С нужно пробросить
до сервиса (SSH-туннель / reverse-proxy), как описано в `remote_reports/README.md`.
