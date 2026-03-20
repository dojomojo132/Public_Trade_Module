"""Find context around specific IDs in form XML"""
import re

def find_id_context(fpath, target_id, context=20):
    with open(fpath, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()
    
    results = []
    for i, line in enumerate(lines):
        if f'id="{target_id}"' in line:
            start = max(0, i - 3)
            end = min(len(lines), i + context)
            results.append((i+1, ''.join(lines[start:end])))
    return results

# ФормаСписка - найти id=50
path1 = r'd:\Git\Public_Trade_Module\Конфигурация\Catalogs\Номенклатура\Forms\ФормаСписка\Ext\Form.xml'
print("=== ФормаСписка: contexts for id=50 ===")
for lineno, ctx in find_id_context(path1, 50):
    print(f"Line {lineno}:")
    print(ctx)
    print("---")

# ФормаЭлемента - найти id=14
path2 = r'd:\Git\Public_Trade_Module\Конфигурация\Catalogs\Номенклатура\Forms\ФормаЭлемента\Ext\Form.xml'
print("\n=== ФормаЭлемента: contexts for id=14 ===")
for lineno, ctx in find_id_context(path2, 14):
    print(f"Line {lineno}:")
    print(ctx)
    print("---")
