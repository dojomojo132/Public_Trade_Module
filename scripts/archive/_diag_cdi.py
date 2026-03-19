# Проверяем структуру CDI файлов  
import pathlib, re

base = pathlib.Path(r'D:\Git\Public_Trade_Module')

# ConfigDumpInfo основного
cdi_path = base / 'Конфигурация' / 'ConfigDumpInfo.xml'
cdi = cdi_path.read_text(encoding='utf-8', errors='replace')
print(f'CDI size: {len(cdi)} chars')
print('Первые 2000 символов:')
print(cdi[:2000])
print('...')
print('Строки с "Field":', sum(1 for l in cdi.splitlines() if 'Field' in l or 'field' in l))
print('Строки с "Fld":', sum(1 for l in cdi.splitlines() if 'Fld' in l))
print('Строки с "Пароль":', sum(1 for l in cdi.splitlines() if 'Пароль' in l or 'Password' in l))
