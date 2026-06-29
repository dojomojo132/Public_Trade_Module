#!/usr/bin/env python3
"""Build admin.html with document support."""

with open('webapp/admin.html', 'r', encoding='utf-8') as f:
    txt = f.read()
print(f'Read {len(txt)} bytes')

# 1. Replace document placeholders
reps = {
    'doc_receipt': 'receipt',
    'doc_expense': 'expense',
    'doc_transfer': 'transfer',
    'doc_writeoff': 'writeoff',
    'doc_return': 'return',
    'doc_kkk': 'kkk',
}
for did, dcode in reps.items():
    marker = "id:'" + did + "'"
    pos = txt.find(marker)
    if pos >= 0:
        sub = txt[pos:pos+300]
        old = "action:'placeholder'"
        new = "action:'document', document:'" + dcode + "'"
        sub2 = sub.replace(old, new, 1)
        txt = txt[:pos] + sub2 + txt[pos+300:]
        print('  patched', did)
print('Step 1 done')

# 2. Insert DOCUMENT_META before CATALOG_DATA
doc_meta_lines = [
    "    /* ======================================== DOCUMENT META ======================================== */",
    "    var DOCUMENT_META = {",
    "      receipt: { code:'receipt', name:'РџСЂРёС…РѕРґРЅР°СЏ РЅР°РєР»Р°РґРЅР°СЏ',",
    "        header: [",
    "          { id:'number', label:'РќРѕРјРµСЂ', type:'string', required:true, ro:true },",
    "          { id:'date', label:'Р”Р°С‚Р°', type:'date', required:true },",
    "          { id:'counterparty', label:'РљРѕРЅС‚СЂР°РіРµРЅС‚', type:'string', required:true },",
    "          { id:'warehouse', label:'РЎРєР»Р°Рґ', type:'string', required:true },",
    "          { id:'total', label:'РЎСѓРјРјР°', type:'number', ro:true }",
    "        ]",
    "      },",
    "      expense: { code:'expense', name:'Р Р°СЃС…РѕРґРЅР°СЏ РЅР°РєР»Р°РґРЅР°СЏ',",
    "        header: [",
    "          { id:'number', label:'РќРѕРјРµСЂ', type:'string', required:true, ro:true },",
    "          { id:'date', label:'Р”Р°С‚Р°', type:'date', required:true },",
    "          { id:'counterparty', label:'РљРѕРЅС‚СЂР°РіРµРЅС‚', type:'string', required:true },",
    "          { id:'warehouse', label:'РЎРєР»Р°Рґ', type:'string', required:true },",
    "          { id:'total', label:'РЎСѓРјРјР°', type:'number', ro:true }",
    "        ]",
    "      },",
    "      transfer: { code:'transfer', name:'РџРµСЂРµРјРµС‰РµРЅРёРµ',",
    "        header: [",
    "          { id:'number', label:'РќРѕРјРµСЂ', type:'string', required:true, ro:true },",
    "          { id:'date', label:'Р”Р°С‚Р°', type:'date', required:true },",
    "          { id:'warehouseFrom', label:'РЎРєР»Р°Рґ-РѕС‚РїСЂР°РІРёС‚РµР»СЊ', type:'string', required:true },",
    "          { id:'warehouseTo', label:'РЎРєР»Р°Рґ-РїРѕР»СѓС‡Р°С‚РµР»СЊ', type:'string', required:true },",
    "          { id:'total', label:'РЎСѓРјРјР°', type:'number', ro:true }",
    "        ]",
    "      },",
    "      writeoff: { code:'writeoff', name:'РЎРїРёСЃР°РЅРёРµ',",
    "        header: [",
    "          { id:'number', label:'РќРѕРјРµСЂ', type:'string', required:true, ro:true },",
    "          { id:'date', label:'Р”Р°С‚Р°', type:'date', required:true },",
    "          { id:'warehouse', label:'РЎРєР»Р°Рґ', type:'string', required:true },",
    "          { id:'reason', label:'РџСЂРёС‡РёРЅР°', type:'text' },",
    "          { id:'total', label:'РЎСѓРјРјР°', type:'number', ro:true }",
    "        ]",
    "      },",
    "      return_doc: { code:'return_doc', name:'Р’РѕР·РІСЂР°С‚',",
    "        header: [",
    "          { id:'number', label:'РќРѕРјРµСЂ', type:'string', required:true, ro:true },",
    "          { id:'date', label:'Р”Р°С‚Р°', type:'date', required:true },",
    "          { id:'counterparty', label:'РљРѕРЅС‚СЂР°РіРµРЅС‚', type:'string', required:true },",
    "          { id:'warehouse', label:'РЎРєР»Р°Рґ', type:'string', required:true },",
    "          { id:'reason', label:'РџСЂРёС‡РёРЅР°', type:'text' },",
    "          { id:'total', label:'РЎСѓРјРјР°', type:'number', ro:true }",
    "        ]",
    "      },",
    "      kkk: { code:'kkk', name:'Р§РµРє РљРљРњ',",
    "        header: [",
    "          { id:'number', label:'РќРѕРјРµСЂ', type:'string', required:true, ro:true },",
    "          { id:'date', label:'Р”Р°С‚Р°', type:'date', required:true },",
    "          { id:'shift', label:'РЎРјРµРЅР°', type:'string', required:true },",
    "          { id:'cashier', label:'РљР°СЃСЃРёСЂ', type:'string', required:true },",
    "          { id:'total', label:'РЎСѓРјРјР°', type:'number', ro:true }",
    "        ]",
    "      }",
    "    };",
]
doc_meta = '\n'.join(doc_meta_lines)
pos = txt.find('var CATALOG_DATA')
if pos >= 0:
    txt = txt[:pos] + doc_meta + '\n' + txt[pos:]
print('Step 2 done')