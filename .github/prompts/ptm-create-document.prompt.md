---
description: "Создание нового документа 1С:Предприятие PTM с полным набором файлов: XML объекта, модуль проведения, форма, Configuration.xml, ConfigDumpInfo.xml, подсистема."
agent: "1c-coder"
tools: [read, search, edit, execute, todo]
argument-hint: "Имя документа, реквизиты шапки, табличные части с колонками, движения регистров, подсистема"
---

Создай новый документ в конфигурации PTM.

## Входные данные
- Имя документа: {{ИМЯ}}
- Реквизиты шапки: {{РЕКВИЗИТЫ}}
- Табличные части: {{ТЧ}} с колонками
- Движения регистров: {{РЕГИСТРЫ}}
- Подсистема: {{ПОДСИСТЕМА}}

## Алгоритм

1. Проверить спецификацию и убедиться что документа ещё нет (MCP → `list_metadata_objects`)
2. Создать XML из шаблона `Документация/Шаблоны/template-document.xml`
3. Создать ObjectModule.bsl с ОбработкаПроведения
4. Обновить Configuration.xml → `<Document>{{ИМЯ}}</Document>`
5. Обновить ConfigDumpInfo.xml → все записи (объект, реквизиты, ТЧ, колонки)
6. Обновить подсистему → `<xr:Item>Document.{{ИМЯ}}</xr:Item>`
7. Создать форму через `python scripts/_generate_form.py --type document`
8. `get_errors` + `validate-config.ps1` → 0 ошибок
9. Обновить спецификацию (Record в History)

Подробные правила → skills: `1c-form-generator`, `1c-bsl-review`. Instructions: `bsl.instructions.md`, `xml-1c.instructions.md`.
