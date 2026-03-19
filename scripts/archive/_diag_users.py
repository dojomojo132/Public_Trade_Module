# Диагностика: ищем запись Пользователи в CDI и проверяем структуру XML
import pathlib, re

base = pathlib.Path(r'D:\Git\Public_Trade_Module')

# 1. CDI запись для Пользователи
cdi_path = base / 'Конфигурация' / 'ConfigDumpInfo.xml'
cdi = cdi_path.read_text(encoding='utf-8', errors='replace')

# Ищем Пользователи в CDI
idx = cdi.find('Пользователи')
if idx >= 0:
    # Показать весь блок
    start = max(0, idx - 50)
    end = min(len(cdi), idx + 1000)
    print('=== CDI запись Пользователи ===')
    print(cdi[start:end])
else:
    print('Пользователи НЕ найдено в CDI')

print('\n=== Текущее состояние Пользователи.xml (attributes section) ===')
# Читаем Пользователи.xml
pz_path = base / 'Конфигурация' / 'Catalogs' / 'Пользователи.xml'
pz = pz_path.read_text(encoding='utf-8', errors='replace')

# Находим секцию Attributes
attr_start = pz.find('<Attributes>')
attr_end = pz.find('</Attributes>') + len('</Attributes>')
if attr_start >= 0:
    print(pz[attr_start:attr_end])
else:
    print('Секция Attributes не найдена')
    # Поищем по-другому
    for m in re.finditer(r'<Attribute ', pz):
        print(pz[m.start():m.start()+500])
        print('---')
