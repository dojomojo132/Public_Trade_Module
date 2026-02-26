---
description: 'Валидация конфигурации перед загрузкой в 1С: 7 стадий проверки, типичные ошибки'
mode: agent
---

# Валидация конфигурации перед загрузкой

## Когда использовать
- После создания/изменения объектов метаданных
- Перед загрузкой в 1С:Предприятие
- При подозрении на ошибки целостности

## Алгоритм

### Шаг 1: Запуск
```powershell
$script = Get-ChildItem -Path "D:\Git\Public_Trade_Module" -Recurse -Filter "validate-config.ps1" | Select-Object -First 1
powershell -ExecutionPolicy Bypass -File $script.FullName
```

### Шаг 2: Анализ (7 стадий)
1. **Configuration.xml** — парсинг и извлечение объектов
2. **Файлы ↔ Реестр** — каждый объект имеет файл и наоборот
3. **ConfigDumpInfo.xml** — каждый объект имеет запись с UUID
4. **XML структура** — InternalInfo, GeneratedType, UUID
5. **Формы** — уникальность id, ContextMenu/ExtendedTooltip
6. **Файловая структура** — Form.xml и Module.bsl на месте
7. **Перекрёстные ссылки** — RegisterRecords, DefaultObjectForm

### Шаг 3: Исправление
| Ошибка | Решение |
|--------|---------|
| `Файл не найден: Catalogs/Xxx.xml` | Создать из шаблона |
| `Нет записи в ConfigDumpInfo` | Добавить `<Metadata>` запись |
| `Нет в Configuration.xml` | Добавить в `<ChildObjects>` |
| `id дублируется` | Перенумеровать элементы формы |
| `Нет ContextMenu/ExtendedTooltip` | Добавить дочерние элементы |
| `RegisterRecords → несуществ.` | Исправить имя или создать регистр |

### Шаг 4: Повтор
Повторять пока **0 ошибок** → готово к загрузке.
