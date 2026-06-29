// doc-ui.js — document journal + form rendering
// Depends on: DOCUMENT_META, DOCUMENT_DATA, CATALOG_DATA, docState,
//             esc(), escAttr(), notify(), topOfStack(), findItem(), navStack, render()

/* ── Helper: flatten catalog to [{id,name}] for select ── */
function catalogSelectOptions(refId) {
  var arr = CATALOG_DATA[refId] || [];
  var opts = [];
  arr.forEach(function(item) {
    if (!item.isGroup) opts.push({ id: item.id, name: item.name });
  });
  return opts;
}

function renderSelect(id, val, opts, disabled) {
  var h = '<select class="field-input" id="' + id + '" style="width:100%" ' + (disabled ? 'disabled' : '') + '>';
  h += '<option value="">-- выберите --</option>';
  opts.forEach(function(o) {
    var sel = (val === o.name || val === o.id) ? ' selected' : '';
    h += '<option value="' + escAttr(o.name) + '"' + sel + '>' + esc(o.name) + '</option>';
  });
  h += '</select>';
  return h;
}

function renderInput(id, val, type, ro) {
  if (type === 'text') {
    return '<textarea class="field-input" id="' + id + '" ' + (ro ? 'readonly' : '') + '>' + esc(val) + '</textarea>';
  }
  var t = (type === 'date') ? 'date' : (type === 'number' ? 'number' : 'text');
  return '<input class="field-input" id="' + id + '" value="' + escAttr(val) + '" type="' + t + '" ' + (ro ? 'readonly' : '') + '>';
}

/* ── OPEN / NAV ── */
function openDocument(docType) {
  var meta = DOCUMENT_META[docType]; if (!meta) return;
  docState.docType = docType; docState.editingId = null; docState.isNew = false; docState.editData = null;
  navStack.push({ id: 'doc_' + docType, title: meta.name, type: 'doc_view', docType: docType });
  render(); window.scrollTo({ top: 0, behavior: 'smooth' });
}

function renderDoc() {
  var top = topOfStack(); if (!top) return;
  if (top.type === 'doc_form') { renderDocForm(); return; }
  if (top.type === 'doc_view') { renderDocJournal(); return; }
}

/* ── JOURNAL ── */
function renderDocJournal() {
  var top = topOfStack(); if (!top || top.type !== 'doc_view') return;
  var docType = top.docType;
  var meta = DOCUMENT_META[docType]; if (!meta) return;
  var docs = DOCUMENT_DATA[docType] || [];
  var main = document.getElementById('mainContent');

  var html = '';
  html += '<button class="back-btn" id="docListBack">← Назад</button>';
  html += '<div class="section-title"><span class="st-icon">&#128196;</span>' + esc(meta.name) + '</div>';
  html += '<div class="cat-toolbar">';
  html += '<button class="btn btn-primary" id="docAdd">+ Создать</button>';
  html += '</div>';
  html += '<div class="cat-table">';
  if (docs.length === 0) {
    html += '<div class="cat-empty">Нет документов</div>';
  } else {
    docs.forEach(function(doc) {
      var postedIcon = doc.posted ? '&#9989;' : '&#128221;';
      html += '<div class="cat-row" data-id="' + doc.id + '">' +
        '<div class="cat-icon">' + postedIcon + '</div>' +
        '<div class="cat-code">' + esc(doc.number) + '</div>' +
        '<div class="cat-name">' + esc(doc.date) + '</div>' +
        '<div class="cat-extra">' + (doc.total || 0).toFixed(2) + '</div>' +
        '</div>';
    });
  }
  html += '</div>';
  main.innerHTML = html;

  document.getElementById('docListBack').addEventListener('click', function() {
    docState.docType = null; navStack.pop();
    render(); window.scrollTo({ top: 0, behavior: 'smooth' });
  });
  document.getElementById('docAdd').addEventListener('click', function() { startNewDoc(docType); });
  main.querySelectorAll('.cat-row').forEach(function(row) {
    row.addEventListener('click', function(e) {
      openDocForm(docType, row.getAttribute('data-id'));
      e.stopPropagation();
    });
  });
}

function findDoc(docType, id) {
  var arr = DOCUMENT_DATA[docType] || [];
  for (var i = 0; i < arr.length; i++) { if (arr[i].id === id) return arr[i]; }
  return null;
}

function openDocForm(docType, docId) {
  var doc = findDoc(docType, docId); if (!doc) return;
  docState.editingId = docId; docState.isNew = false;
  docState.editData = JSON.parse(JSON.stringify(doc));
  navStack.push({ id: 'doc_form_' + docId, title: doc.number, type: 'doc_form', docType: docType });
  render(); window.scrollTo({ top: 0, behavior: 'smooth' });
}

function startNewDoc(docType) {
  var meta = DOCUMENT_META[docType];
  var data = { id: 'new', number: '', date: new Date().toISOString().slice(0,10), posted: false, rows: [] };
  meta.header.forEach(function(f) { if (data[f.id] === undefined) data[f.id] = ''; });
  data.total = 0;
  docState.editingId = null; docState.isNew = true;
  docState.editData = data;
  navStack.push({ id: 'doc_new', title: 'Новый документ', type: 'doc_form', docType: docType });
  render(); window.scrollTo({ top: 0, behavior: 'smooth' });
}

/* ── FORM (header + table) ── */
function renderDocForm() {
  var top = topOfStack(); if (!top || top.type !== 'doc_form') return;
  var docType = top.docType;
  var meta = DOCUMENT_META[docType]; if (!meta) return;
  var data = docState.editData; if (!data) return;
  var isNew = docState.isNew;
  var main = document.getElementById('mainContent');

  var html = '';
  html += '<button class="back-btn" id="docFormBack">← К журналу</button>';
  html += '<div class="card">';
  html += '<div class="card-header"><h3>' + (isNew ? '&#128196; Новый документ' : '&#128196; ' + esc(data.number || '')) + '</h3>';
  html += '<span style="font-size:12px;">' + (data.posted ? '&#9989; Проведён' : '&#128221; Не проведён') + '</span>';
  html += '</div>';
  html += '<div class="card-body">';

  // Header fields — support ref type
  meta.header.forEach(function(f) {
    var val = data[f.id] !== undefined ? data[f.id] : '';
    var ro = f.ro || (!isNew && f.id === 'number');
    var fieldHtml;
    if (f.type === 'ref') {
      var opts = catalogSelectOptions(f.ref);
      fieldHtml = renderSelect('dfld_' + f.id, val, opts, ro);
    } else {
      fieldHtml = renderInput('dfld_' + f.id, val, f.type, ro);
    }
    html += '<div class="field-group"><div class="field-label">' + esc(f.label) + (f.required ? ' *' : '') + '</div>' + fieldHtml + '</div>';
  });

  // Table section — goods is ref to 'goods' catalog
  var goodsOpts = catalogSelectOptions('goods');
  html += '<div class="section-title" style="margin-top:20px">&#128203; Табличная часть</div>';
  html += '<div class="cat-table" style="margin-bottom:8px">';
  html += '<div class="cat-row" style="background:#f8f9fa;font-weight:600;font-size:12px;cursor:default">' +
    '<div style="flex:2">Номенклатура</div>' +
    '<div class="cat-code">Кол-во</div>' +
    '<div class="cat-code">Цена</div>' +
    '<div class="cat-code">Сумма</div>' +
    '<div style="width:30px"></div>' +
    '</div>';
  var rows = data.rows || [];
  if (rows.length === 0) {
    html += '<div class="cat-empty" style="padding:16px">Нет позиций</div>';
  } else {
    rows.forEach(function(row, ri) {
      var sel = renderSelect('docRowGoods_' + ri, row.goods || '', goodsOpts, false);
      html += '<div class="cat-row">' +
        '<div style="flex:2">' + sel + '</div>' +
        '<div class="cat-code"><input class="field-input" id="docRowQty_' + ri + '" value="' + (row.qty || 0) + '" type="number" style="padding:4px 6px;font-size:13px" data-row="' + ri + '"></div>' +
        '<div class="cat-code"><input class="field-input" id="docRowPrice_' + ri + '" value="' + (row.price || 0).toFixed(2) + '" type="number" step="0.01" style="padding:4px 6px;font-size:13px" data-row="' + ri + '"></div>' +
        '<div class="cat-code" id="docRowSum_' + ri + '">' + ((row.qty||0)*(row.price||0)).toFixed(2) + '</div>' +
        '<button class="btn btn-danger btn-sm" style="padding:2px 6px" id="docRowDel_' + ri + '">&#10005;</button>' +
        '</div>';
    });
  }
  html += '</div>';
  html += '<button class="btn btn-outline btn-sm" id="docAddRow" style="margin-bottom:16px">+ Строка</button>';

  html += '</div>';
  html += '<div class="card-footer">';
  html += '<button class="btn btn-primary" id="docSaveBtn">&#128190; Сохранить</button>';
  if (!isNew) {
    html += '<button class="btn ' + (data.posted ? 'btn-outline' : 'btn-success') + '" id="docPostBtn">' +
      (data.posted ? '&#8617; Отменить проведение' : '&#9989; Провести') + '</button>';
  }
  html += '<button class="btn btn-outline" id="docCancelBtn">Отмена</button>';
  html += '</div>';
  html += '</div>';
  main.innerHTML = html;

  // Live recalc on qty/price change
  rows.forEach(function(row, ri) {
    var qEl = document.getElementById('docRowQty_' + ri);
    var pEl = document.getElementById('docRowPrice_' + ri);
    if (qEl && pEl) {
      var handler = function() {
        var q = parseFloat(qEl.value) || 0;
        var p = parseFloat(pEl.value) || 0;
        var sumEl = document.getElementById('docRowSum_' + ri);
        if (sumEl) sumEl.textContent = (q * p).toFixed(2);
      };
      qEl.addEventListener('input', handler);
      pEl.addEventListener('input', handler);
    }
  });

  document.getElementById('docFormBack').addEventListener('click', function() {
    docState.editingId = null; docState.isNew = false; docState.editData = null;
    navStack.pop(); render(); window.scrollTo({ top: 0, behavior: 'smooth' });
  });
  document.getElementById('docSaveBtn').addEventListener('click', function() { saveDocument(docType, meta); });
  document.getElementById('docCancelBtn').addEventListener('click', function() {
    docState.editingId = null; docState.isNew = false; docState.editData = null;
    navStack.pop(); render(); window.scrollTo({ top: 0, behavior: 'smooth' });
  });
  var postBtn = document.getElementById('docPostBtn');
  if (postBtn) {
    postBtn.addEventListener('click', function() { togglePost(docType); });
  }
  var addRowBtn = document.getElementById('docAddRow');
  if (addRowBtn) {
    addRowBtn.addEventListener('click', function() {
      data.rows = data.rows || [];
      data.rows.push({ goods:'', qty:1, price:0, sum:0 });
      renderDocForm();
    });
  }
  rows.forEach(function(row, ri) {
    var btn = document.getElementById('docRowDel_' + ri);
    if (btn) {
      btn.addEventListener('click', function(e) {
        data.rows.splice(ri, 1);
        renderDocForm();
        e.stopPropagation();
      });
    }
  });
}

/* ── SAVE: read select values ── */
function saveDocument(docType, meta) {
  var data = docState.editData; if (!data) return;
  meta.header.forEach(function(f) {
    if (f.ro && f.id === 'total') return;
    var el = document.getElementById('dfld_' + f.id);
    if (el) {
      data[f.id] = el.value;
      if (f.type === 'number' && data[f.id] !== '') data[f.id] = parseFloat(data[f.id]);
    }
  });
  // Read table rows
  var rows = data.rows || [];
  for (var ri = 0; ri < rows.length; ri++) {
    var gEl = document.getElementById('docRowGoods_' + ri);
    var qEl = document.getElementById('docRowQty_' + ri);
    var pEl = document.getElementById('docRowPrice_' + ri);
    if (gEl) rows[ri].goods = gEl.value;
    if (qEl) rows[ri].qty = parseFloat(qEl.value) || 0;
    if (pEl) rows[ri].price = parseFloat(pEl.value) || 0;
    rows[ri].sum = rows[ri].qty * rows[ri].price;
  }
  var total = 0;
  rows.forEach(function(row) { total += row.sum; });
  data.total = Math.round(total * 100) / 100;

  for (var i = 0; i < meta.header.length; i++) {
    var f = meta.header[i];
    if (f.required && !data[f.id]) {
      notify('Поле "' + f.label + '" обязательно');
      return;
    }
  }

  if (docState.isNew) {
    var arr = DOCUMENT_DATA[docType] || [];
    var maxNum = 0;
    arr.forEach(function(d) { var n = parseInt(d.number.replace(/\D/g,'')) || 0; if (n > maxNum) maxNum = n; });
    var prefixes = { receipt:'ПН-', expense:'РН-', transfer:'ПЕР-', writeoff:'СП-', return_doc:'ВОЗ-', kkk:'ЧЕК-' };
    data.number = (prefixes[docType] || 'ДОК-') + String(maxNum + 1).padStart(5, '0');
    data.id = docType.charAt(0) + (arr.length + 1);
    data.posted = false;
    DOCUMENT_DATA[docType] = arr;
    arr.push(JSON.parse(JSON.stringify(data)));
    notify('Документ "' + data.number + '" создан');
  } else {
    var doc = findDoc(docType, data.id || docState.editingId);
    if (doc) { Object.keys(data).forEach(function(k) { doc[k] = data[k]; }); }
    notify('Документ сохранён');
  }

  docState.editingId = null; docState.isNew = false; docState.editData = null;
  navStack.pop(); render(); window.scrollTo({ top: 0, behavior: 'smooth' });
}

function togglePost(docType) {
  var data = docState.editData; if (!data) return;
  data.posted = !data.posted;
  var doc = findDoc(docType, data.id || docState.editingId);
  if (doc) doc.posted = data.posted;
  notify(data.posted ? 'Документ проведён' : 'Проведение отменено');
  renderDocForm();
}
