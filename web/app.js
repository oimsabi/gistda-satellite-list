/* GISTDA price list app — tabs, filter, sort, SVG chart. Data from data.js (PRICE_DATA). */
"use strict";

const DATA = PRICE_DATA;
const VAT = 1.07;

const state = {
  category: DATA.categories[0].id,
  search: "",
  satellite: "",
  resMin: null,
  resMax: null,
  priceMax: null,
  sortKey: null,
  sortDir: 1,
  vat: false,
  chartUnit: null,
  openNotes: new Set(),
};

const $ = (id) => document.getElementById(id);
const fmt = (n) => n == null ? null : Math.round(n).toLocaleString("th-TH");

function priceOf(v) { return v == null ? null : (state.vat ? v * VAT : v); }

function currentCategory() {
  return DATA.categories.find((c) => c.id === state.category);
}

function categoryRecords() {
  return DATA.records.filter((r) => r.category === state.category);
}

function filteredRecords() {
  const q = state.search.trim().toLowerCase();
  return categoryRecords().filter((r) => {
    if (q) {
      const hay = `${r.satellite} ${r.mode || ""} ${r.band || ""} ${r.polarization || ""}`.toLowerCase();
      if (!hay.includes(q)) return false;
    }
    if (state.satellite && r.satellite !== state.satellite) return false;
    if (state.resMin != null && r.resolution_m < state.resMin) return false;
    if (state.resMax != null && r.resolution_m > state.resMax) return false;
    if (state.priceMax != null) {
      const prices = [r.price_archive, r.price_tasking].filter((p) => p != null);
      if (!prices.length || Math.min(...prices) > state.priceMax) return false;
    }
    return true;
  });
}

function sortedRecords(rows) {
  if (!state.sortKey) return rows;
  const k = state.sortKey, dir = state.sortDir;
  return [...rows].sort((a, b) => {
    const av = a[k], bv = b[k];
    if (av == null && bv == null) return 0;
    if (av == null) return 1;           // N/A always last
    if (bv == null) return -1;
    if (typeof av === "number") return (av - bv) * dir;
    return String(av).localeCompare(String(bv), "th") * dir;
  });
}

/* ---------- tabs ---------- */
function renderTabs() {
  const nav = $("tabs");
  nav.innerHTML = "";
  DATA.categories.forEach((c) => {
    const btn = document.createElement("button");
    btn.className = "tab" + (c.id === state.category ? " active" : "");
    btn.setAttribute("role", "tab");
    btn.innerHTML = `<span class="tab-th">${c.name_th}</span><span class="tab-en">${c.name_en}</span>`;
    btn.onclick = () => {
      state.category = c.id;
      location.hash = c.id;
      state.satellite = "";
      state.sortKey = null;
      state.chartUnit = null;
      state.openNotes.clear();
      renderAll();
    };
    nav.appendChild(btn);
  });
}

/* ---------- filters ---------- */
function renderSatelliteFilter() {
  const sel = $("fSatellite");
  const sats = [...new Set(categoryRecords().map((r) => r.satellite))];
  sel.innerHTML = `<option value="">ทุกดาวเทียม · All satellites</option>` +
    sats.map((s) => `<option value="${s}" ${s === state.satellite ? "selected" : ""}>${s}</option>`).join("");
  sel.parentElement.style.display = "";
}

function bindFilters() {
  $("fSearch").addEventListener("input", (e) => { state.search = e.target.value; renderTable(); renderChart(); });
  $("fSatellite").addEventListener("change", (e) => { state.satellite = e.target.value; renderTable(); renderChart(); });
  const num = (v) => v === "" ? null : Number(v);
  $("fResMin").addEventListener("input", (e) => { state.resMin = num(e.target.value); renderTable(); renderChart(); });
  $("fResMax").addEventListener("input", (e) => { state.resMax = num(e.target.value); renderTable(); renderChart(); });
  $("fPriceMax").addEventListener("input", (e) => { state.priceMax = num(e.target.value); renderTable(); renderChart(); });
  $("fReset").addEventListener("click", () => {
    Object.assign(state, { search: "", satellite: "", resMin: null, resMax: null, priceMax: null });
    ["fSearch", "fResMin", "fResMax", "fPriceMax"].forEach((id) => { $(id).value = ""; });
    $("fSatellite").value = "";
    renderTable(); renderChart();
  });
  $("vatToggle").addEventListener("change", (e) => { state.vat = e.target.checked; renderTable(); renderChart(); });
}

/* ---------- table ---------- */
function columnsFor(rows) {
  const cat = currentCategory();
  const cols = [{ key: "satellite", th: "ดาวเทียม", en: "Satellite" }];
  if (rows.some((r) => r.mode)) cols.push({ key: "mode", th: "โหมด", en: "Mode" });
  if (rows.some((r) => r.band)) cols.push({ key: "band", th: "แบนด์", en: "Band" });
  cols.push({ key: "resolution_m", th: "รายละเอียดภาพ", en: "Resolution" });
  if (rows.some((r) => r.polarization)) cols.push({ key: "polarization", th: "Polarization", en: "" });
  cols.push({ key: "price_archive", th: cat.price_columns.archive.th, en: cat.price_columns.archive.en, num: true });
  cols.push({ key: "price_tasking", th: cat.price_columns.tasking.th, en: cat.price_columns.tasking.en, num: true });
  cols.push({ key: "price_unit", th: "หน่วย", en: "Unit" });
  return cols;
}

function renderTable() {
  const rows = sortedRecords(filteredRecords());
  const cols = columnsFor(categoryRecords());

  const thead = $("tableHead");
  thead.innerHTML = "<tr>" + cols.map((c) => {
    const arrow = state.sortKey === c.key ? `<span class="arrow">${state.sortDir === 1 ? "▲" : "▼"}</span>` : "";
    const sub = c.en ? `<br><span style="font-weight:400;color:var(--text-muted)">${c.en}</span>` : "";
    return `<th data-key="${c.key}" class="${c.num ? "num" : ""}">${c.th}${sub}${arrow}</th>`;
  }).join("") + "<th></th></tr>";

  thead.querySelectorAll("th[data-key]").forEach((th) => {
    th.onclick = () => {
      const k = th.dataset.key;
      if (state.sortKey === k) state.sortDir *= -1;
      else { state.sortKey = k; state.sortDir = 1; }
      renderTable();
    };
  });

  const tbody = $("tableBody");
  tbody.innerHTML = "";
  if (!rows.length) {
    tbody.innerHTML = `<tr><td class="empty-msg" colspan="${cols.length + 1}">ไม่พบข้อมูลตามตัวกรอง · No rows match the filters</td></tr>`;
  }
  rows.forEach((r, i) => {
    const tr = document.createElement("tr");
    tr.className = "data-row";
    const hasNotes = r.notes_th || r.min_order_th;
    const cells = cols.map((c) => {
      if (c.key === "satellite") return `<td class="sat-name">${r.satellite}</td>`;
      if (c.key === "resolution_m") return `<td>${r.resolution_label}</td>`;
      if (c.key === "price_unit") return `<td><span class="unit-badge">${r.price_unit}</span></td>`;
      if (c.num) {
        const v = fmt(priceOf(r[c.key]));
        return `<td class="num">${v ?? '<span class="na">N/A</span>'}</td>`;
      }
      return `<td>${r[c.key] ?? '<span class="na">—</span>'}</td>`;
    }).join("");
    const noteId = `${r.satellite}|${r.mode || ""}|${i}`;
    const open = state.openNotes.has(noteId);
    tr.innerHTML = cells + `<td>${hasNotes ? `<button class="note-toggle">${open ? "ซ่อน ▾" : "เงื่อนไข ▸"}</button>` : ""}</td>`;
    tbody.appendChild(tr);

    if (hasNotes) {
      tr.querySelector(".note-toggle").onclick = () => {
        open ? state.openNotes.delete(noteId) : state.openNotes.add(noteId);
        renderTable();
      };
      if (open) {
        const nr = document.createElement("tr");
        nr.className = "note-row";
        const lines = [];
        if (r.min_order_th) lines.push(`พื้นที่สั่งขั้นต่ำ · Min order: ${r.min_order_th} (${r.min_order_en})`);
        if (r.notes_th) lines.push(r.notes_th);
        if (r.notes_en) lines.push(r.notes_en);
        nr.innerHTML = `<td colspan="${cols.length + 1}">` +
          lines.map((l) => `<div class="note-line">${l}</div>`).join("") + "</td>";
        tbody.appendChild(nr);
      }
    }
  });

  $("resultCount").textContent = `${rows.length} / ${categoryRecords().length} รายการ · rows`;

  const notes = currentCategory();
  $("categoryNotes").innerHTML =
    notes.notes_th.map((t, i) => `<div>• ${t} — ${notes.notes_en[i]}</div>`).join("");
}

/* ---------- chart ---------- */
const S1 = () => getComputedStyle(document.documentElement).getPropertyValue("--series-1").trim();
const S2 = () => getComputedStyle(document.documentElement).getPropertyValue("--series-2").trim();

function renderChart() {
  const cat = currentCategory();
  const all = sortedRecords(filteredRecords());

  // one unit per chart — mixing THB/km² with THB/scene on one axis misleads
  const units = [...new Set(all.map((r) => r.price_unit))];
  if (!units.includes(state.chartUnit)) state.chartUnit = units[0] || null;
  const chips = $("unitChips");
  chips.innerHTML = "";
  if (units.length > 1) {
    units.forEach((u) => {
      const b = document.createElement("button");
      b.className = "unit-chip" + (u === state.chartUnit ? " active" : "");
      b.textContent = u;
      b.onclick = () => { state.chartUnit = u; renderChart(); };
      chips.appendChild(b);
    });
  }

  const rows = all.filter((r) => r.price_unit === state.chartUnit);
  const aLabel = `${cat.price_columns.archive.th} · ${cat.price_columns.archive.en}`;
  const tLabel = `${cat.price_columns.tasking.th} · ${cat.price_columns.tasking.en}`;
  $("chartLegend").innerHTML =
    `<span class="legend-item"><span class="legend-swatch" style="background:${S1()}"></span>${aLabel}</span>` +
    `<span class="legend-item"><span class="legend-swatch" style="background:${S2()}"></span>${tLabel}</span>`;

  const svg = $("chart");
  svg.innerHTML = "";
  if (!rows.length) { svg.setAttribute("height", 40); return; }

  const labelW = 235, valueW = 84, W = 1080;
  const plotX = labelW, plotW = W - labelW - valueW;
  const barH = 13, barGap = 2, groupPad = 9, rowH = barH * 2 + barGap + groupPad * 2;
  const topPad = 8, bottomPad = 26;
  const H = topPad + rows.length * rowH + bottomPad;
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  svg.setAttribute("width", W);
  svg.setAttribute("height", H);
  svg.style.minWidth = "760px";

  const maxV = Math.max(...rows.flatMap((r) => [priceOf(r.price_archive) || 0, priceOf(r.price_tasking) || 0]));
  const scale = (v) => (v / maxV) * plotW;
  const NS = "http://www.w3.org/2000/svg";
  const el = (tag, attrs) => {
    const e = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
    return e;
  };
  const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();

  // gridlines at clean ticks (hairline, recessive)
  const tickStep = niceStep(maxV);
  for (let t = tickStep; t <= maxV; t += tickStep) {
    const x = plotX + scale(t);
    svg.appendChild(el("line", { x1: x, y1: topPad, x2: x, y2: H - bottomPad, stroke: css("--gridline"), "stroke-width": 1 }));
    const txt = el("text", { x, y: H - 8, "text-anchor": "middle", "font-size": 11, fill: css("--text-muted") });
    txt.textContent = Math.round(t).toLocaleString("th-TH");
    svg.appendChild(txt);
  }
  // baseline
  svg.appendChild(el("line", { x1: plotX, y1: topPad, x2: plotX, y2: H - bottomPad, stroke: css("--baseline"), "stroke-width": 1 }));

  const showTips = rows.length <= 12;
  const tooltip = $("chartTooltip");

  rows.forEach((r, i) => {
    const y0 = topPad + i * rowH + groupPad;
    const name = r.mode ? `${r.satellite} — ${r.mode}` : r.satellite;
    const lbl = el("text", { x: labelW - 10, y: y0 + barH + barGap / 2 + 4, "text-anchor": "end", "font-size": 12.5, fill: css("--text-primary") });
    lbl.textContent = name.length > 32 ? name.slice(0, 31) + "…" : name;
    svg.appendChild(lbl);

    [["price_archive", S1(), 0, aLabel], ["price_tasking", S2(), barH + barGap, tLabel]].forEach(([key, color, dy, seriesLabel]) => {
      const raw = r[key];
      const v = priceOf(raw);
      const y = y0 + dy;
      if (v == null) {
        const na = el("text", { x: plotX + 6, y: y + barH - 3, "font-size": 10.5, fill: css("--text-muted") });
        na.textContent = "N/A";
        svg.appendChild(na);
        return;
      }
      const w = Math.max(scale(v), 2);
      // square at baseline, 4px rounded data-end
      const rr = Math.min(4, w / 2);
      const path = el("path", {
        d: `M${plotX},${y} h${w - rr} a${rr},${rr} 0 0 1 ${rr},${rr} v${barH - 2 * rr} a${rr},${rr} 0 0 1 -${rr},${rr} h${-(w - rr)} z`,
        fill: color,
      });
      path.style.cursor = "pointer";
      path.addEventListener("mousemove", (ev) => {
        const rect = svg.closest(".chart-section").getBoundingClientRect();
        tooltip.hidden = false;
        tooltip.innerHTML = `<div class="tt-title">${name}</div>` +
          `<div class="tt-line"><span class="legend-swatch" style="background:${color}"></span>${seriesLabel}</div>` +
          `<div class="tt-line">${fmt(v)} ${state.vat ? "(รวม VAT)" : ""} — ${r.price_unit}</div>`;
        tooltip.style.left = Math.min(ev.clientX - rect.left + 14, rect.width - 290) + "px";
        tooltip.style.top = (ev.clientY - rect.top + 14) + "px";
      });
      path.addEventListener("mouseleave", () => { tooltip.hidden = true; });
      svg.appendChild(path);

      if (showTips) {
        const vt = el("text", { x: plotX + w + 6, y: y + barH - 2.5, "font-size": 11, fill: css("--text-secondary") });
        vt.textContent = fmt(v);
        svg.appendChild(vt);
      }
    });
  });

  const note = document.querySelector(".chart-note");
  if (note) note.remove();
  const n = document.createElement("div");
  n.className = "chart-note";
  n.textContent = `หน่วย · Unit: ${state.chartUnit}${state.vat ? " — ราคารวม VAT 7% · incl. VAT" : " — ราคาไม่รวม VAT · excl. VAT"}`;
  svg.closest(".chart-section").appendChild(n);
}

function niceStep(maxV) {
  const raw = maxV / 5;
  const mag = Math.pow(10, Math.floor(Math.log10(raw)));
  const norm = raw / mag;
  const step = norm <= 1 ? 1 : norm <= 2 ? 2 : norm <= 5 ? 5 : 10;
  return step * mag;
}

/* ---------- theme ---------- */
function bindTheme() {
  const urlTheme = new URLSearchParams(location.search).get("theme");
  const saved = urlTheme || localStorage.getItem("gistda-theme");
  if (saved) document.documentElement.dataset.theme = saved;
  $("themeToggle").onclick = () => {
    const cur = document.documentElement.dataset.theme ||
      (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    const next = cur === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    localStorage.setItem("gistda-theme", next);
    renderChart(); // re-read series colors
  };
}

/* ---------- footer ---------- */
function renderFooter() {
  const m = DATA.meta;
  $("footer").innerHTML =
    `<div class="vat-note">** ${m.vat_note_th} · ${m.vat_note_en}</div>` +
    `<div>${m.contact.address_th}</div>` +
    `<div>โทร · Tel: ${m.contact.phone} &nbsp;|&nbsp; โทรสาร · Fax: ${m.contact.fax} &nbsp;|&nbsp; ` +
    `อีเมล · Email: <a href="mailto:${m.contact.email}">${m.contact.email}</a></div>` +
    `<div>ที่มา · Source: ${m.source}</div>`;
}

function renderAll() {
  renderTabs();
  renderSatelliteFilter();
  renderTable();
  renderChart();
}

const hashCat = location.hash.replace("#", "");
if (DATA.categories.some((c) => c.id === hashCat)) state.category = hashCat;

bindTheme();
bindFilters();
renderFooter();
renderAll();
