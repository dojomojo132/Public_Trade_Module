---
description: "Создание формы для объекта метаданных 1С:Предприятие: дескриптор, Form.xml, Module.bsl с правильными ID, BOM, CRLF."
agent: "1c-form-builder"
tools: [read, search, edit, execute]
argument-hint: "Тип объекта (Document/Catalog/DataProcessor), имя объекта, имя формы"
---

Создай форму для объекта метаданных.

## Входные данные
- Объект-владелец: {{ТИП}}.{{ИМЯ}}
- Имя формы: {{ИМЯ_ФОРМЫ}}
- Тип формы: документ / справочник-элемент / справочник-список / обработка

## Алгоритм

1. Проверить владельца через MCP → `get_form_structure` (убедиться что формы ещё нет)
2. Запустить генератор: `python scripts/_generate_form.py --type <тип> --object <Объект> --form <Имя>`
3. Обновить XML владельца: `<Form>{{ИМЯ_ФОРМЫ}}</Form>` в `<ChildObjects>`
4. Если основная форма → заполнить `<DefaultObjectForm>` / `<DefaultListForm>`
5. Обновить ConfigDumpInfo.xml → `<Metadata name="Тип.Имя.Form.ИмяФормы" id="UUID"/>`
6. `get_errors` на Form.xml и Module.bsl → 0 ошибок

Подробные правила ID, BOM, элементов → skill `1c-form-generator`.
