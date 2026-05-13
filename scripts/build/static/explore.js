/* explore.js — client-side filter + global address search.
 *
 * Loads docs/dashboard/data/events.json and renders a filterable table.
 * No build step, no bundler — vanilla ES module pattern.
 *
 * B9: URL state encoding — filters reflected in querystring; shareable views.
 * B10: Column sort (click th[data-sort-key]) + click-through links.
 */

(function () {
  let allEvents = [];
  let currentFilters = {};
  let sortState = { key: "action_date", desc: true };

  async function loadEvents() {
    const r = await fetch("data/events.json");
    return await r.json();
  }

  // ── B9: URL state ──────────────────────────────────────────────────────────

  function writeUrlState(f) {
    const params = new URLSearchParams();
    if (f.search) params.set("q", f.search);
    ["chain", "mechanism_type", "status", "confidence"].forEach((name) => {
      if (f[name] && f[name].size) {
        params.set(name, Array.from(f[name]).join(","));
      }
    });
    if (f.date_from) params.set("from", f.date_from);
    if (f.date_to) params.set("to", f.date_to);
    const newUrl =
      window.location.pathname +
      (params.toString() ? "?" + params.toString() : "");
    history.replaceState(null, "", newUrl);
  }

  function readUrlState() {
    const p = new URLSearchParams(window.location.search);
    if (p.has("q")) document.getElementById("search-input").value = p.get("q");
    ["chain", "mechanism_type", "status", "confidence"].forEach((name) => {
      if (p.has(name)) {
        const wanted = new Set(p.get(name).split(","));
        document.querySelectorAll(`input[name="${name}"]`).forEach((el) => {
          el.checked = wanted.has(el.value);
        });
      }
    });
    if (p.has("from"))
      document.querySelector('input[name="date_from"]').value = p.get("from");
    if (p.has("to"))
      document.querySelector('input[name="date_to"]').value = p.get("to");
  }

  // ── Filters ────────────────────────────────────────────────────────────────

  function readFilters() {
    const f = {};
    f.search = document.getElementById("search-input").value.trim().toLowerCase();
    ["chain", "mechanism_type", "status", "confidence"].forEach((name) => {
      const checked = Array.from(
        document.querySelectorAll(`input[name="${name}"]:checked`)
      ).map((el) => el.value);
      f[name] = new Set(checked);
    });
    f.date_from = document.querySelector('input[name="date_from"]').value;
    f.date_to = document.querySelector('input[name="date_to"]').value;
    return f;
  }

  function applyFilters(events, f) {
    return events.filter((ev) => {
      if (f.chain.size && !f.chain.has(ev.chain)) return false;
      if (f.mechanism_type.size && !f.mechanism_type.has(ev.mechanism_type)) return false;
      if (f.status.size && !f.status.has(ev.status)) return false;
      if (f.confidence.size && !f.confidence.has(ev.confidence)) return false;
      if (f.date_from && ev.action_date < f.date_from) return false;
      if (f.date_to && ev.action_date > f.date_to) return false;
      if (f.search) {
        const q = f.search;
        const haystack = [
          ev.target_identifier,
          ev.trigger_id,
          ev.target_category,
          ev.notes_path,
        ]
          .filter(Boolean)
          .join(" ")
          .toLowerCase();
        if (!haystack.includes(q)) return false;
      }
      return true;
    });
  }

  // ── B10: Sort ──────────────────────────────────────────────────────────────

  function sortEvents(events) {
    const key = sortState.key;
    const dir = sortState.desc ? -1 : 1;
    return [...events].sort((a, b) => {
      const va = (a[key] ?? "").toString();
      const vb = (b[key] ?? "").toString();
      return va < vb ? -1 * dir : va > vb ? 1 * dir : 0;
    });
  }

  function bindSortHeaders() {
    document.querySelectorAll(".result-table th[data-sort-key]").forEach((th) => {
      th.addEventListener("click", () => {
        const key = th.dataset.sortKey;
        if (sortState.key === key) {
          sortState.desc = !sortState.desc;
        } else {
          sortState.key = key;
          sortState.desc = true;
        }
        document
          .querySelectorAll(".result-table th")
          .forEach((h) => delete h.dataset.sortActive);
        th.dataset.sortActive = "1";
        refresh();
      });
    });
  }

  // ── Render ─────────────────────────────────────────────────────────────────

  function renderRow(ev) {
    const tr = document.createElement("tr");

    const addressDisplay = ev.notes_path
      ? `<a href="notes/${ev.notes_path.replace("notes/", "").replace(".md", ".html")}"><span class="address-mono">${ev.target_identifier || ""}</span></a>`
      : `<span class="address-mono">${ev.target_identifier || ""}</span>`;

    const triggerDisplay = ev.trigger_id
      ? `<a href="triggers.html#${ev.trigger_id}">${ev.trigger_id}</a>`
      : `<span class="no-trigger">—</span>`;

    const cells = [
      ev.action_date || "",
      ev.mechanism_type || "",
      ev.chain || "",
      addressDisplay,
      triggerDisplay,
      ev.status || "",
      ev.confidence || "",
    ];
    cells.forEach((c) => {
      const td = document.createElement("td");
      td.innerHTML = c;
      tr.appendChild(td);
    });
    return tr;
  }

  function render(filtered) {
    const body = document.getElementById("results-body");
    body.innerHTML = "";
    // Cap render at first 500 rows for performance; reader can refine filters.
    const display = filtered.slice(0, 500);
    display.forEach((ev) => body.appendChild(renderRow(ev)));
    document.getElementById("result-count").textContent = filtered.length;
    const bl = filtered.filter((e) => e.mechanism_type === "BLACKLIST").length;
    const ub = filtered.filter((e) => e.mechanism_type === "UNBLACKLIST").length;
    document.getElementById("bl-count").textContent = bl;
    document.getElementById("ub-count").textContent = ub;
  }

  // ── Main loop ──────────────────────────────────────────────────────────────

  function refresh() {
    currentFilters = readFilters();
    writeUrlState(currentFilters);
    let filtered = applyFilters(allEvents, currentFilters);
    filtered = sortEvents(filtered);
    render(filtered);
  }

  function bindEvents() {
    document.getElementById("search-input").addEventListener("input", refresh);
    document
      .querySelectorAll('.filter-chips input, input[name="date_from"], input[name="date_to"]')
      .forEach((el) => el.addEventListener("change", refresh));
  }

  loadEvents().then((events) => {
    allEvents = events;
    readUrlState();
    bindSortHeaders();
    bindEvents();
    refresh();
  });
})();
