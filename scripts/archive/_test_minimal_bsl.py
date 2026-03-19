"""
Диагностический скрипт: заменяет Module.bsl сервиса МобильнаяКасса
на минимальную версию без extension-ссылок, для теста.
"""
import os, shutil

src = r'D:\Git\Public_Trade_Module\Конфигурация\HTTPServices\МобильнаяКасса\Ext\Module.bsl'
bak = src + '.orig'

# Backup
with open(src, encoding='utf-8-sig') as r:
    orig = r.read()
with open(bak, 'w', encoding='utf-8-sig') as w:
    w.write(orig)
print(f'Backup: {bak} ({len(orig)} chars)')

# Minimal BSL — NO extension references
minimal = (
    "\ufeff"
    "#Область ОбработчикиHTTPСервисов\n"
    "\n"
    "Функция mainGET(Запрос)\n"
    "\tОтвет = Новый HTTPСервисОтвет(200);\n"
    "\tОтвет.Заголовки.Вставить(\"Content-Type\", \"text/html; charset=utf-8\");\n"
    "\tОтвет.УстановитьТелоИзСтроки(\"<h1>Mobile Kasca TEST OK</h1>\");\n"
    "\tВозврат Ответ;\n"
    "КонецФункции\n"
    "\n"
    "Функция cartGET(Запрос)\n"
    "\tОтвет = Новый HTTPСервисОтвет(200);\n"
    "\tОтвет.УстановитьТелоИзСтроки(\"{\\\"success\\\": true, \\\"items\\\": []}\");\n"
    "\tВозврат Ответ;\n"
    "КонецФункции\n"
    "\n"
    "Функция cartPOST(Запрос)\n"
    "\tОтвет = Новый HTTPСервисОтвет(200);\n"
    "\tОтвет.УстановитьТелоИзСтроки(\"{\\\"success\\\": true}\");\n"
    "\tВозврат Ответ;\n"
    "КонецФункции\n"
    "\n"
    "Функция cartDELETE(Запрос)\n"
    "\tОтвет = Новый HTTPСервисОтвет(200);\n"
    "\tОтвет.УстановитьТелоИзСтроки(\"{\\\"success\\\": true}\");\n"
    "\tВозврат Ответ;\n"
    "КонецФункции\n"
    "\n"
    "Функция sendPOST(Запрос)\n"
    "\tОтвет = Новый HTTPСервисОтвет(200);\n"
    "\tОтвет.УстановитьТелоИзСтроки(\"{\\\"success\\\": true}\");\n"
    "\tВозврат Ответ;\n"
    "КонецФункции\n"
    "\n"
    "#КонецОбласти\n"
)

with open(src, 'w', encoding='utf-8-sig') as w:
    w.write(minimal)
print(f'Minimal BSL written ({len(minimal)} chars) to {src}')
