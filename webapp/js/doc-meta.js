// DOCUMENT_META вЂ” metadata for all document types
var DOCUMENT_META = {
  receipt: { code:'receipt', name:'Приходная накладная',
    header: [
      { id:'number', label:'Номер', type:'string', required:true, ro:true },
      { id:'date', label:'Дата', type:'date', required:true },
      { id:'counterparty', label:'Контрагент', type:'ref', ref:'counterparties', required:true },
      { id:'warehouse', label:'Склад', type:'ref', ref:'warehouses', required:true },
      { id:'total', label:'Сумма', type:'number', ro:true }
    ]
  },
  expense: { code:'expense', name:'Расходная накладная',
    header: [
      { id:'number', label:'Номер', type:'string', required:true, ro:true },
      { id:'date', label:'Дата', type:'date', required:true },
      { id:'counterparty', label:'Контрагент', type:'ref', ref:'counterparties', required:true },
      { id:'warehouse', label:'Склад', type:'ref', ref:'warehouses', required:true },
      { id:'total', label:'Сумма', type:'number', ro:true }
    ]
  },
  transfer: { code:'transfer', name:'Перемещение',
    header: [
      { id:'number', label:'Номер', type:'string', required:true, ro:true },
      { id:'date', label:'Дата', type:'date', required:true },
      { id:'warehouseFrom', label:'Склад-отправитель', type:'ref', ref:'warehouses', required:true },
      { id:'warehouseTo', label:'Склад-получатель', type:'ref', ref:'warehouses', required:true },
      { id:'total', label:'Сумма', type:'number', ro:true }
    ]
  },
  writeoff: { code:'writeoff', name:'Списание',
    header: [
      { id:'number', label:'Номер', type:'string', required:true, ro:true },
      { id:'date', label:'Дата', type:'date', required:true },
      { id:'warehouse', label:'Склад', type:'ref', ref:'warehouses', required:true },
      { id:'reason', label:'Причина', type:'text' },
      { id:'total', label:'Сумма', type:'number', ro:true }
    ]
  },
  return_doc: { code:'return_doc', name:'Возврат',
    header: [
      { id:'number', label:'Номер', type:'string', required:true, ro:true },
      { id:'date', label:'Дата', type:'date', required:true },
      { id:'counterparty', label:'Контрагент', type:'ref', ref:'counterparties', required:true },
      { id:'warehouse', label:'Склад', type:'ref', ref:'warehouses', required:true },
      { id:'reason', label:'Причина', type:'text' },
      { id:'total', label:'Сумма', type:'number', ro:true }
    ]
  },
  kkk: { code:'kkk', name:'Чек ККМ',
    header: [
      { id:'number', label:'Номер', type:'string', required:true, ro:true },
      { id:'date', label:'Дата', type:'date', required:true },
      { id:'shift', label:'Смена', type:'string', required:true },
      { id:'cashier', label:'Кассир', type:'ref', ref:'users', required:true },
      { id:'total', label:'Сумма', type:'number', ro:true }
    ]
  }
};

// DOCUMENT_DATA вЂ” test documents with table sections
var DOCUMENT_DATA = {
  receipt: [
    { id:'r1', number:'ПН-00001', date:'2026-05-15', counterparty:'ООО "Молокозавод"', warehouse:'Основной склад', total:2250.00, posted:true,
      rows: [
        { goods:'Молоко 3.2% 1л', qty:20, price:45.00, sum:900.00 },
        { goods:'Кефир 2.5% 0.5л', qty:15, price:38.00, sum:570.00 },
        { goods:'Сыр Голландский', qty:3, price:260.00, sum:780.00 }
      ]
    },
    { id:'r2', number:'ПН-00002', date:'2026-05-16', counterparty:'ИП Иванов А.А.', warehouse:'Основной склад', total:660.00, posted:false,
      rows: [
        { goods:'Хлеб белый', qty:30, price:22.00, sum:660.00 }
      ]
    },
    { id:'r3', number:'ПН-00003', date:'2026-05-17', counterparty:'ООО "Молокозавод"', warehouse:'Торговый зал', total:1350.00, posted:true,
      rows: [
        { goods:'Сок яблочный 1л', qty:10, price:55.00, sum:550.00 },
        { goods:'Вода минеральная 1.5л', qty:20, price:28.00, sum:560.00 },
        { goods:'Батон нарезной', qty:10, price:24.00, sum:240.00 }
      ]
    }
  ],
  expense: [
    { id:'e1', number:'РН-00001', date:'2026-05-16', counterparty:'ООО "Супермаркет"', warehouse:'Основной склад', total:1080.00, posted:true,
      rows: [
        { goods:'Сыр Голландский', qty:2, price:320.00, sum:640.00 },
        { goods:'Молоко 3.2% 1л', qty:8, price:55.00, sum:440.00 }
      ]
    }
  ],
  transfer: [
    { id:'t1', number:'ПЕР-00001', date:'2026-05-14', warehouseFrom:'Основной склад', warehouseTo:'Торговый зал', total:900.00, posted:true,
      rows: [
        { goods:'Молоко 3.2% 1л', qty:10, price:45.00, sum:450.00 },
        { goods:'Кефир 2.5% 0.5л', qty:10, price:45.00, sum:450.00 }
      ]
    }
  ],
  writeoff: [
    { id:'w1', number:'СП-00001', date:'2026-05-15', warehouse:'Торговый зал', reason:'Истёк срок годности', total:190.00, posted:true,
      rows: [
        { goods:'Молоко 3.2% 1л', qty:2, price:45.00, sum:90.00 },
        { goods:'Батон нарезной', qty:5, price:20.00, sum:100.00 }
      ]
    }
  ],
  return_doc: [],
  kkk: [
    { id:'k1', number:'ЧЕК-00001', date:'2026-05-19', shift:'Смена 1', cashier:'Петрова А.С.', total:520.00, posted:true,
      rows: [
        { goods:'Хлеб белый', qty:2, price:25.00, sum:50.00 },
        { goods:'Молоко 3.2% 1л', qty:3, price:50.00, sum:150.00 },
        { goods:'Сыр Голландский', qty:1, price:320.00, sum:320.00 }
      ]
    },
    { id:'k2', number:'ЧЕК-00002', date:'2026-05-19', shift:'Смена 1', cashier:'Петрова А.С.', total:165.00, posted:true,
      rows: [
        { goods:'Вода минеральная 1.5л', qty:2, price:30.00, sum:60.00 },
        { goods:'Батон нарезной', qty:3, price:22.00, sum:66.00 },
        { goods:'Кефир 2.5% 0.5л', qty:1, price:39.00, sum:39.00 }
      ]
    }
  ]
};
