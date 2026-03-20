"""Compare configVersion across CDI files"""
import re, os

def get_cv(content, name):
    m = re.search(r'Catalog\.' + re.escape(name) + r'[^>]*configVersion="([^"]+)"', content)
    return m.group(1) if m else None

with open(r'd:\Git\Public_Trade_Module\Конфигурация\ConfigDumpInfo.xml', 'r', encoding='utf-8-sig') as f:
    cdi = f.read()

for name in ['НалоговыеГруппы', 'Номенклатура']:
    cv = get_cv(cdi, name)
    print(f'Current CDI {name}: {cv}')

print()
for backup in ['2026-03-20_183603', '2026-03-19_173153']:
    bpath = rf'd:\Git\Public_Trade_Module\_backups\{backup}\Конфигурация\ConfigDumpInfo.xml'
    if os.path.exists(bpath):
        with open(bpath, 'r', encoding='utf-8-sig') as f:
            bcdi = f.read()
        for name in ['НалоговыеГруппы', 'Номенклатура']:
            cv = get_cv(bcdi, name)
            print(f'Backup {backup} CDI {name}: {cv}')
    print()
