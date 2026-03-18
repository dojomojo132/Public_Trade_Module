"""Копирует Module.bsl мобильной кассы из расширения в основную конфигурацию"""
import os, shutil

base = r'D:\Git\Public_Trade_Module'

# Найдём исходный файл
src = os.path.join(base, 
    '\u041a\u043e\u043d\u0444\u0438\u0433\u0443\u0440\u0430\u0446\u0438\u044f_PTM_Analytics',
    'HTTPServices',
    '\u0410\u043d\u043b_\u041c\u043e\u0431\u0438\u043b\u044c\u043d\u0430\u044f\u041a\u0430\u0441\u0441\u0430',
    'Ext',
    'Module.bsl'
)

# Целевая папка в основной конфигурации
dst_dir = os.path.join(base, 
    '\u041a\u043e\u043d\u0444\u0438\u0433\u0443\u0440\u0430\u0446\u0438\u044f',
    'HTTPServices',
    '\u041c\u043e\u0431\u0438\u043b\u044c\u043d\u0430\u044f\u041a\u0430\u0441\u0441\u0430',
    'Ext'
)

print(f'Источник: {src}')
print(f'Существует: {os.path.exists(src)}')
print(f'Цель: {dst_dir}')

os.makedirs(dst_dir, exist_ok=True)
dst = os.path.join(dst_dir, 'Module.bsl')
shutil.copy2(src, dst)

# Проверяем BOM (UTF-8 BOM должен быть ef bb bf)
with open(dst, 'rb') as f:
    first = f.read(3)

print(f'Скопировано: {os.path.getsize(dst)} байт, BOM: {first.hex()}')
if first != b'\xef\xbb\xbf':
    print('ВНИМАНИЕ: нет UTF-8 BOM, добавляю...')
    with open(dst, 'rb') as f:
        content = f.read()
    with open(dst, 'wb') as f:
        f.write(b'\xef\xbb\xbf' + content)
    print(f'BOM добавлен, итого: {os.path.getsize(dst)} байт')
else:
    print('BOM OK')
