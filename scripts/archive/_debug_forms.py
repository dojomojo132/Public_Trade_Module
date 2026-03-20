"""Check form XML integrity after field removal"""
import os
import re

forms = [
    r'd:\Git\Public_Trade_Module\Конфигурация\Catalogs\Номенклатура\Forms\ФормаСписка\Ext\Form.xml',
    r'd:\Git\Public_Trade_Module\Конфигурация\Catalogs\Номенклатура\Forms\ФормаЭлемента\Ext\Form.xml',
]

id_pattern = re.compile(r'id="(-?\d+)"')
datapath_pattern = re.compile(r'DataPath[^>]*>([^<]+)</DataPath>', re.IGNORECASE)
datapath_pattern2 = re.compile(r'<DataPath>([^<]+)</DataPath>')

for fpath in forms:
    print(f"\n=== {fpath.split(chr(92))[-4]}/{fpath.split(chr(92))[-1]} ===")
    with open(fpath, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    ids = [int(m.group(1)) for m in id_pattern.finditer(content)]
    print(f"Total IDs: {len(ids)}, max={max(ids) if ids else 0}")
    for check_id in [14, 16, 50]:
        found = check_id in ids
        print(f"  id={check_id}: {'STILL PRESENT !!!' if found else 'removed (ok)'}")
    
    # Check for ставкандс/фоп datapaths
    for pat in [r'[Сс]тавкаНДС', r'[Фф][Оо][Пп]']:
        matches = re.findall(pat, content)
        if matches:
            print(f"  FOUND reference to '{pat}': {matches[:5]}")
    
    # Find all DataPath values
    datapaths = re.findall(r'<DataPath>([^<]+)</DataPath>', content)
    print(f"  DataPaths: {datapaths[:20]}")
