const API_BASE = "";

let author = localStorage.getItem("ptm_inv_author") || "";
let warehouse = "";
let docId = "";
let activeLine = null;

function $(id) { return document.getElementById(id); }

function show(name) {
  document.querySelectorAll(".screen").forEach((el) => el.classList.remove("active"));
  $(name).classList.add("active");
}

function setError(id, msg) { $(id).textContent = msg || ""; }

async function api(path, opts) {
  const resp = await fetch(API_BASE + path, Object.assign({
    headers: { "Content-Type": "application/json" },
    credentials: "same-origin",
  }, opts || {}));
  const data = await resp.json().catch(() => ({ success: false, error: "Некорректный ответ" }));
  if (!resp.ok || data.success === false) {
    throw new Error(data.error || ("HTTP " + resp.status));
  }
  return data;
}

async function refreshStatus() {
  try {
    const d = await api("/inv/status");
    const el = $("statusBanner");
    if (d.online) {
      el.className = "banner on";
      el.textContent = "1С доступна · штрихкодов в кеше: " + d.barcodeCount;
    } else {
      el.className = "banner off";
      el.textContent = "1С недоступна · работаем с кешем (" + d.barcodeCount + " ШК)";
    }
    el.style.display = "block";
  } catch (e) {
    $("statusBanner").style.display = "none";
  }
}

async function boot() {
  try {
    await api("/me");
    if (!author) {
      show("nameScreen");
      return;
    }
    await loadWarehouses();
  } catch (e) {
    show("loginScreen");
  }
}

$("loginForm").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  setError("loginError", "");
  try {
    await api("/login", {
      method: "POST",
      body: JSON.stringify({ username: $("username").value, password: $("password").value }),
    });
    if (!author) show("nameScreen");
    else await loadWarehouses();
  } catch (e) {
    setError("loginError", e.message);
  }
});

$("nameGo").addEventListener("click", async () => {
  const name = $("authorName").value.trim();
  if (!name) { setError("nameError", "Укажите имя"); return; }
  author = name;
  localStorage.setItem("ptm_inv_author", author);
  await loadWarehouses();
});

async function loadWarehouses() {
  setError("whError", "");
  await refreshStatus();
  try {
    const d = await api("/inv/warehouses");
    const box = $("whList");
    if (!d.items.length) {
      box.innerHTML = "<p>Кеш складов пуст. Нажмите «Синхронизировать».</p>";
    } else {
      box.innerHTML = d.items.map((w) => (
        `<div class="card" onclick="pickWarehouse('${w.id}')"><b>${escapeHtml(w.name || w.code || w.id)}</b></div>`
      )).join("");
    }
    show("whScreen");
  } catch (e) {
    setError("whError", e.message);
    show("whScreen");
  }
}

function pickWarehouse(id) {
  warehouse = id;
  loadDocs();
}
window.pickWarehouse = pickWarehouse;

async function loadDocs() {
  setError("docsError", "");
  $("docsTitle").textContent = "Переучёт";
  try {
    const d = await api("/inv/docs?warehouse=" + encodeURIComponent(warehouse));
    $("docsList").innerHTML = d.items.map((doc) => (
      `<div class="card" onclick="openDoc('${doc.id}')">
        <b>${escapeHtml(doc.comment)}</b>
        <div class="meta">${escapeHtml(doc.author)} · строк: ${doc.lines} · ${escapeHtml(doc.status)}</div>
      </div>`
    )).join("") || "<p>Нет черновиков</p>";
    show("docsScreen");
  } catch (e) {
    setError("docsError", e.message);
    show("docsScreen");
  }
}

$("createDoc").addEventListener("click", async () => {
  const comment = $("newComment").value.trim();
  setError("docsError", "");
  try {
    const d = await api("/inv/docs", {
      method: "POST",
      body: JSON.stringify({ warehouse, comment, author }),
    });
    $("newComment").value = "";
    openDoc(d.id);
  } catch (e) {
    setError("docsError", e.message);
  }
});

async function openDoc(id) {
  docId = id;
  setError("docError", "");
  try {
    const d = await api("/inv/doc?id=" + encodeURIComponent(id));
    $("docTitle").textContent = d.comment;
    $("docMeta").textContent = d.author + " · " + d.status + (d.error ? " · " + d.error : "");
    renderLines(d.items);
    $("qtyBox").style.display = "none";
    show("docScreen");
    $("barcodeInput").focus();
  } catch (e) {
    setError("docsError", e.message);
  }
}
window.openDoc = openDoc;

function renderLines(items) {
  $("lines").innerHTML = items.map((it) => (
    `<div class="line ${it.line === activeLine ? "active" : ""}" data-line="${it.line}">
      <div>${escapeHtml(it.name)}<div class="meta">${escapeHtml(it.barcode)}</div></div>
      <div><b>${it.qty}</b></div>
    </div>`
  )).join("") || "<p>Пусто. Отсканируйте штрихкод.</p>";
}

async function doScan() {
  const barcode = $("barcodeInput").value.trim();
  if (!barcode) return;
  setError("docError", "");
  try {
    const d = await api("/inv/scan", {
      method: "POST",
      body: JSON.stringify({ id: docId, barcode }),
    });
    $("barcodeInput").value = "";
    activeLine = d.line;
    $("qtyInput").value = d.qty === 0 ? "" : d.qty;
    $("qtyBox").style.display = "block";
    $("qtyLabel").textContent = d.name;
    $("qtyInput").focus();
    const doc = await api("/inv/doc?id=" + encodeURIComponent(docId));
    renderLines(doc.items);
  } catch (e) {
    setError("docError", e.message);
  }
}

$("scanBtn").addEventListener("click", doScan);
$("barcodeInput").addEventListener("keydown", (e) => { if (e.key === "Enter") doScan(); });

$("qtySave").addEventListener("click", saveQty);
$("qtyInput").addEventListener("keydown", (e) => { if (e.key === "Enter") saveQty(); });

async function saveQty() {
  const qty = Number($("qtyInput").value);
  if (!Number.isFinite(qty)) { setError("docError", "Некорректное количество"); return; }
  try {
    await api("/inv/qty", {
      method: "POST",
      body: JSON.stringify({ id: docId, line: activeLine, qty }),
    });
    $("qtyBox").style.display = "none";
    const doc = await api("/inv/doc?id=" + encodeURIComponent(docId));
    renderLines(doc.items);
    $("barcodeInput").focus();
  } catch (e) {
    setError("docError", e.message);
  }
}

$("deleteDoc").addEventListener("click", async () => {
  if (!confirm("Удалить черновик?")) return;
  try {
    await api("/inv/docs?id=" + encodeURIComponent(docId), { method: "DELETE" });
    loadDocs();
  } catch (e) {
    setError("docError", e.message);
  }
});

$("syncBtn").addEventListener("click", async () => {
  setError("whError", "");
  try {
    await api("/inv/sync", { method: "POST" });
    await loadWarehouses();
  } catch (e) {
    setError("whError", e.message);
    refreshStatus();
  }
});

$("backDocs").addEventListener("click", loadDocs);
$("backWh").addEventListener("click", loadWarehouses);

function escapeHtml(s) {
  return String(s || "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

boot();
