# Показать структуру Пользователи.xml для вставки атрибута
import pathlib

base = pathlib.Path(r'D:\Git\Public_Trade_Module')
pz_path = base / 'Конфигурация' / 'Catalogs' / 'Пользователи.xml'
pz = pz_path.read_text(encoding='utf-8', errors='replace')

# Найти последний </Attribute> перед закрывающим тегом объекта
# Показываем последние 3000 символов - там должны быть атрибуты
print('=== ПОСЛЕДНИЕ 3000 символов Пользователи.xml ===')
print(pz[-3000:])
