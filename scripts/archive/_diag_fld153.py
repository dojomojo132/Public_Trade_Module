# Диагностика: поиск Fld153 в ConfigDumpInfo.xml
import pathlib, re

base = pathlib.Path(r'D:\Git\Public_Trade_Module')
cdi_path = base / 'Конфигурация' / 'ConfigDumpInfo.xml'
cdi = cdi_path.read_text(encoding='utf-8', errors='replace')

idx = cdi.find('Fld153')
if idx >= 0:
    print('=== НАЙДЕНО Fld153 в CDI ===')
    print(cdi[max(0, idx-400):idx+400])
else:
    print('Fld153 НЕ НАЙДЕНО в CDI')
    # Поищем Fld15x
    matches = re.findall(r'Fld1[456]\d', cdi)
    print('Похожие поля Fld15x..Fld16x:', sorted(set(matches)))

# Сколько всего Fld-полей в CDI
all_fields = re.findall(r'Fld\d+', cdi)
nums = sorted(set(int(re.search(r'\d+', f).group()) for f in all_fields))
print(f'\nВсего Fld-полей: {len(nums)}, диапазон: {min(nums)}..{max(nums)}')
print('Поля вокруг 150-160:', [n for n in nums if 148 <= n <= 162])
