# -*- coding: utf-8 -*-
"""Сортировка касс: сначала наличные, потом безнал."""
import pathlib

paths = [
    pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\DataProcessors\РабочееМестоКассира\Forms\Форма\Ext\Form\Module.bsl"),
    pathlib.Path(r"D:\Git\Public_Trade_Module\Конфигурация\Проверка\DataProcessors\РабочееМестоКассира\Forms\Форма\Ext\Form\Module.bsl"),
]

old = """\tЗапрос.Текст = 
\t\t"ВЫБРАТЬ
\t\t|\tКассы.Ссылка КАК Ссылка,
\t\t|\tКассы.Наименование КАК Наименование
\t\t|ИЗ
\t\t|\tСправочник.Кассы КАК Кассы
\t\t|ГДЕ
\t\t|\tНЕ Кассы.ПометкаУдаления
\t\t|\tИ Кассы.ДоступнаПриРасчете = ИСТИНА
\t\t|УПОРЯДОЧИТЬ ПО
\t\t|\tКассы.Наименование";"""

new = """\tЗапрос.Текст = 
\t\t"ВЫБРАТЬ
\t\t|\tКассы.Ссылка КАК Ссылка,
\t\t|\tКассы.Наименование КАК Наименование
\t\t|ИЗ
\t\t|\tСправочник.Кассы КАК Кассы
\t\t|ГДЕ
\t\t|\tНЕ Кассы.ПометкаУдаления
\t\t|\tИ Кассы.ДоступнаПриРасчете = ИСТИНА
\t\t|УПОРЯДОЧИТЬ ПО
\t\t|\tВЫБОР КОГДА Кассы.ВидКассы = ЗНАЧЕНИЕ(Перечисление.ВидыКасс.Наличная) ТОГДА 0 ИНАЧЕ 1 КОНЕЦ,
\t\t|\tКассы.Наименование";"""

for path in paths:
    folder = "Конфигурация" if "Проверка" not in str(path) else "Проверка"
    content = path.read_text(encoding='utf-8-sig')
    count = content.count(old)
    if count == 1:
        content = content.replace(old, new, 1)
        path.write_text(content, encoding='utf-8-sig')
        print(f"✓ {folder}: OK")
    else:
        print(f"✗ {folder}: {count} вхождений")

print("Готово!")
