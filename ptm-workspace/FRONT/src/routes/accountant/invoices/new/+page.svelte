<script lang="ts">
  import { onMount, tick } from 'svelte';
  import { browser } from '$app/environment';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import Header from '$lib/components/Header.svelte';
  import { authStore } from '$lib/stores/auth.svelte';
  import { apiFetch } from '$lib/api/client';
  import { formatMoney } from '$lib/utils';

  interface Warehouse { id: string; name: string }
  interface Counterparty { id: string; name: string; is_supplier: boolean }
  interface Product { id: string; code: string; name: string; unit: string }

  interface Line {
    uid: number;
    product: Product | null;
    productSearch: string;
    searchResults: Product[];
    searchHighlight: number;
    searching: boolean;
    qty: number;
    price: number;      // цена с НДС (20%)
  }

  const VAT = 20;

  let uidSeq = 1;

  function newLine(): Line {
    return { uid: uidSeq++, product: null, productSearch: '', searchResults: [], searchHighlight: -1, searching: false, qty: 1, price: 0 };
  }

  function lineSum(l: Line) { return l.qty * l.price; }
  function linePriceExcl(l: Line) { return l.price / (1 + VAT / 100); }
  function lineSumExcl(l: Line) { return l.qty * linePriceExcl(l); }

  function onSumInput(line: Line, value: string) {
    const sum = parseFloat(value);
    if (!isNaN(sum) && line.qty !== 0) line.price = sum / line.qty;
  }

  function onPriceExclInput(line: Line, value: string) {
    const pe = parseFloat(value);
    if (!isNaN(pe)) line.price = pe * (1 + VAT / 100);
  }

  function onSumExclInput(line: Line, value: string) {
    const se = parseFloat(value);
    if (!isNaN(se) && line.qty !== 0) line.price = (se / line.qty) * (1 + VAT / 100);
  }

  let warehouses = $state<Warehouse[]>([]);
  let counterparties = $state<Counterparty[]>([]);
  let warehouseId = $state('');
  let counterpartyId = $state('');
  let lines = $state<Line[]>([]);
  let saving = $state(false);
  let posting = $state(false);
  let errorMsg = $state('');
  let editId = $state<string | null>(null);
  let navCell = $state({ row: 0, col: 1 });
  let editCell = $state<{ row: number; col: number } | null>(null);

  function isEditing(row: number, col: number): boolean {
    return editCell?.row === row && editCell?.col === col;
  }

  const total = $derived(lines.reduce((s, l) => s + l.qty * l.price, 0));

  onMount(() => {
    if (!browser) return;
    init();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Insert') { e.preventDefault(); addLine(); }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  });

  async function init() {
    await new Promise(r => setTimeout(r, 200));
    if (!authStore.isAuthenticated || (authStore.role !== 'accountant' && authStore.role !== 'admin')) {
      await goto('/login');
      return;
    }
    const [wRes, cRes] = await Promise.all([
      apiFetch<{ warehouses: Warehouse[] }>('/api/warehouses'),
      apiFetch<{ counterparties: Counterparty[] }>('/api/counterparties'),
    ]);
    warehouses = wRes.warehouses ?? [];
    counterparties = (cRes.counterparties ?? []).filter(c => c.is_supplier);
    if (warehouses.length > 0) warehouseId = warehouses[0].id;
    if (counterparties.length > 0) counterpartyId = counterparties[0].id;

    // Режим редактирования: ?edit=ID
    const editParam = $page.url.searchParams.get('edit');
    if (editParam) {
      editId = editParam;
      try {
        const res = await apiFetch<{ document: {
          warehouse_id: string | null;
          counterparty_id: string | null;
          lines: Array<{ product_id: string; product_code: string; product_name: string; unit: string; quantity: string; price: string }>;
        } }>(`/api/documents/${editParam}`);
        const doc = res.document;
        if (doc.warehouse_id) warehouseId = doc.warehouse_id;
        if (doc.counterparty_id) counterpartyId = doc.counterparty_id;
        lines = doc.lines.map(l => ({
          uid: uidSeq++,
          product: { id: l.product_id, code: l.product_code, name: l.product_name, unit: l.unit },
          productSearch: l.product_name,
          searchResults: [],
          searchHighlight: -1,
          searching: false,
          qty: parseFloat(l.quantity),
          price: parseFloat(l.price),
        }));
      } catch {
        lines = [newLine()];
      }
    } else {
      lines = [newLine()];
    }
  }

  // -- Поиск товара -------------------------------
  let searchTimers: Record<number, ReturnType<typeof setTimeout>> = {};

  function onSearchInput(line: Line) {
    const uid = line.uid;
    clearTimeout(searchTimers[uid]);
    line.searchHighlight = -1;
    if (line.productSearch.length < 2) {
      line.searchResults = [];
      return;
    }
    searchTimers[uid] = setTimeout(async () => {
      line.searching = true;
      try {
        const res = await apiFetch<{ products: Product[] }>(
          `/api/products/search?q=${encodeURIComponent(line.productSearch)}`
        );
        line.searchResults = res.products ?? [];
      } catch {
        line.searchResults = [];
      } finally {
        line.searching = false;
      }
    }, 300);
  }

  function selectProduct(line: Line, product: Product) {
    line.product = product;
    line.productSearch = `[${product.code}] ${product.name}`;
    line.searchResults = [];
    line.searchHighlight = -1;
  }

  function clearProduct(line: Line, keepSearch = false) {
    const prev = line.product?.name ?? '';
    line.product = null;
    line.productSearch = keepSearch ? prev : '';
    line.searchResults = [];
    line.searchHighlight = -1;
    // если оставляем текст — запустить поиск сразу
    if (keepSearch && prev.length >= 2) {
      tick().then(() => onSearchInput(line));
    }
  }

  function focusEnd(node: HTMLInputElement) {
    node.focus();
    const len = node.value.length;
    node.setSelectionRange(len, len);
  }

  async function addLine() {
    lines = [...lines, newLine()];
    const newRowIdx = lines.length - 1;
    navCell = { row: newRowIdx, col: 0 };
    await tick();
    const inputs = Array.from(document.querySelectorAll<HTMLInputElement>('input[placeholder="Код или название…"]'));
    inputs[inputs.length - 1]?.focus();
  }

  function removeLine(uid: number) {
    lines = lines.filter(l => l.uid !== uid);
    if (lines.length === 0) lines = [newLine()];
  }

  // -- Навигация клавишами -------------------------
  async function startEditing(row: number, col: number) {
    if (row < 0 || row >= lines.length) return;
    navCell = { row, col };
    editCell = { row, col };
    await tick();
    const el = document.querySelector<HTMLInputElement>(`[data-row="${row}"][data-col="${col}"]`);
    if (el) { el.focus(); el.select(); }
  }

  function stopEditing(row: number, col: number) {
    if (editCell?.row !== row || editCell?.col !== col) return;
    editCell = null;
    tick().then(() => {
      if (!editCell) {
        const el = document.querySelector<HTMLElement>(`[data-nav="${row}-${col}"]`);
        el?.focus();
      }
    });
  }

  function navMove(rowDelta: number, colDelta: number, curRow: number, curCol: number) {
    const allCols = [0, 1, 2, 3, 4, 5];
    const newRow = Math.max(0, Math.min(lines.length - 1, curRow + rowDelta));
    let newCol = curCol;
    if (colDelta !== 0) {
      const idx = allCols.indexOf(curCol);
      if (idx >= 0) {
        const ni = Math.max(0, Math.min(allCols.length - 1, idx + colDelta));
        newCol = allCols[ni];
      }
    }
    navCell = { row: newRow, col: newCol };
    tick().then(() => {
      const el = document.querySelector<HTMLElement>(`[data-nav="${newRow}-${newCol}"]`);
      el?.focus();
    });
  }

  function onNavKeyDown(e: KeyboardEvent, row: number, col: number) {
    if (e.key === 'ArrowDown') { e.preventDefault(); navMove(1, 0, row, col); }
    else if (e.key === 'ArrowUp') { e.preventDefault(); navMove(-1, 0, row, col); }
    else if (e.key === 'ArrowRight') { e.preventDefault(); navMove(0, 1, row, col); }
    else if (e.key === 'ArrowLeft') { e.preventDefault(); navMove(0, -1, row, col); }
    else if (e.key === 'Enter' || e.key === 'F2') { e.preventDefault(); startEditing(row, col); }
    else if (/^[\d.]$/.test(e.key)) { startEditing(row, col); } // начало цифрового ввода
  }

  // Доступность для обратной совместимости
  async function moveFocus(rowIdx: number, colIdx: number) {
    await startEditing(rowIdx, colIdx);
  }

  function onProductKeyDown(e: KeyboardEvent, line: Line, rowIdx: number) {
    const results = line.searchResults;
    if (results.length > 0) {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        line.searchHighlight = Math.min(line.searchHighlight + 1, results.length - 1);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        line.searchHighlight = Math.max(line.searchHighlight - 1, 0);
      } else if (e.key === 'Enter') {
        if (line.searchHighlight >= 0) {
          e.preventDefault();
          selectProduct(line, results[line.searchHighlight]);
          startEditing(rowIdx, 1);
        }
      } else if (e.key === 'Escape') {
        e.preventDefault();
        line.searchResults = [];
        line.searchHighlight = -1;
      }
    } else {
      if (e.key === 'ArrowDown') { e.preventDefault(); navMove(1, 0, rowIdx, 0); }
      else if (e.key === 'ArrowUp') { e.preventDefault(); navMove(-1, 0, rowIdx, 0); }
      else if (e.key === 'ArrowRight') { e.preventDefault(); navMove(0, 1, rowIdx, 0); }
      else if (e.key === 'Escape') {
        if (!line.product && !line.productSearch && lines.length > 1) {
          e.preventDefault();
          const prevRow = rowIdx > 0 ? rowIdx - 1 : 0;
          removeLine(line.uid);
          tick().then(() => navMove(0, 0, prevRow, 1));
        }
      }
    }
  }

  function onCellKeyDown(e: KeyboardEvent, rowIdx: number, colIdx: number) {
    if (e.key === 'Escape') {
      e.preventDefault();
      (e.target as HTMLInputElement).blur();
      return;
    }
    if (e.key === 'Enter') {
      e.preventDefault();
      (e.target as HTMLInputElement).blur();
      // Переход на следующую ячейку только в последней строке
      if (rowIdx === lines.length - 1 && colIdx < 3) {
        tick().then(() => startEditing(rowIdx, colIdx + 1));
      }
      return;
    }
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      (e.target as HTMLInputElement).blur();
      tick().then(() => navMove(1, 0, rowIdx, colIdx));
      return;
    }
    if (e.key === 'ArrowUp') {
      e.preventDefault();
      (e.target as HTMLInputElement).blur();
      tick().then(() => navMove(-1, 0, rowIdx, colIdx));
      return;
    }
    else if (e.key === 'ArrowRight') {
      const inp = e.target as HTMLInputElement;
      if (inp.selectionStart === inp.value.length) {
        e.preventDefault(); inp.blur();
        tick().then(() => startEditing(rowIdx, colIdx + 1));
      }
    } else if (e.key === 'ArrowLeft') {
      const inp = e.target as HTMLInputElement;
      if (inp.selectionStart === 0 && colIdx >= 1) {
        e.preventDefault(); inp.blur();
        if (colIdx === 1) { tick().then(() => navMove(0, 0, rowIdx, 0)); }
        else { tick().then(() => startEditing(rowIdx, colIdx - 1)); }
      }
    }
  }

  // -- Сохранение ---------------------------------
  function buildPayload() {
    const validLines = lines.filter(l => l.product !== null && l.qty > 0);
    if (validLines.length === 0) throw new Error('Добавьте хотя бы одну строку с товаром');
    if (!warehouseId) throw new Error('Выберите склад');
    return {
      doc_type: 'invoice_in',
      warehouse_id: warehouseId,
      counterparty_id: counterpartyId || undefined,
      lines: validLines.map(l => ({
        product_id: l.product!.id,
        quantity: l.qty,
        price: l.price,
        cost_price: l.price,
      })),
      payments: [],
    };
  }

  async function saveDraft() {
    errorMsg = '';
    try {
      const payload = buildPayload();
      saving = true;
      if (editId) {
        await apiFetch(`/api/documents/${editId}`, { method: 'PUT', body: JSON.stringify(payload) });
        await goto(`/accountant/invoices/${editId}`);
      } else {
        const res = await apiFetch<{ success: boolean; document_id: string }>('/api/documents', {
          method: 'POST',
          body: JSON.stringify(payload),
        });
        await goto(`/accountant/invoices/${res.document_id}`);
      }
    } catch (e) {
      errorMsg = e instanceof Error ? e.message : 'Ошибка сохранения';
    } finally {
      saving = false;
    }
  }

  async function saveAndPost() {
    errorMsg = '';
    try {
      const payload = buildPayload();
      posting = true;
      let docId: string;
      if (editId) {
        await apiFetch(`/api/documents/${editId}`, { method: 'PUT', body: JSON.stringify(payload) });
        docId = editId;
      } else {
        const res = await apiFetch<{ success: boolean; document_id: string }>('/api/documents', {
          method: 'POST',
          body: JSON.stringify(payload),
        });
        docId = res.document_id;
      }
      await apiFetch(`/api/documents/${docId}/post`, { method: 'POST' });
      await goto(`/accountant/invoices/${docId}`);
    } catch (e) {
      errorMsg = e instanceof Error ? e.message : 'Ошибка проведения';
    } finally {
      posting = false;
    }
  }
</script>

<svelte:head><title>{editId ? 'PTM — Редактирование накладной' : 'PTM — Новая накладная'}</title></svelte:head>

<Header />

<main class="flex flex-1 flex-col overflow-hidden">
  <!-- Скроллируемая область: заголовок + шапка + таблица -->
  <div class="flex-1 overflow-y-auto p-4">

    <!-- Заголовок -->
    <div class="mb-4 flex items-center gap-3">
      <a href="/accountant/invoices" class="text-slate-400 hover:text-slate-200 transition">← Назад</a>
      <h1 class="text-lg font-semibold">{editId ? 'Редактирование накладной' : 'Новая приходная накладная'}</h1>
    </div>

    <!-- Шапка документа -->
    <div class="mb-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
      <div>
        <label for="warehouse" class="mb-1 block text-xs text-slate-400">Склад *</label>
        <select
          id="warehouse"
          bind:value={warehouseId}
          class="w-full rounded-lg bg-slate-800 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
        >
          {#each warehouses as wh (wh.id)}
            <option value={wh.id}>{wh.name}</option>
          {/each}
        </select>
      </div>
      <div>
        <label for="counterparty" class="mb-1 block text-xs text-slate-400">Поставщик</label>
        <select
          id="counterparty"
          bind:value={counterpartyId}
          class="w-full rounded-lg bg-slate-800 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
        >
          <option value="">— не выбран —</option>
          {#each counterparties as cp (cp.id)}
            <option value={cp.id}>{cp.name}</option>
          {/each}
        </select>
      </div>
    </div>

    <!-- Табличная часть -->
    <div class="mb-3 rounded-xl border border-slate-700">
      <table class="w-full text-sm">
        <thead>
          <tr class="border-b border-slate-700 bg-slate-800 text-left">
            <th class="w-8 px-3 py-2 text-slate-400">№</th>
            <th class="px-3 py-2 text-slate-400">Товар</th>
            <th class="w-28 px-3 py-2 text-right text-slate-400">Кол-во</th>
            <th class="w-28 px-3 py-2 text-right text-slate-400">Цена</th>
            <th class="w-28 px-3 py-2 text-right text-slate-400">Сумма</th>
            <th class="w-28 px-3 py-2 text-right text-slate-500 text-xs">Цена б/НДС</th>
            <th class="w-28 px-3 py-2 text-right text-slate-500 text-xs">Сумма б/НДС</th>
            <th class="w-8 px-2 py-2"></th>
          </tr>
        </thead>
        <tbody>
          {#each lines as line, lineIdx (line.uid)}
            <tr class="border-b border-slate-800">
              <td class="px-3 py-2 text-slate-500 text-xs">{lines.indexOf(line) + 1}</td>
              <!-- Товар (поиск / выбранный) -->
              <td class="px-3 py-2">
                <div class="relative"
                  onfocusout={(e) => {
                    const related = e.relatedTarget as Node | null;
                    if (!related || !(e.currentTarget as HTMLElement).contains(related)) {
                      line.searchResults = [];
                      line.searching = false;
                    }
                  }}
                >
                  {#if line.product}
                    <button
                      type="button"
                      onclick={() => clearProduct(line, true)}
                      data-nav={`${lineIdx}-0`}
                      onfocus={() => { navCell = { row: lineIdx, col: 0 }; }}
                      onkeydown={(e) => {
                        if (e.key === 'ArrowRight') { e.preventDefault(); navMove(0, 1, lineIdx, 0); }
                        else if (e.key === 'ArrowDown') { e.preventDefault(); navMove(1, 0, lineIdx, 0); }
                        else if (e.key === 'ArrowUp') { e.preventDefault(); navMove(-1, 0, lineIdx, 0); }
                      }}
                      class="w-full rounded text-left text-slate-300 hover:text-white transition px-2 py-1.5 focus:outline-none {navCell.row === lineIdx && navCell.col === 0 ? 'ring-1 ring-brand-500' : ''}"
                      title="Нажмите для смены товара"
                    >
                      <span class="font-mono text-xs text-slate-500">[{line.product.code}]</span>
                      {line.product.name}
                      <span class="text-xs text-slate-500">({line.product.unit})</span>
                    </button>
                  {:else}
                    <input
                      type="text"
                      placeholder="Код или название…"
                      bind:value={line.productSearch}
                      oninput={() => onSearchInput(line)}
                      onkeydown={(e) => onProductKeyDown(e, line, lineIdx)}
                      onfocus={() => { navCell = { row: lineIdx, col: 0 }; }}
                      data-nav={`${lineIdx}-0`}
                      data-row={lineIdx}
                      data-col={0}
                      use:focusEnd
                      class="w-full rounded bg-transparent px-2 py-1.5 text-sm hover:bg-slate-700/30 focus:bg-slate-700 focus:outline-none focus:ring-1 focus:ring-brand-500"
                    />
                    {#if line.searching}
                      <div class="absolute left-0 top-full z-10 mt-1 rounded-lg bg-slate-700 px-3 py-2 text-xs text-slate-400 shadow-lg">
                        Поиск…
                      </div>
                    {:else if line.searchResults.length > 0}
                      <ul class="absolute left-0 top-full z-10 mt-1 max-h-48 w-full overflow-y-auto rounded-lg border border-slate-600 bg-slate-800 shadow-lg">
                        {#each line.searchResults as prod, prodIdx (prod.id)}
                          <li>
                            <button
                              type="button"
                              onclick={() => selectProduct(line, prod)}
                              class="w-full px-3 py-2 text-left text-sm hover:bg-slate-700 transition {line.searchHighlight === prodIdx ? 'bg-brand-700 !text-white' : ''}"
                            >
                              <span class="font-mono text-xs text-slate-400">[{prod.code}]</span>
                              {prod.name}
                              <span class="text-xs text-slate-500">{prod.unit}</span>
                            </button>
                          </li>
                        {/each}
                      </ul>
                    {/if}
                  {/if}
                </div>
              </td>
              <!-- %НДС -->
              <!-- Удалено: НДС 20% фиксирован -->
              <!-- Кол-во -->
              <td class="px-3 py-2">
                {#if isEditing(lineIdx, 1)}
                  <input
                    type="number" min="0.001" step="0.001"
                    bind:value={line.qty}
                    onkeydown={(e) => onCellKeyDown(e, lineIdx, 1)}
                    onblur={() => stopEditing(lineIdx, 1)}
                    data-row={lineIdx} data-col={1}
                    class="w-full rounded bg-slate-700 px-2 py-1.5 text-right text-sm focus:outline-none focus:ring-1 focus:ring-brand-500"
                  />
                {:else}
                  <div
                    tabindex="0"
                    data-nav={`${lineIdx}-1`}
                    onclick={() => startEditing(lineIdx, 1)}
                    onkeydown={(e) => onNavKeyDown(e, lineIdx, 1)}
                    onfocus={() => { navCell = { row: lineIdx, col: 1 }; }}
                    class="w-full cursor-default select-none rounded px-2 py-1.5 text-right text-sm text-slate-300 focus:outline-none {navCell.row === lineIdx && navCell.col === 1 ? 'ring-1 ring-brand-500' : 'hover:bg-slate-700/30'}"
                  >{line.qty}</div>
                {/if}
              </td>
              <!-- Цена (с НДС) -->
              <td class="px-3 py-2">
                {#if isEditing(lineIdx, 2)}
                  <input
                    type="number" min="0" step="0.01"
                    bind:value={line.price}
                    onkeydown={(e) => onCellKeyDown(e, lineIdx, 2)}
                    onblur={() => stopEditing(lineIdx, 2)}
                    data-row={lineIdx} data-col={2}
                    class="w-full rounded bg-slate-700 px-2 py-1.5 text-right text-sm focus:outline-none focus:ring-1 focus:ring-brand-500"
                  />
                {:else}
                  <div
                    tabindex="0"
                    data-nav={`${lineIdx}-2`}
                    onclick={() => startEditing(lineIdx, 2)}
                    onkeydown={(e) => onNavKeyDown(e, lineIdx, 2)}
                    onfocus={() => { navCell = { row: lineIdx, col: 2 }; }}
                    class="w-full cursor-default select-none rounded px-2 py-1.5 text-right text-sm text-slate-300 focus:outline-none {navCell.row === lineIdx && navCell.col === 2 ? 'ring-1 ring-brand-500' : 'hover:bg-slate-700/30'}"
                  >{line.price}</div>
                {/if}
              </td>
              <!-- Сумма (редактируемая) -->
              <td class="px-3 py-2">
                {#if isEditing(lineIdx, 3)}
                  <input
                    type="number" min="0" step="0.01"
                    value={line.qty * line.price}
                    onchange={(e) => onSumInput(line, (e.target as HTMLInputElement).value)}
                    onkeydown={(e) => onCellKeyDown(e, lineIdx, 3)}
                    onblur={() => stopEditing(lineIdx, 3)}
                    data-row={lineIdx} data-col={3}
                    class="w-full rounded bg-slate-700 px-2 py-1.5 text-right text-sm focus:outline-none focus:ring-1 focus:ring-brand-500"
                  />
                {:else}
                  <div
                    tabindex="0"
                    data-nav={`${lineIdx}-3`}
                    onclick={() => startEditing(lineIdx, 3)}
                    onkeydown={(e) => onNavKeyDown(e, lineIdx, 3)}
                    onfocus={() => { navCell = { row: lineIdx, col: 3 }; }}
                    class="w-full cursor-default select-none rounded px-2 py-1.5 text-right text-sm text-slate-300 focus:outline-none {navCell.row === lineIdx && navCell.col === 3 ? 'ring-1 ring-brand-500' : 'hover:bg-slate-700/30'}"
                  >{(line.qty * line.price).toFixed(2)}</div>
                {/if}
              </td>
              <!-- Цена б/НДС (редактируемая) -->
              <td class="px-3 py-2">
                {#if isEditing(lineIdx, 4)}
                  <input
                    type="number" min="0" step="0.01"
                    value={linePriceExcl(line).toFixed(2)}
                    onchange={(e) => onPriceExclInput(line, (e.target as HTMLInputElement).value)}
                    onkeydown={(e) => onCellKeyDown(e, lineIdx, 4)}
                    onblur={() => stopEditing(lineIdx, 4)}
                    data-row={lineIdx} data-col={4}
                    class="w-full rounded bg-slate-700 px-2 py-1.5 text-right text-sm text-slate-400 focus:outline-none focus:ring-1 focus:ring-brand-500"
                  />
                {:else}
                  <div
                    tabindex="0"
                    data-nav={`${lineIdx}-4`}
                    onclick={() => startEditing(lineIdx, 4)}
                    onkeydown={(e) => onNavKeyDown(e, lineIdx, 4)}
                    onfocus={() => { navCell = { row: lineIdx, col: 4 }; }}
                    class="w-full cursor-default select-none rounded px-2 py-1.5 text-right text-sm text-slate-400 focus:outline-none {navCell.row === lineIdx && navCell.col === 4 ? 'ring-1 ring-brand-500' : 'hover:bg-slate-700/30'}"
                  >{linePriceExcl(line).toFixed(2)}</div>
                {/if}
              </td>
              <!-- Сумма б/НДС (редактируемая) -->
              <td class="px-3 py-2">
                {#if isEditing(lineIdx, 5)}
                  <input
                    type="number" min="0" step="0.01"
                    value={lineSumExcl(line).toFixed(2)}
                    onchange={(e) => onSumExclInput(line, (e.target as HTMLInputElement).value)}
                    onkeydown={(e) => onCellKeyDown(e, lineIdx, 5)}
                    onblur={() => stopEditing(lineIdx, 5)}
                    data-row={lineIdx} data-col={5}
                    class="w-full rounded bg-slate-700 px-2 py-1.5 text-right text-sm text-slate-400 focus:outline-none focus:ring-1 focus:ring-brand-500"
                  />
                {:else}
                  <div
                    tabindex="0"
                    data-nav={`${lineIdx}-5`}
                    onclick={() => startEditing(lineIdx, 5)}
                    onkeydown={(e) => onNavKeyDown(e, lineIdx, 5)}
                    onfocus={() => { navCell = { row: lineIdx, col: 5 }; }}
                    class="w-full cursor-default select-none rounded px-2 py-1.5 text-right text-sm text-slate-400 focus:outline-none {navCell.row === lineIdx && navCell.col === 5 ? 'ring-1 ring-brand-500' : 'hover:bg-slate-700/30'}"
                  >{lineSumExcl(line).toFixed(2)}</div>
                {/if}
              </td>
              <!-- Удалить строку -->
              <td class="px-2 py-2 text-center">
                <button
                  type="button"
                  onclick={() => removeLine(line.uid)}
                  class="text-slate-600 hover:text-rose-400 transition"
                  title="Удалить строку"
                >?</button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>

    <!-- Добавить строку -->
    <div class="pb-2">
      <!-- кнопка перенесена в подвал -->
    </div>

  </div>

  <!-- Фиксированный подвал: итого + кнопки -->
  <div class="border-t border-slate-700 bg-slate-900 px-4 py-3">
    {#if errorMsg}
      <div class="mb-2 rounded-lg bg-rose-900/30 p-2 text-sm text-rose-300">{errorMsg}</div>
    {/if}
    <div class="flex items-center gap-3">
      <button
        type="button"
        onclick={addLine}
        class="rounded-lg bg-slate-700 px-4 py-2.5 text-sm hover:bg-slate-600 transition"
        title="Добавить строку (Insert)"
      >+ Добавить строку</button>
      <div class="h-5 w-px bg-slate-700"></div>
      <button
        type="button"
        onclick={saveAndPost}
        disabled={saving || posting}
        class="rounded-lg bg-brand-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-brand-500 disabled:opacity-50 transition"
      >
        {posting ? '? Сохранение…' : 'Сохранить'}
      </button>
      <a
        href="/accountant/invoices"
        class="text-sm text-slate-400 hover:text-slate-200 transition"
      >Отмена</a>
      <div class="ml-auto text-right">
        <div class="text-xs text-slate-400">Итого:</div>
        <div class="text-xl font-bold text-emerald-300">{formatMoney(total)}</div>
      </div>
    </div>
  </div>

</main>
