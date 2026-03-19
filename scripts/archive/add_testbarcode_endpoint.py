"""
Добавляет endpoint testbarcodeGET в Module.bsl HTTP-сервиса Анл_МобильнаяКасса.
Встраивает scanner-benchmark.html как BSL-строку.
"""
import pathlib

html = pathlib.Path('webapp/scanner-benchmark.html').read_text(encoding='utf-8')
lines = html.splitlines()

parts = []
parts.append('')
parts.append('// ============================================================')
parts.append('// Тест производительности библиотек сканирования штрихкодов')
parts.append('// URL: /ptm/hs/mobile/testbarcode')
parts.append('// ============================================================')
parts.append('')
parts.append('Функция testbarcodeGET(Запрос)')
parts.append('\tОтвет = Новый HTTPСервисОтвет(200);')
parts.append('\tОтвет.Заголовки.Вставить("Content-Type", "text/html; charset=utf-8");')
parts.append('\tОтвет.УстановитьТелоИзСтроки(СформироватьHTMLБенчмарк(), "utf-8", ИспользованиеByteOrderMark.НеИспользовать);')
parts.append('\tВозврат Ответ;')
parts.append('КонецФункции')
parts.append('')
parts.append('Функция СформироватьHTMLБенчмарк()')
parts.append('\tСтр =')

# Escape double quotes for BSL (doubling them)
first_esc = lines[0].replace('"', '""')
parts.append('\t"' + first_esc)
for line in lines[1:]:
    esc = line.replace('"', '""')
    parts.append('\t|' + esc)

parts.append('\t";')
parts.append('\tВозврат Стр;')
parts.append('КонецФункции')

addition = '\n'.join(parts)

bsl_path = pathlib.Path('Конфигурация_PTM_Analytics/HTTPServices/Анл_МобильнаяКасса/Ext/Module.bsl')
bsl = bsl_path.read_text(encoding='utf-8-sig')
bsl_new = bsl.rstrip() + '\n' + addition + '\n'
bsl_path.write_text(bsl_new, encoding='utf-8-sig')

print('Done. New BSL lines:', len(bsl_new.splitlines()))
print('Addition lines:', len(parts))
