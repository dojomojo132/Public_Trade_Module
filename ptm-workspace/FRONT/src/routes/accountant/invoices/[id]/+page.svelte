<script lang="ts">
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import Header from '$lib/components/Header.svelte';
  import { authStore } from '$lib/stores/auth.svelte';
  import { apiFetch } from '$lib/api/client';
  import { formatMoney } from '$lib/utils';

  interface DocLine {
    line_number: number;
    product_id: string;
    product_code: string;
    product_name: string;
    unit: string;
    quantity: string;
    price: string;
    line_total: string;
  }

  interface Doc {
    id: string;
    doc_number: string | null;
    doc_type: string;
    doc_date: string;
    posted: boolean;
    total_amount: string;
    warehouse_id: string | null;
    warehouse_name: string | null;
    counterparty_id: string | null;
    counterparty_name: string | null;
    lines: DocLine[];
  }

  let doc = $state<Doc | null>(null);
  let loading = $state(false);
  let error = $state('');
  let actionLoading = $state(false);

  const docId = $derived($page.params.id);

  onMount(() => {
    if (!browser) return;
    init();
  });

  async function init() {
    await new Promise(r => setTimeout(r, 200));
    if (!authStore.isAuthenticated || (authStore.role !== 'accountant' && authStore.role !== 'admin')) {
      await goto('/login');
      return;
    }
    await loadDoc();
  }

  async function loadDoc() {
    loading = true;
    error = '';
    try {
      const res = await apiFetch<{ success: boolean; document: Doc }>(`/api/documents/${docId}`);
      doc = res.document;
    } catch (e) {
      error = e instanceof Error ? e.message : 'Ошибка загрузки';
    } finally {
      loading = false;
    }
  }

  function formatDate(iso: string) {
    return new Date(iso).toLocaleString('ru-RU', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit'
    });
  }

  async function doPost() {
    if (!doc) return;
    actionLoading = true;
    error = '';
    try {
      await apiFetch(`/api/documents/${doc.id}/post`, { method: 'POST' });
      await loadDoc();
    } catch (e) {
      error = e instanceof Error ? e.message : 'Ошибка проведения';
    } finally {
      actionLoading = false;
    }
  }

  async function doUnpost() {
    if (!doc) return;
    actionLoading = true;
    error = '';
    try {
      await apiFetch(`/api/documents/${doc.id}/unpost`, { method: 'POST' });
      await loadDoc();
    } catch (e) {
      error = e instanceof Error ? e.message : 'Ошибка отмены проведения';
    } finally {
      actionLoading = false;
    }
  }
</script>

<svelte:head><title>PTM — Накладная</title></svelte:head>

<Header />

<main class="flex flex-1 flex-col overflow-hidden">
  <div class="flex-1 overflow-y-auto p-4">

    <div class="mb-4 flex items-center gap-3">
      <a href="/accountant/invoices" class="text-slate-400 hover:text-slate-200 transition">← Накладные</a>
    </div>

    {#if loading}
      <div class="flex h-40 items-center justify-center text-slate-500">⏳ Загрузка…</div>
    {:else if error}
      <div class="rounded-lg bg-rose-900/30 p-4 text-rose-300">{error}</div>
    {:else if doc}
      <!-- Шапка -->
      <div class="mb-4 rounded-xl border border-slate-700 bg-slate-800 p-4">
        <div class="mb-2 flex items-center justify-between">
          <h1 class="text-lg font-semibold">
            Накладная {doc.doc_number ?? doc.id.slice(0, 8) + '…'}
          </h1>
          {#if doc.posted}
            <span class="rounded-full bg-emerald-900/40 px-3 py-1 text-sm text-emerald-300">✓ Проведена</span>
          {:else}
            <span class="rounded-full bg-amber-900/40 px-3 py-1 text-sm text-amber-300">● Черновик</span>
          {/if}
        </div>
        <div class="grid grid-cols-2 gap-2 text-sm sm:grid-cols-4">
          <div>
            <div class="text-xs text-slate-400">Дата</div>
            <div>{formatDate(doc.doc_date)}</div>
          </div>
          <div>
            <div class="text-xs text-slate-400">Поставщик</div>
            <div>{doc.counterparty_name ?? '—'}</div>
          </div>
          <div>
            <div class="text-xs text-slate-400">Склад</div>
            <div>{doc.warehouse_name ?? '—'}</div>
          </div>
          <div>
            <div class="text-xs text-slate-400">Сумма</div>
            <div class="font-bold text-emerald-300">{formatMoney(Number(doc.total_amount))}</div>
          </div>
        </div>
      </div>

      <!-- Строки -->
      <div class="mb-4 overflow-x-auto rounded-xl border border-slate-700">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-slate-700 bg-slate-800 text-left">
              <th class="px-4 py-2 text-slate-400">№</th>
              <th class="px-4 py-2 text-slate-400">Товар</th>
              <th class="px-4 py-2 text-right text-slate-400">Кол-во</th>
              <th class="px-4 py-2 text-right text-slate-400">Цена</th>
              <th class="px-4 py-2 text-right text-slate-400">Сумма</th>
            </tr>
          </thead>
          <tbody>
            {#each doc.lines as ln (ln.line_number)}
              <tr class="border-b border-slate-800">
                <td class="px-4 py-2 text-slate-500">{ln.line_number}</td>
                <td class="px-4 py-2">
                  <span class="font-mono text-xs text-slate-500">[{ln.product_code}]</span>
                  {ln.product_name}
                  <span class="text-xs text-slate-500">{ln.unit}</span>
                </td>
                <td class="px-4 py-2 text-right">{ln.quantity}</td>
                <td class="px-4 py-2 text-right">{formatMoney(Number(ln.price))}</td>
                <td class="px-4 py-2 text-right font-mono text-emerald-300">{formatMoney(Number(ln.line_total))}</td>
              </tr>
            {/each}
          </tbody>
          <tfoot>
            <tr class="bg-slate-800">
              <td colspan="4" class="px-4 py-2 text-right font-medium text-slate-400">Итого:</td>
              <td class="px-4 py-2 text-right font-bold font-mono text-emerald-300">
                {formatMoney(Number(doc.total_amount))}
              </td>
            </tr>
          </tfoot>
        </table>
      </div>

      <!-- Кнопки действий -->
      <div class="flex items-center gap-3">
        {#if !doc.posted}
          <a
            href="/accountant/invoices/new?edit={doc.id}"
            class="rounded-lg bg-slate-700 px-5 py-2.5 text-sm font-medium hover:bg-slate-600 transition"
          >✎ Редактировать</a>
          <button
            type="button"
            onclick={doPost}
            disabled={actionLoading}
            class="rounded-lg bg-brand-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-brand-500 disabled:opacity-50 transition"
          >
            {actionLoading ? '⏳…' : '✓ Провести'}
          </button>
        {:else}
          <button
            type="button"
            onclick={doUnpost}
            disabled={actionLoading}
            class="rounded-lg bg-slate-700 px-5 py-2.5 text-sm font-medium hover:bg-slate-600 disabled:opacity-50 transition"
          >
            {actionLoading ? '⏳…' : '⊘ Исключить из проведения'}
          </button>
        {/if}
      </div>
    {/if}

  </div>
</main>
