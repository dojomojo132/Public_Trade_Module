"""
Конвертирует webapp/scanner-benchmark.html в BSL-функцию СформироватьHTMLБенчмарк().
Результат записывает в _bsl_benchmark_func.txt
"""
import pathlib

html = pathlib.Path('webapp/scanner-benchmark.html').read_text(encoding='utf-8')
lines = html.splitlines()

out = []
out.append('Функция СформироватьHTMLБенчмарк()')

first = lines[0].replace('"', '""')
out.append('\tСтр = "' + first)

for line in lines[1:]:
    escaped = line.replace('"', '""')
    out.append('\t|' + escaped)

out.append('\t";')
out.append('\tВозврат Стр;')
out.append('КонецФункции')

result = '\n'.join(out)
out_path = pathlib.Path('_bsl_benchmark_func.txt')
out_path.write_text(result, encoding='utf-8-sig')

print('Generated lines:', len(out))
print('File size KB:', round(out_path.stat().st_size / 1024, 1))
