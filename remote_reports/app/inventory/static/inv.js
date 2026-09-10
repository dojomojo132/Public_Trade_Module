const API_BASE = "";

let author = localStorage.getItem("ptm_inv_author") || "";
let warehouse = "";
let docId = "";
let activeLine = null;

function $(id) { return document.getElementById(id); }

function show(name) {
  document.querySelectorAll(".screen").forEach((el) => { el.hidden = el.id !== name; });
}

function flash(id, msg) {
  const el = $(id);
  if (!el) return;
  if (!msg) { el.hidden = true; el.textContent = ""; return; }
  el.hidden = false;
  el.textContent = msg;
}

async function api(path, opts) {
  const resp = await fetch(API_BASE + path, Object.assign({
    headers: { "Content-Type": "application/json" },
    credentials: "same-origin",
  }, opts || {}));
  if (resp.status === 401 || resp.status === 302) {
    window.location.href = "/login";
    throw new Error("Нужна авторизация");
  }
  if (resp.redirected && resp.url.indexOf("/login") >= 0) {
    window.location.href = "/login";
    throw new Error("Нужна авторизация");
  }
  const data = await resp.json().catch(() => ({ success: false, error: "Некорректный ответ" }));
  if (!resp.ok || data.success === false) {
    throw new Error(data.error || ("HTTP " + resp.status));
  }
  return data;
}

async function refreshStatus() {
  try {
    const d = await api("/inv/status");
    const el = $("ib-status");
    el.setAttribute("data-state", d.online ? "online" : "offline");
    if (!d.ibConfigured) {
      el.setAttribute("data-state", "offline");
      el.textContent = "Нет 1С";
      return;
    }
    el.textContent = d.online
      ? ("1С · " + d.barcodeCount + " ШК")
      : ("Кеш · " + d.barcodeCount + " ШК");
  } catch (e) {
    $("ib-status").setAttribute("data-state", "offline");
    $("ib-status").textContent = "Офлайн";
  }
}

async function boot() {
  if (!author) {
    show("nameScreen");
    await refreshStatus();
    return;
  }
  await loadWarehouses();
}

$("nameGo").addEventListener("click", async () => {
  const name = $("authorName").value.trim();
  if (!name) { flash("nameError", "Укажите имя"); return; }
  author = name;
  localStorage.setItem("ptm_inv_author", author);
  await loadWarehouses();
});

async function loadWarehouses() {
  flash("whError", "");
  await refreshStatus();
  try {
    const d = await api("/inv/warehouses");
    const box = $("whList");
    if (!d.items.length) {
      box.innerHTML = "<div class=\"panel form-card\"><p class=\"lede\">Кеш складов пуст. Нажмите «Синхронизировать с 1С». Ссылка на ИБ берётся из <a href=\"/settings\">Настроек</a> отчётов — отдельный адрес 1С для телефона не нужен.</p></div>";
    } else {
      box.innerHTML = d.items.map((w) => (
        `<a class="panel report-card" href="#" data-wh="${w.id}">
          <h2>${escapeHtml(w.name || w.code || w.id)}</h2>
          <p>${escapeHtml(w.code || "")}</p>
          <span class="go">Открыть →</span>
        </a>`
      )).join("");
      box.querySelectorAll("[data-wh]").forEach((el) => {
        el.addEventListener("click", (ev) => {
          ev.preventDefault();
          pickWarehouse(el.getAttribute("data-wh"));
        });
      });
    }
    show("whScreen");
  } catch (e) {
    flash("whError", e.message);
    show("whScreen");
  }
}

function pickWarehouse(id) {
  warehouse = id;
  loadDocs();
}

async function loadDocs() {
  flash("docsError", "");
  try {
    const d = await api("/inv/docs?warehouse=" + encodeURIComponent(warehouse));
    $("docsList").innerHTML = d.items.map((doc) => (
      `<a class="panel report-card" href="#" data-doc="${doc.id}">
        <h2>${escapeHtml(doc.comment)}</h2>
        <p>${escapeHtml(doc.author)} · строк: ${doc.lines} · ${escapeHtml(doc.status)}</p>
        <span class="go">Считать →</span>
      </a>`
    )).join("") || "<p class=\"lede\">Нет черновиков</p>";
    $("docsList").querySelectorAll("[data-doc]").forEach((el) => {
      el.addEventListener("click", (ev) => {
        ev.preventDefault();
        openDoc(el.getAttribute("data-doc"));
      });
    });
    show("docsScreen");
  } catch (e) {
    flash("docsError", e.message);
    show("docsScreen");
  }
}

$("createDoc").addEventListener("click", async () => {
  const comment = $("newComment").value.trim();
  flash("docsError", "");
  try {
    const d = await api("/inv/docs", {
      method: "POST",
      body: JSON.stringify({ warehouse, comment, author }),
    });
    $("newComment").value = "";
    openDoc(d.id);
  } catch (e) {
    flash("docsError", e.message);
  }
});

async function openDoc(id) {
  docId = id;
  flash("docError", "");
  try {
    const d = await api("/inv/doc?id=" + encodeURIComponent(id));
    $("docTitle").textContent = d.comment;
    $("docMeta").textContent = d.author + " · " + d.status + (d.error ? " · " + d.error : "");
    renderLines(d.items);
    $("qtyBox").hidden = true;
    show("docScreen");
    $("barcodeInput").focus();
  } catch (e) {
    flash("docsError", e.message);
  }
}

function renderLines(items) {
  $("lines").innerHTML = items.map((it) => (
    `<div class="line ${it.line === activeLine ? "active" : ""}">
      <div>${escapeHtml(it.name)}<div class="hint">${escapeHtml(it.barcode)}</div></div>
      <div><b>${it.qty}</b></div>
    </div>`
  )).join("") || "<p class=\"lede\">Пусто. Отсканируйте штрихкод.</p>";
}

async function doScan() {
  const barcode = $("barcodeInput").value.trim();
  if (!barcode) return;
  flash("docError", "");
  try {
    const d = await api("/inv/scan", {
      method: "POST",
      body: JSON.stringify({ id: docId, barcode }),
    });
    $("barcodeInput").value = "";
    activeLine = d.line;
    $("qtyInput").value = d.qty === 0 ? "" : d.qty;
    $("qtyBox").hidden = false;
    $("qtyLabel").textContent = d.name;
    $("qtyInput").focus();
    const doc = await api("/inv/doc?id=" + encodeURIComponent(docId));
    renderLines(doc.items);
  } catch (e) {
    flash("docError", e.message);
  }
}

$("scanBtn").addEventListener("click", doScan);
$("barcodeInput").addEventListener("keydown", (e) => { if (e.key === "Enter") doScan(); });
$("qtySave").addEventListener("click", saveQty);
$("qtyInput").addEventListener("keydown", (e) => { if (e.key === "Enter") saveQty(); });

async function saveQty() {
  const qty = Number($("qtyInput").value);
  if (!Number.isFinite(qty)) { flash("docError", "Некорректное количество"); return; }
  try {
    await api("/inv/qty", {
      method: "POST",
      body: JSON.stringify({ id: docId, line: activeLine, qty }),
    });
    $("qtyBox").hidden = true;
    const doc = await api("/inv/doc?id=" + encodeURIComponent(docId));
    renderLines(doc.items);
    $("barcodeInput").focus();
  } catch (e) {
    flash("docError", e.message);
  }
}

$("deleteDoc").addEventListener("click", async () => {
  if (!confirm("Удалить черновик?")) return;
  try {
    await api("/inv/docs?id=" + encodeURIComponent(docId), { method: "DELETE" });
    loadDocs();
  } catch (e) {
    flash("docError", e.message);
  }
});

$("syncBtn").addEventListener("click", async () => {
  flash("whError", "");
  try {
    await api("/inv/sync", { method: "POST" });
    await loadWarehouses();
  } catch (e) {
    flash("whError", e.message);
    refreshStatus();
  }
});

$("backDocs").addEventListener("click", (e) => { e.preventDefault(); loadDocs(); });
$("backWh").addEventListener("click", (e) => { e.preventDefault(); loadWarehouses(); });

function escapeHtml(s) {
  return String(s || "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

boot();
