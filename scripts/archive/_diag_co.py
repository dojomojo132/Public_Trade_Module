# Проверяем точную строку закрытия ChildObjects в Пользователи.xml
import pathlib, re

base = pathlib.Path(r'D:\Git\Public_Trade_Module')
pz_path = base / 'Конфигурация' / 'Catalogs' / 'Пользователи.xml'
pz = pz_path.read_text(encoding='utf-8-sig', errors='replace')

# Найти все вхождения </ChildObjects> и показать контекст
for m in re.finditer(r'</ChildObjects>', pz):
    idx = m.start()
    print(f'--- Позиция {idx} ---')
    print(repr(pz[max(0, idx-30):idx+50]))
    print()
