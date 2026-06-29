#!/usr/bin/env python3
import re

with open('webapp/admin.html', 'r', encoding='utf-8') as f:
    txt = f.read()
print(f"Read {len(txt)} bytes")

reps = {
    "doc_receipt": "receipt",
    "doc_expense": "expense", 
    "doc_transfer": "transfer",
    "doc_writeoff": "writeoff",
    "doc_return": "return",
    "doc_kkk": "kkk",
}
for did, dcode in reps.items():
    marker = f"id:'{did}'"
    pos = txt.find(marker)
    if pos >= 0:
        sub = txt[pos:pos+300]
        old = "action:'placeholder'"
        new = f"action:'document', document:'{dcode}'"
        sub2 = sub.replace(old, new, 1)
        txt = txt[:pos] + sub2 + txt[pos+300:]
        print(f"  {did} -> document:{dcode}")
print("STEP 1 done")

doc_meta = """    /* ======================================== DOCUMENT META ======================================== */
""" + """    var DOCUMENT_META = {""" + """
      receipt: { code:'receipt', name:'""" + "Приходная накладная" + """',
        header: [
          { id:'number', label:'""" + "Номер" + """', type:'string', required:true, ro:true },
          { id:'date', label:'""" + "Дата" + """', type:'date', required:true },
          { id:'counterparty', label:'""" + "Контрагент" + """', type:'string', required:true },
          { id:'warehouse', label:'""" + "Склад" + """', type:'string', required:true },
          { id:'total', label:'""" + "Сумма" + """', type:'number', ro:true }
        ]
      },
      expense: { code:'expense', name:'""" + "Расходная накладная" + """',
        header: [
          { id:'number', label:'""" + "Номер" + """', type:'string', required:true, ro:true },
          { id:'date', label:'""" + "Дата" + """', type:'date', required:true },
          { id:'counterparty', label:'""" + "Контрагент" + """', type:'string', required:true },
          { id:'warehouse', label:'""" + "Склад" + """', type:'string', required:true },
          { id:'total', label:'""" + "Сумма" + """', type:'number', ro:true }
        ]
      },
      transfer: { code:'transfer', name:'""" + "Перемещение" + """',
        header: [
          { id:'number', label:'""" + "Номер" + """', type:'string', required:true, ro:true },
          { id:'date', label:'""" + "Дата" + """', type:'date', required:true },
          { id:'warehouseFrom', label:'""" + "Склад-отправитель" + """', type:'string', required:true },
          { id:'warehouseTo', label:'""" + "Склад-получатель" + """', type:'string', required:true },
          { id:'total', label:'""" + "Сумма" + """', type:'number', ro:true }
        ]
      },
      writeoff: { code:'writeoff', name:'""" + "Списание" + """',
        header: [
          { id:'number', label:'""" + "Номер" + """', type:'string', required:true, ro:true },
          { id:'date', label:'""" + "Дата" + """', type:'date', required:true },
          { id:'warehouse', label:'""" + "Склад" + """', type:'string', required:true },
          { id:'reason', label:'""" + "Причина" + """', type:'text' },
          { id:'total', label:'""" + "Сумма" + """', type:'number', ro:true }
        ]
      },
      return_doc: { code:'return_doc', name:'""" + "Возврат" + """',
        header: [
          { id:'number', label:'""" + "Номер" + """', type:'string', required:true, ro:true },
          { id:'date', label:'""" + "Дата" + """', type:'date', required:true },
          { id:'counterparty', label:'""" + "Контрагент" + """', type:'string', required:true },
          { id:'warehouse', label:'""" + "Склад" + """', type:'string', required:true },
          { id:'reason', label:'""" + "Причина" + """', type:'text' },
          { id:'total', label:'""" + "Сумма" + """', type:'number', ro:true }
        ]
      },
      kkk: { code:'kkk', name:'""" + "Чек ККМ" + """',
        header: [
          { id:'number', label:'""" + "Номер" + """', type:'string', required:true, ro:true },
          { id:'date', label:'""" + "Дата" + """', type:'date', required:true },
          { id:'shift', label:'""" + "Смена" + """', type:'string', required:true },
          { id:'cashier', label:'""" + "Кассир" + """', type:'string', required:true },
          { id:'total', label:'""" + "Сумма" + """', type:'number', ro:true }
        ]
      }
    };
"""
pos = txt.find('var CATALOG_DATA')
if pos >= 0:
    txt = txt[:pos] + doc_meta + '\n' + txt[pos:]
print("STEP 2: DOCUMENT_META inserted")
