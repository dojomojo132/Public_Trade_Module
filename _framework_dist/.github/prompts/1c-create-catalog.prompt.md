---
description: "Создание нового справочника 1С:Предприятие с полным набором файлов: XML объекта, Configuration.xml, ConfigDumpInfo.xml, подсистема, форма."
agent: "1c-coder"
tools: [read, search, edit, execute, todo]
argument-hint: "Имя справочника, реквизиты, табличные части, подсистема"
---

Создай новый справочник в конфигурации.

## Входные данные
- Имя справочника: {{ИМЯ}}
- Реквизиты: {{РЕКВИЗИТЫ}}
- Табличные части: {{ТЧ}} (опционально)
- Подсистема: {{ПОДСИСТЕМА}}

## Алгоритм

1. Проверить спецификацию и убедиться что справочника ещё нет (MCP → `list_metadata_objects`)
2. Создать XML из шаблона `{config.paths.templates}/template-catalog.xml`
3. Обновить Configuration.xml → `<Catalog>{{ИМЯ}}</Catalog>` в `<ChildObjects>`
4. Обновить ConfigDumpInfo.xml → `<Metadata name="Catalog.{{ИМЯ}}" ...>`
5. Обновить подсистему → `<xr:Item>Catalog.{{ИМЯ}}</xr:Item>`
6. Создать форму через `python scripts/_generate_form.py --type catalog-element`
7. `get_errors` + `validate-config.ps1` → 0 ошибок
8. Обновить спецификацию (Record в History)

Подробные правила XML → skill `1c-form-generator`, `xml-1c.instructions.md`.
