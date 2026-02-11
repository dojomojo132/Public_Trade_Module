# Шаблоны XML для конфигурации 1С:Предприятие 8.3.27

## Назначение

Эти шаблоны — **эталонная структура** XML-файлов конфигурации.  
AI-агент ОБЯЗАН использовать их как основу при создании новых объектов метаданных.

## Порядок использования

1. Выбрать шаблон по типу объекта
2. Скопировать целиком (включая заголовок с xmlns!)
3. Заменить все `{{PLACEHOLDER}}` реальными значениями
4. Сгенерировать UUID для каждого `{{UUID_...}}`
5. Проверить через `get_errors`

## Шаблоны

| Файл | Тип объекта | Когда использовать |
|------|-------------|-------------------|
| `template-catalog.xml` | Справочник | Новый справочник |
| `template-document.xml` | Документ | Новый документ (с ТЧ) |
| `template-form.xml` | Форма | Любая новая форма |
| `template-accumulation-register.xml` | Регистр накопления | Остатки/обороты |
| `template-information-register.xml` | Регистр сведений | Настройки, цены |
| `template-enum.xml` | Перечисление | Фиксированный набор значений |
| `template-common-module.xml` | Общий модуль | Серверная/клиентская логика |
| `template-delete-object.py` | Python-скрипт удаления | Удаление объектов с кириллицей в путях |

## Критические правила

- **Заголовок:** Копировать ВСЕ `xmlns` из шаблона. Неполный набор = ошибка загрузки.
- **version:** Всегда `2.20` (НЕ `2.0`!)
- **InternalInfo:** Обязателен для справочников, документов, регистров. Без него конфигуратор не загрузит XML.
- **UUID:** Формат `xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx`, lowercase hex. Каждый UUID уникален.
- **Формы:** Каждый элемент формы ОБЯЗАН иметь `ContextMenu` и `ExtendedTooltip` с уникальными id.
## Шаблон удаления объектов (template-delete-object.py)

**ПРОБЛЕМА:** PowerShell в VS Code полностью ломает кириллицу в путях. Команды `Remove-Item`, `Get-ChildItem` с русскими символами НЕ РАБОТАЮТ.

**РЕШЕНИЕ:** Использовать Python-скрипт для операций с файлами.

### Использование:

```bash
# 1. Скопировать шаблон в корень проекта
cp "Документация/Шаблоны/template-delete-object.py" "_delete_MyObject.py"

# 2. Заменить в скрипте:
#    {{ИмяОбъекта}} → реальное имя объекта (например: ТестРеквизитов)
#    {{ТипОбъекта}} → тип папки (например: DataProcessors, Documents, Catalogs)

# 3. Запустить
python "D:\Git\Public_Trade_Module\_delete_MyObject.py"

# 4. Удалить временный скрипт
rm _delete_MyObject.py
```

### Что НЕ РАБОТАЕТ:

```powershell
# ❌ PowerShell команды с кириллицей
Remove-Item "Конфигурация\Проверка\..." -Force

# ❌ Python inline через PowerShell
python -c "import os; os.remove('путь')"

# ❌ .NET API через PowerShell
[System.IO.File]::Delete("путь с кириллицей")
```

### Что РАБОТАЕТ:

```powershell
# ✅ Python-скрипт через прямой вызов
python "путь\к\скрипту.py"

# ✅ Get-ChildItem БЕЗ кириллицы в -Path
$script = Get-ChildItem -Path "D:\Git\Public_Trade_Module" -Recurse -Filter "script.ps1"
```