"""Backup and minimize HTTP service module for testing"""
import shutil, os

base = os.path.join(r'D:\Git\Public_Trade_Module', 'Конфигурация_PTM_Analytics', 'HTTPServices', 'Анл_МобильнаяКасса', 'Ext')
src = os.path.join(base, 'Module.bsl')
bak = os.path.join(base, 'Module.bsl.full_backup')

# Backup
shutil.copy2(src, bak)
print(f"Backup: {bak} ({os.path.getsize(bak)} bytes)")

# Write minimal module
minimal = '''\ufeff#Область ОбработчикиHTTPСервисов\r
\r
Функция ГлавнаяСтраницаGET(Запрос)\r
\tОтвет = Новый HTTPСервисОтвет(200);\r
\tОтвет.Заголовки.Вставить("Content-Type", "text/html; charset=utf-8");\r
\tОтвет.УстановитьТелоИзСтроки("<html><body><h1>Hello Mobile!</h1></body></html>");\r
\tВозврат Ответ;\r
КонецФункции\r
\r
Функция КорзинаGET(Запрос)\r
\tОтвет = Новый HTTPСервисОтвет(200);\r
\tОтвет.Заголовки.Вставить("Content-Type", "application/json; charset=utf-8");\r
\tОтвет.УстановитьТелоИзСтроки("{""items"":[]}");\r
\tВозврат Ответ;\r
КонецФункции\r
\r
Функция КорзинаPOST(Запрос)\r
\tОтвет = Новый HTTPСервисОтвет(200);\r
\tОтвет.Заголовки.Вставить("Content-Type", "application/json; charset=utf-8");\r
\tОтвет.УстановитьТелоИзСтроки("{""result"":""ok""}");\r
\tВозврат Ответ;\r
КонецФункции\r
\r
Функция КорзинаDELETE(Запрос)\r
\tОтвет = Новый HTTPСервисОтвет(200);\r
\tОтвет.Заголовки.Вставить("Content-Type", "application/json; charset=utf-8");\r
\tОтвет.УстановитьТелоИзСтроки("{""result"":""ok""}");\r
\tВозврат Ответ;\r
КонецФункции\r
\r
Функция ОтправкаPOST(Запрос)\r
\tОтвет = Новый HTTPСервисОтвет(200);\r
\tОтвет.Заголовки.Вставить("Content-Type", "application/json; charset=utf-8");\r
\tОтвет.УстановитьТелоИзСтроки("{""result"":""ok""}");\r
\tВозврат Ответ;\r
КонецФункции\r
\r
#КонецОбласти\r
'''

with open(src, 'wb') as f:
    f.write(minimal.encode('utf-8'))
print(f"Minimal module written: {os.path.getsize(src)} bytes")
