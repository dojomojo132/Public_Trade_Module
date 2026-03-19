# Показать первый атрибут ИдентификаторПользователяИБ как шаблон
import pathlib

base = pathlib.Path(r'D:\Git\Public_Trade_Module')
pz_path = base / 'Конфигурация' / 'Catalogs' / 'Пользователи.xml'
pz = pz_path.read_text(encoding='utf-8', errors='replace')

# Найти атрибут ИдентификаторПользователяИБ
marker = 'ИдентификаторПользователяИБ'
idx = pz.find(marker)
if idx >= 0:
    # Найти начало блока Attribute
    attr_start = pz.rfind('<Attribute', 0, idx)
    # Найти конец блока
    attr_end = pz.find('</Attribute>', idx) + len('</Attribute>')
    print('=== Атрибут ИдентификаторПользователяИБ ===')
    print(repr(pz[attr_start:attr_end]))
    print()
    print('=== Читаемый вид ===')
    print(pz[attr_start:attr_end])
