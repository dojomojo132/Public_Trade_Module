# Показать точный контекст для вставки в CDI  
import pathlib

base = pathlib.Path(r'D:\Git\Public_Trade_Module')
cdi_path = base / 'Конфигурация' / 'ConfigDumpInfo.xml'
cdi = cdi_path.read_text(encoding='utf-8', errors='replace')

# Найти блок Catalog.Пользователи в CDI
marker = 'Catalog.Пользователи'
idx = cdi.find(marker)
if idx >= 0:
    start = max(0, idx - 100)
    end = min(len(cdi), idx + 800)
    print('=== CDI блок Пользователи (точный) ===')
    print(repr(cdi[start:end]))
    print()
    print('=== CDI блок Пользователи (читаемый) ===')
    print(cdi[start:end])
