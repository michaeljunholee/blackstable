// Stablecoin Blacklisting — Overview dashboard
(function () {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  function cssVar(name) {
    return getComputedStyle(document.body).getPropertyValue(name).trim();
  }

  const State = {
    events: [],
    triggers: {},
    clusters: [],
    // Multi-select category filter — Set of categories that are ON
    activeCats: new Set(['ofac', 'court', 'hack', 'untriggered']),
    timeMin: null,
    timeMax: null,
    timeFullMin: null,
    timeFullMax: null,
    activeId: null,
    pinnedId: null,
  };

  function categoryOf(tType) {
    if (!tType) return 'untriggered';
    const t = String(tType).toUpperCase();
    if (t.includes('OFAC')) return 'ofac';
    if (t.includes('COURT')) return 'court';
    if (t.includes('HACK') || t.includes('EXCHANGE')) return 'hack';
    return 'other';
  }
  const CAT_LABEL = { ofac: 'OFAC sanction', court: 'Court order', hack: 'Hack response', untriggered: 'No public reason', other: 'Other' };

  // --- Annotations: marquee events to label inside the chart
  const ANNOTATIONS = [
    { date: '2025-11-04', mech: 'BLACKLIST', label: 'DPRK bankers', sub: 'OFAC SDN · 339 wallets', side: 'top' },
    { date: '2025-03-22', mech: 'UNBLACKLIST', label: 'Tornado Cash delisted', sub: '540 wallets unfrozen in 24h', side: 'bottom' },
    { date: '2023-07-21', mech: 'BLACKLIST', label: 'TC redesignation wave', sub: 'Summer 2023 · ~600 wallets', side: 'top' },
  ];

  async function load() {
    const [evRes, trRes] = await Promise.all([
      fetch('data/events.json').then(r => r.json()),
      fetch('data/triggers.json').then(r => r.json()),
    ]);
    State.events = evRes;
    State.triggers = Object.fromEntries(trRes.map(t => [t.trigger_id, t]));

    const map = new Map();
    for (const e of evRes) {
      const key = `${e.mechanism_type}|${e.action_date}`;
      if (!map.has(key)) {
        map.set(key, { date: e.action_date, mech: e.mechanism_type, evts: [], triggers: {} });
      }
      const c = map.get(key);
      c.evts.push(e);
      const tid = e.trigger_id;
      if (tid) c.triggers[tid] = (c.triggers[tid] || 0) + 1;
    }
    const clusters = [];
    for (const [, c] of map) {
      const total = c.evts.length;
      const attributed = c.evts.filter(x => x.trigger_id).length;
      let dominantTid = null, dominantN = 0;
      for (const [tid, n] of Object.entries(c.triggers)) {
        if (n > dominantN) { dominantN = n; dominantTid = tid; }
      }
      const tr = dominantTid ? State.triggers[dominantTid] : null;
      const category = tr ? categoryOf(tr.trigger_type) : 'untriggered';
      clusters.push({
        id: `${c.mech === 'BLACKLIST' ? 'bl' : 'ub'}_${c.date}`,
        date: c.date,
        mech: c.mech,
        count: total,
        attributed,
        category,
        triggerId: dominantTid,
        triggerDesc: tr ? tr.description : null,
        triggerType: tr ? tr.trigger_type : null,
        ts: new Date(c.date + 'T00:00:00Z').getTime(),
      });
    }
    clusters.sort((a, b) => a.ts - b.ts);
    State.clusters = clusters;
    const ts = clusters.map(c => c.ts);
    State.timeFullMin = Math.min(...ts);
    State.timeFullMax = Math.max(...ts);
    // Default window = full range so users see everything; brush narrowing is optional
    State.timeMin = State.timeFullMin;
    State.timeMax = State.timeFullMax;
    return clusters;
  }

  function inFilter(c) { return State.activeCats.has(c.category); }
  function inWindow(c) { return c.ts >= State.timeMin && c.ts <= State.timeMax; }
  function visibleClusters() { return State.clusters.filter(c => inFilter(c) && inWindow(c)); }

  function fmtNum(n) { return n >= 1000 ? n.toLocaleString() : String(n); }
  function fmtPct(n) { return (n * 100).toFixed(0) + '%'; }
  function fmtDate(d) {
    const dt = new Date(d + 'T00:00:00Z');
    return dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' });
  }
  function relUpdate(d) {
    const days = Math.floor((Date.now() - new Date(d + 'T00:00:00Z').getTime()) / 86400000);
    if (days < 1) return 'Updated today';
    if (days === 1) return 'Updated yesterday';
    if (days < 7) return `Updated ${days}d ago`;
    if (days < 30) return `Updated ${Math.floor(days/7)}w ago`;
    const dt = new Date(d + 'T00:00:00Z');
    return 'Updated ' + dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric', timeZone: 'UTC' });
  }

  function renderKPIs() {
    const vis = visibleClusters();
    const totalEvents = vis.reduce((s, c) => s + c.count, 0);
    const blEvents = vis.filter(c => c.mech === 'BLACKLIST').reduce((s, c) => s + c.count, 0);
    const ubEvents = vis.filter(c => c.mech === 'UNBLACKLIST').reduce((s, c) => s + c.count, 0);
    const attributed = vis.reduce((s, c) => s + c.attributed, 0);
    const attrPct = totalEvents > 0 ? (attributed / totalEvents) : 0;
    const blOnly = vis.filter(c => c.mech === 'BLACKLIST');
    const ubOnly = vis.filter(c => c.mech === 'UNBLACKLIST');
    const largestFreeze = blOnly.reduce((a, b) => (b.count > (a ? a.count : 0) ? b : a), null);
    const largestUnfreeze = ubOnly.reduce((a, b) => (b.count > (a ? a.count : 0) ? b : a), null);

    const months = new Map();
    for (const c of vis) {
      const m = c.date.slice(0, 7);
      months.set(m, (months.get(m) || 0) + (c.mech === 'BLACKLIST' ? c.count : 0));
    }
    const monthArr = Array.from(months.entries()).sort();

    const html = `
      <div class="kpi" data-kpi="total">
        <div class="k-label">Wallets affected (in view)</div>
        <div class="k-value">${fmtNum(totalEvents)}</div>
        <div class="k-sub">${fmtNum(blEvents)} freezes · ${fmtNum(ubEvents)} unfreezes</div>
        ${spark(monthArr, 'var(--bl)')}
      </div>
      <div class="kpi" data-kpi="attr">
        <div class="k-label"><span class="k-swatch" style="background:var(--bl)"></span>Public‑trigger share</div>
        <div class="k-value">${fmtPct(attrPct)}</div>
        <div class="k-unit">${fmtNum(attributed)} of ${fmtNum(totalEvents)} attributed</div>
        <div class="k-bar"><span style="width:${(attrPct * 100).toFixed(1)}%"></span></div>
      </div>
      <div class="kpi" data-kpi="largest-freeze">
        <div class="k-label"><span class="k-swatch" style="background:var(--bl)"></span>Largest freeze</div>
        <div class="k-value">${largestFreeze ? fmtNum(largestFreeze.count) : '—'}</div>
        <div class="k-unit">wallets</div>
        <div class="k-sub">${largestFreeze ? fmtDate(largestFreeze.date) + ' · ' + CAT_LABEL[largestFreeze.category] : '—'}</div>
      </div>
      <div class="kpi" data-kpi="largest-unfreeze">
        <div class="k-label"><span class="k-swatch" style="background:var(--ub)"></span>Largest unfreeze</div>
        <div class="k-value">${largestUnfreeze ? fmtNum(largestUnfreeze.count) : '—'}</div>
        <div class="k-unit">wallets</div>
        <div class="k-sub">${largestUnfreeze ? fmtDate(largestUnfreeze.date) + ' · ' + CAT_LABEL[largestUnfreeze.category] : '—'}</div>
      </div>
    `;
    $('#kpi-strip').innerHTML = html;
    $$('#kpi-strip .kpi').forEach(el => {
      el.addEventListener('mouseenter', () => kpiHighlight(el.dataset.kpi));
      el.addEventListener('mouseleave', () => kpiHighlight(null));
    });

    // Last-updated stamp — shows the date of last data observation
    const lastDate = State.clusters.length ? State.clusters[State.clusters.length - 1].date : null;
    if (lastDate && $('#last-updated')) {
      $('#last-updated').textContent = 'Last Updated: ' + fmtDate(lastDate);
    }
  }
  function spark(monthArr, color) {
    if (!monthArr.length) return '';
    const W = 180, H = 24;
    const max = Math.max(...monthArr.map(m => m[1]), 1);
    const step = monthArr.length > 1 ? W / (monthArr.length - 1) : 0;
    const pts = monthArr.map(([, v], i) => `${(i * step).toFixed(1)},${(H - (v / max) * H).toFixed(1)}`).join(' ');
    return `<svg class="k-spark" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none">
      <polyline points="${pts}" fill="none" stroke="${color}" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>
    </svg>`;
  }

  function kpiHighlight(kind) {
    if (!kind) {
      State.clusters.forEach(c => bubbleEl(c.id) && bubbleEl(c.id).classList.remove('dim'));
      return;
    }
    const set = new Set();
    const vis = visibleClusters();
    if (kind === 'attr') vis.filter(c => c.attributed > 0).forEach(c => set.add(c.id));
    else if (kind === 'largest-freeze') {
      const top = vis.filter(c => c.mech === 'BLACKLIST').sort((a, b) => b.count - a.count).slice(0, 1);
      top.forEach(c => set.add(c.id));
    }
    else if (kind === 'largest-unfreeze') {
      const top = vis.filter(c => c.mech === 'UNBLACKLIST').sort((a, b) => b.count - a.count).slice(0, 1);
      top.forEach(c => set.add(c.id));
    }
    else vis.forEach(c => set.add(c.id));
    State.clusters.forEach(c => {
      const el = bubbleEl(c.id); if (!el) return;
      if (set.has(c.id)) el.classList.remove('dim'); else el.classList.add('dim');
    });
  }
  function bubbleEl(id) { return document.querySelector(`[data-cid="${CSS.escape(id)}"]`); }

  // Draw (or remove) a clearly visible dashed ring around the currently
  // pinned bubble. Called from drawTimeline() so the halo persists across
  // any redraw (brush, filter toggle, theme switch), and from the click
  // handlers so the halo updates immediately on pin/unpin without a
  // full timeline rebuild.
  function updatePinHalo() {
    const svg = $('#timeline');
    if (!svg) return;
    const old = svg.querySelector('.tl-pin-halo');
    if (old) old.remove();
    if (!State.pinnedId) return;
    const bubble = bubbleEl(State.pinnedId);
    if (!bubble) return;
    const cx = parseFloat(bubble.getAttribute('cx'));
    const cy = parseFloat(bubble.getAttribute('cy'));
    const r = parseFloat(bubble.getAttribute('r'));
    const halo = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    halo.setAttribute('class', 'tl-pin-halo');
    halo.setAttribute('cx', cx);
    halo.setAttribute('cy', cy);
    halo.setAttribute('r', r + 7);
    halo.setAttribute('fill', 'none');
    svg.appendChild(halo);
  }

  // --- Timeline SVG ---
  const TL = { W: 1600, H: 460, pad: { l: 64, r: 28, t: 36, b: 38 } };
  function drawTimeline() {
    const svg = $('#timeline');
    svg.innerHTML = '';
    const innerW = TL.W - TL.pad.l - TL.pad.r;
    const blY = TL.pad.t + 92;
    const ubY = TL.H - TL.pad.b - 92;
    const axisY = (blY + ubY) / 2;

    const xMin = State.timeMin, xMax = State.timeMax;
    const xs = (ts) => TL.pad.l + ((ts - xMin) / (xMax - xMin)) * innerW;

    const startY = new Date(xMin).getUTCFullYear();
    const endY = new Date(xMax).getUTCFullYear();
    const ticks = [];
    for (let y = startY; y <= endY + 1; y++) {
      ticks.push({ ts: Date.UTC(y, 0, 1), label: String(y) });
    }
    let s = '';

    // Lane backgrounds — subtle freeze/unfreeze tint
    s += `<rect x="${TL.pad.l}" y="${TL.pad.t}" width="${innerW}" height="${(axisY - TL.pad.t).toFixed(1)}" fill="var(--bl-soft)" fill-opacity="0.18"/>`;
    s += `<rect x="${TL.pad.l}" y="${axisY}" width="${innerW}" height="${(TL.H - TL.pad.b - axisY).toFixed(1)}" fill="var(--ub-soft)" fill-opacity="0.18"/>`;

    // Year grid + labels
    for (const t of ticks) {
      const x = xs(t.ts);
      if (x < TL.pad.l - 1 || x > TL.W - TL.pad.r + 1) continue;
      s += `<line x1="${x.toFixed(1)}" y1="${TL.pad.t}" x2="${x.toFixed(1)}" y2="${TL.H - TL.pad.b}" stroke="var(--line)" stroke-width="0.5" stroke-dasharray="2,3" opacity="0.7"/>`;
      s += `<text x="${x.toFixed(1)}" y="${TL.H - TL.pad.b + 18}" text-anchor="middle" font-family="JetBrains Mono" font-size="10.5" fill="var(--ink-faint)">${t.label}</text>`;
    }

    // Lane baselines
    s += `<line x1="${TL.pad.l}" y1="${blY}" x2="${TL.W - TL.pad.r}" y2="${blY}" stroke="var(--ink)" stroke-width="0.5" opacity="0.18"/>`;
    s += `<line x1="${TL.pad.l}" y1="${ubY}" x2="${TL.W - TL.pad.r}" y2="${ubY}" stroke="var(--ink)" stroke-width="0.5" opacity="0.18"/>`;
    // Center axis (mirror)
    s += `<line x1="${TL.pad.l}" y1="${axisY}" x2="${TL.W - TL.pad.r}" y2="${axisY}" stroke="var(--ink)" stroke-width="0.6" opacity="0.42"/>`;

    // Lane labels (in-chart, larger, no excessive tracking)
    s += `<text x="${TL.pad.l + 6}" y="${TL.pad.t + 18}" font-family="JetBrains Mono" font-size="11" font-weight="600" fill="var(--bl)" letter-spacing="0.04em">FREEZE ↑</text>`;
    s += `<text x="${TL.pad.l + 6}" y="${TL.H - TL.pad.b - 8}" font-family="JetBrains Mono" font-size="11" font-weight="600" fill="var(--ub)" letter-spacing="0.04em">UNFREEZE ↓</text>`;

    // Bubbles
    const maxN = Math.max(...State.clusters.map(c => c.count));
    const rOf = (n) => 4 + Math.sqrt(n / maxN) * 36;
    const sorted = [...State.clusters].sort((a, b) => b.count - a.count);
    for (const c of sorted) {
      const x = xs(c.ts);
      const y = c.mech === 'BLACKLIST' ? blY : ubY;
      const r = rOf(c.count);
      const isUnattr = c.category === 'untriggered';
      const ringMode = !document.body.classList.contains('solid-unattributed');
      const stroke = (isUnattr && ringMode) ? cssVar('--na') : 'var(--panel)';
      const fill = (isUnattr && ringMode) ? 'transparent' : (isUnattr ? cssVar('--na') : (c.mech === 'BLACKLIST' ? cssVar('--bl') : cssVar('--ub')));
      const inWin = inFilter(c) && inWindow(c);
      const visClass = inWin ? '' : (inFilter(c) ? 'dim' : 'hidden');
      const pinClass = c.id === State.pinnedId ? 'pinned' : '';
      const sw = (isUnattr && ringMode) ? 1.6 : 1;
      const fop = isUnattr && ringMode ? 1 : (isUnattr ? 0.7 : 0.85);
      s += `<circle class="tl-bubble ${visClass} ${pinClass}" data-cid="${c.id}" cx="${x.toFixed(1)}" cy="${y}" r="${r.toFixed(1)}" fill="${fill}" fill-opacity="${fop}" stroke="${stroke}" stroke-width="${sw}"/>`;
    }

    // Annotations — only render those inside the current x-window
    for (const a of ANNOTATIONS) {
      const ts = new Date(a.date + 'T00:00:00Z').getTime();
      if (ts < xMin || ts > xMax) continue;
      const x = xs(ts);
      const y = a.mech === 'BLACKLIST' ? blY : ubY;
      const labY = a.side === 'top' ? TL.pad.t + 14 : TL.H - TL.pad.b - 22;
      const lineY1 = a.side === 'top' ? labY + 6 : labY - 8;
      const lineY2 = a.side === 'top' ? y - rOf(maxN * 0.4) : y + rOf(maxN * 0.4);
      const subY = a.side === 'top' ? labY + 12 : labY + 12;
      // Place label slightly to the side to avoid overlap with the bubble itself
      const labX = x;
      s += `<g class="tl-annotation">`;
      s += `<line class="tl-anno-line" x1="${labX}" y1="${lineY1}" x2="${labX}" y2="${lineY2}"/>`;
      s += `<text class="tl-anno-label" x="${labX}" y="${labY}" text-anchor="middle"><tspan class="bold">${a.label}</tspan></text>`;
      s += `<text class="tl-anno-label" x="${labX}" y="${subY}" text-anchor="middle" opacity="0.75">${a.sub}</text>`;
      s += `</g>`;
    }

    svg.innerHTML = s;
    updatePinHalo();

    $$('.tl-bubble', svg).forEach(el => {
      el.addEventListener('mouseenter', e => {
        const id = el.dataset.cid;
        State.activeId = id;
        showTooltip(e, id);
        showDetail(id);
        el.classList.add('active');
      });
      el.addEventListener('mousemove', moveTooltip);
      el.addEventListener('mouseleave', () => {
        hideTooltip();
        el.classList.remove('active');
        showDetail(State.pinnedId);
      });
      el.addEventListener('click', () => {
        const id = el.dataset.cid;
        if (State.pinnedId === id) {
          State.pinnedId = null;
          el.classList.remove('pinned');
          showDetail(null);
        } else {
          if (State.pinnedId) {
            const prev = bubbleEl(State.pinnedId);
            if (prev) prev.classList.remove('pinned');
          }
          State.pinnedId = id;
          el.classList.add('pinned');
          showDetail(id);
        }
        updatePinHalo();
      });
    });
  }

  function showDetail(id) {
    const card = $('#detail');
    if (!id) {
      card.classList.add('empty');
      card.classList.remove('unbl');
      card.innerHTML = `
        <div class="dc-head">
          <span class="dc-date">—</span>
          <span class="dc-tag muted">SELECT A BUBBLE</span>
        </div>
        <div class="dc-body"></div>
      `;
      return;
    }
    const c = State.clusters.find(x => x.id === id);
    if (!c) return;
    card.classList.remove('empty');
    card.classList.toggle('unbl', c.mech === 'UNBLACKLIST');
    const tagClass = c.mech === 'UNBLACKLIST' ? 'dc-tag unbl' : (c.category === 'untriggered' ? 'dc-tag muted' : 'dc-tag');
    const tagText = c.mech === 'UNBLACKLIST' ? 'UNFREEZE' : 'FREEZE';
    const reason = c.triggerDesc || 'No public trigger has been linked to this cluster. The action is recorded on‑chain but the rationale has not appeared in any public source we monitor.';
    const attrPct = c.count > 0 ? Math.round((c.attributed / c.count) * 100) : 0;
    const isPinned = id === State.pinnedId;
    card.innerHTML = `
      <div class="dc-head">
        <span class="dc-date">${fmtDate(c.date)}</span>
        <span class="${tagClass}">${tagText}</span>
        <span class="dc-tag muted">${CAT_LABEL[c.category]}</span>
        ${isPinned ? '<span class="dc-tag pinned" title="Click the bubble again to unpin">📌 PINNED</span>' : ''}
      </div>
      <div class="dc-count-cell">
        <div class="dc-count-num">${c.count}</div>
        <div class="dc-count-lbl">Wallets</div>
        <div class="dc-count-attr">${c.attributed} attributed · ${attrPct}%</div>
      </div>
      <div class="dc-body">
        <div class="trigger-desc">${escapeHtml(reason)}</div>
      </div>
      <div class="dc-meta">
        <span><b>Cluster</b> ${c.id}</span>
        ${c.triggerId ? `<span><b>Trigger</b> ${c.triggerId}</span>` : ''}
        ${c.triggerType ? `<span><b>Type</b> ${c.triggerType.replace(/_/g, ' ')}</span>` : ''}
      </div>
    `;
  }
  function escapeHtml(s) { return String(s).replace(/[&<>"']/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m])); }

  const tooltip = $('#tooltip');
  function showTooltip(e, id) {
    const c = State.clusters.find(x => x.id === id);
    if (!c) return;
    tooltip.innerHTML = `
      <span class="tt-line">${fmtDate(c.date)} · ${c.mech === 'BLACKLIST' ? 'FREEZE' : 'UNFREEZE'}</span>
      <span class="tt-line tt-faint">${c.count} wallets · ${CAT_LABEL[c.category]}</span>
    `;
    tooltip.classList.add('show');
    moveTooltip(e);
  }
  function moveTooltip(e) {
    const pad = 14;
    const r = tooltip.getBoundingClientRect();
    let x = e.clientX + pad;
    let y = e.clientY - r.height - pad;
    if (x + r.width > window.innerWidth - 8) x = e.clientX - r.width - pad;
    if (y < 8) y = e.clientY + pad;
    tooltip.style.left = x + 'px';
    tooltip.style.top = y + 'px';
  }
  function hideTooltip() { tooltip.classList.remove('show'); }

  // --- Brush ---
  const BR = { W: 1600, H: 64, pad: { l: 64, r: 28, t: 8, b: 16 } };
  function drawBrush() {
    const svg = $('#brush');
    svg.innerHTML = '';
    const innerW = BR.W - BR.pad.l - BR.pad.r;
    const xMin = State.timeFullMin, xMax = State.timeFullMax;
    const xs = (ts) => BR.pad.l + ((ts - xMin) / (xMax - xMin)) * innerW;

    const months = new Map();
    for (const c of State.clusters) {
      const m = c.date.slice(0, 7);
      if (!months.has(m)) months.set(m, { bl: 0, ub: 0, ts: new Date(m + '-15T00:00:00Z').getTime() });
      const o = months.get(m);
      if (c.mech === 'BLACKLIST') o.bl += c.count; else o.ub += c.count;
    }
    const arr = Array.from(months.values()).sort((a, b) => a.ts - b.ts);
    const max = Math.max(...arr.map(m => m.bl + m.ub), 1);
    const barH = BR.H - BR.pad.t - BR.pad.b;
    // Bar width = full month slot in pixels (so all months tile without gap), capped to one twelfth of the year span
    const monthMs = (xMax - xMin) / 12 / ((xMax - xMin) / (1000 * 60 * 60 * 24 * 365.25));
    const pxPerMonth = (innerW / ((xMax - xMin) / (1000 * 60 * 60 * 24 * 30.4375)));
    const barW = Math.max(1, pxPerMonth - 0.5);

    let s = '';
    s += `<rect x="${BR.pad.l}" y="${BR.pad.t}" width="${innerW}" height="${barH}" fill="var(--line-soft)" fill-opacity="0.5"/>`;
    const xRight = BR.pad.l + innerW;
    for (const m of arr) {
      const x = xs(m.ts);
      const tot = m.bl + m.ub;
      const h = (tot / max) * barH;
      let bx = x - barW / 2;
      let bw = barW;
      // Clamp to the inner rect so bars never extend beyond the brush band
      if (bx < BR.pad.l) { bw -= (BR.pad.l - bx); bx = BR.pad.l; }
      if (bx + bw > xRight) { bw = xRight - bx; }
      if (bw <= 0) continue;
      s += `<rect x="${bx.toFixed(1)}" y="${(BR.pad.t + barH - h).toFixed(1)}" width="${bw.toFixed(1)}" height="${h.toFixed(1)}" fill="var(--ink-soft)" fill-opacity="0.7"/>`;
    }

    const wx1 = xs(State.timeMin), wx2 = xs(State.timeMax);
    s += `<rect x="${BR.pad.l}" y="${BR.pad.t}" width="${(wx1 - BR.pad.l).toFixed(1)}" height="${barH}" fill="var(--bg)" fill-opacity="0.65"/>`;
    s += `<rect x="${wx2.toFixed(1)}" y="${BR.pad.t}" width="${(BR.pad.l + innerW - wx2).toFixed(1)}" height="${barH}" fill="var(--bg)" fill-opacity="0.65"/>`;
    s += `<rect class="brush-window" id="brush-window" x="${wx1.toFixed(1)}" y="${BR.pad.t}" width="${(wx2 - wx1).toFixed(1)}" height="${barH}"/>`;
    // Visible thicker handles
    const handleW = 5;
    s += `<rect class="brush-handle" id="brush-h-l" x="${(wx1 - handleW/2).toFixed(1)}" y="${BR.pad.t - 2}" width="${handleW}" height="${barH + 4}" rx="1.5"/>`;
    s += `<rect class="brush-handle" id="brush-h-r" x="${(wx2 - handleW/2).toFixed(1)}" y="${BR.pad.t - 2}" width="${handleW}" height="${barH + 4}" rx="1.5"/>`;
    // Handle grip lines
    for (const hx of [wx1, wx2]) {
      s += `<line x1="${(hx - 1).toFixed(1)}" y1="${BR.pad.t + barH/2 - 4}" x2="${(hx - 1).toFixed(1)}" y2="${BR.pad.t + barH/2 + 4}" stroke="var(--bg)" stroke-width="0.7" pointer-events="none"/>`;
      s += `<line x1="${(hx + 1).toFixed(1)}" y1="${BR.pad.t + barH/2 - 4}" x2="${(hx + 1).toFixed(1)}" y2="${BR.pad.t + barH/2 + 4}" stroke="var(--bg)" stroke-width="0.7" pointer-events="none"/>`;
    }

    const startY = new Date(xMin).getUTCFullYear();
    const endY = new Date(xMax).getUTCFullYear();
    for (let y = startY; y <= endY + 1; y++) {
      const ts = Date.UTC(y, 0, 1);
      if (ts < xMin || ts > xMax) continue;
      const x = xs(ts);
      s += `<text x="${x.toFixed(1)}" y="${BR.H - 2}" text-anchor="middle" font-family="JetBrains Mono" font-size="9.5" fill="var(--ink-faint)">${y}</text>`;
    }
    svg.innerHTML = s;
    bindBrush();
  }

  function bindBrush() {
    const svg = $('#brush');
    const xMin = State.timeFullMin, xMax = State.timeFullMax;
    const innerW = BR.W - BR.pad.l - BR.pad.r;
    const tsAt = (clientX) => {
      const r = svg.getBoundingClientRect();
      const px = (clientX - r.left) * (BR.W / r.width);
      const u = Math.max(0, Math.min(1, (px - BR.pad.l) / innerW));
      return xMin + u * (xMax - xMin);
    };

    let mode = null, startX = 0, startMin = 0, startMax = 0;
    const onDown = (m) => (e) => {
      mode = m;
      startX = e.clientX;
      startMin = State.timeMin;
      startMax = State.timeMax;
      document.body.style.userSelect = 'none';
      e.preventDefault();
      e.stopPropagation();
    };
    $('#brush-window').addEventListener('mousedown', onDown('move'));
    $('#brush-h-l').addEventListener('mousedown', onDown('left'));
    $('#brush-h-r').addEventListener('mousedown', onDown('right'));
    svg.addEventListener('mousedown', (e) => {
      if (mode) return;
      if (e.target.id === 'brush-window' || e.target.classList.contains('brush-handle')) return;
      const ts = tsAt(e.clientX);
      const half = (State.timeMax - State.timeMin) / 2;
      State.timeMin = Math.max(xMin, ts - half);
      State.timeMax = Math.min(xMax, ts + half);
      updateAll();
    });

    document.addEventListener('mousemove', (e) => {
      if (!mode) return;
      const r = svg.getBoundingClientRect();
      const dxPx = (e.clientX - startX) * (BR.W / r.width);
      const dxTs = (dxPx / innerW) * (xMax - xMin);
      if (mode === 'move') {
        let nMin = startMin + dxTs;
        let nMax = startMax + dxTs;
        if (nMin < xMin) { nMax += (xMin - nMin); nMin = xMin; }
        if (nMax > xMax) { nMin -= (nMax - xMax); nMax = xMax; }
        State.timeMin = nMin; State.timeMax = nMax;
      } else if (mode === 'left') {
        State.timeMin = Math.max(xMin, Math.min(startMax - 14 * 86400000, startMin + dxTs));
      } else if (mode === 'right') {
        State.timeMax = Math.min(xMax, Math.max(startMin + 14 * 86400000, startMax + dxTs));
      }
      updateAll();
    });
    document.addEventListener('mouseup', () => { mode = null; document.body.style.userSelect = ''; });
  }

  // --- Filter chips (multi-select)
  function bindFilters() {
    // "All" toggle button — turns everything on, or clears down to nothing
    const showingBtn = $('#showing-btn');
    if (showingBtn) {
      showingBtn.addEventListener('click', () => {
        const all = ['ofac', 'court', 'hack', 'untriggered'];
        const allOn = all.every(c => State.activeCats.has(c));
        if (allOn) {
          // Already all on — leave on but treat as "reset" of any single-focus state
          State.activeCats = new Set(all);
        } else {
          State.activeCats = new Set(all);
        }
        syncChipState();
        updateAll();
      });
    }
    $$('#controls .filter-group .chip:not(.showing-btn)').forEach(chip => {
      chip.addEventListener('click', () => {
        const cat = chip.dataset.value;
        if (State.activeCats.has(cat)) {
          if (State.activeCats.size === 1) {
            // Toggling off the only active → turn ALL on (cleared filter)
            State.activeCats = new Set(['ofac', 'court', 'hack', 'untriggered']);
          } else {
            State.activeCats.delete(cat);
          }
        } else {
          State.activeCats.add(cat);
        }
        syncChipState();
        updateAll();
      });
    });
    $('#reset-btn').addEventListener('click', () => {
      State.activeCats = new Set(['ofac', 'court', 'hack', 'untriggered']);
      State.timeMin = State.timeFullMin;
      State.timeMax = State.timeFullMax;
      State.pinnedId = null;
      syncChipState();
      updateAll();
      showDetail(null);
    });
    // Theme toggle
    $$('.theme-toggle button').forEach(b => {
      b.addEventListener('click', () => {
        const dark = b.dataset.theme === 'dark';
        document.body.classList.toggle('dark', dark);
        $$('.theme-toggle button').forEach(x => x.classList.toggle('active', x === b));
        // Persist via tweak protocol if available
        window.parent.postMessage({type: '__edit_mode_set_keys', edits: {dark}}, '*');
        setTimeout(updateAll, 30);
      });
    });
  }
  function syncChipState() {
    $$('#controls [data-filter="category"] .chip:not(.showing-btn)').forEach(c => {
      c.setAttribute('aria-pressed', State.activeCats.has(c.dataset.value) ? 'true' : 'false');
    });
    const all = ['ofac', 'court', 'hack', 'untriggered'];
    const allOn = all.every(c => State.activeCats.has(c));
    const btn = $('#showing-btn');
    if (btn) btn.setAttribute('aria-pressed', allOn ? 'true' : 'false');
  }
  function updateChipCounts() {
    const cats = ['ofac', 'court', 'hack', 'untriggered'];
    const inWin = State.clusters.filter(inWindow);
    cats.forEach(cat => {
      const el = document.querySelector(`[data-filter="category"] [data-value="${cat}"] .chip-count`);
      if (el) el.textContent = inWin.filter(c => c.category === cat).length;
    });
  }

  // --- Donut + breakdown
  function renderDonut() {
    if (!$('#donut')) return;
    const vis = visibleClusters();
    const cats = ['ofac', 'untriggered', 'court', 'hack'];
    const counts = cats.map(c => vis.filter(x => x.category === c).length);
    const total = counts.reduce((a, b) => a + b, 0) || 1;
    const colors = { ofac: cssVar('--bl'), untriggered: cssVar('--na'), court: cssVar('--court'), hack: cssVar('--hack') };

    const cx = 50, cy = 50, R = 38, r = 26;
    let acc = 0;
    let s = '';
    for (let i = 0; i < cats.length; i++) {
      if (counts[i] === 0) continue;
      const frac = counts[i] / total;
      const a0 = acc * 2 * Math.PI - Math.PI / 2;
      const a1 = (acc + frac) * 2 * Math.PI - Math.PI / 2;
      acc += frac;
      const large = frac > 0.5 ? 1 : 0;
      const x0o = cx + R * Math.cos(a0), y0o = cy + R * Math.sin(a0);
      const x1o = cx + R * Math.cos(a1), y1o = cy + R * Math.sin(a1);
      const x0i = cx + r * Math.cos(a1), y0i = cy + r * Math.sin(a1);
      const x1i = cx + r * Math.cos(a0), y1i = cy + r * Math.sin(a0);
      const path = `M ${x0o} ${y0o} A ${R} ${R} 0 ${large} 1 ${x1o} ${y1o} L ${x0i} ${y0i} A ${r} ${r} 0 ${large} 0 ${x1i} ${y1i} Z`;
      const isUnattr = cats[i] === 'untriggered';
      const fillAttrs = isUnattr ? `fill="transparent" stroke="${colors.untriggered}" stroke-width="1.4"` : `fill="${colors[cats[i]]}"`;
      s += `<path d="${path}" ${fillAttrs} data-cat="${cats[i]}" style="cursor:pointer;transition:opacity 100ms" />`;
    }
    s += `<text x="${cx}" y="${cy - 1}" text-anchor="middle" font-family="Source Serif 4" font-size="15" font-weight="500" fill="var(--ink)">${vis.length}</text>`;
    s += `<text x="${cx}" y="${cy + 9}" text-anchor="middle" font-family="JetBrains Mono" font-size="5" fill="var(--ink-faint)" letter-spacing="0.1em">CLUSTERS</text>`;
    $('#donut').innerHTML = s;

    const list = $('#donut-list');
    list.innerHTML = cats.map((c, i) => {
      const swClass = c === 'untriggered' ? 'dr-swatch ring' : 'dr-swatch';
      const swStyle = c === 'untriggered' ? '' : `style="background:${colors[c]}"`;
      return `
      <div class="donut-row" data-cat="${c}">
        <span class="${swClass}" ${swStyle}></span>
        <span class="dr-label">${CAT_LABEL[c]}</span>
        <span class="dr-val">${counts[i]}<span style="opacity:0.5"> · ${Math.round(counts[i] / total * 100)}%</span></span>
      </div>
    `;}).join('');

    list.querySelectorAll('.donut-row').forEach(row => {
      row.addEventListener('mouseenter', () => highlightCategory(row.dataset.cat));
      row.addEventListener('mouseleave', () => highlightCategory(null));
      row.addEventListener('click', () => {
        const cat = row.dataset.cat;
        // Toggle: focus this category alone (or restore all)
        if (State.activeCats.size === 1 && State.activeCats.has(cat)) {
          State.activeCats = new Set(['ofac', 'court', 'hack', 'untriggered']);
        } else {
          State.activeCats = new Set([cat]);
        }
        syncChipState();
        updateAll();
      });
    });
    $('#donut').querySelectorAll('path').forEach(p => {
      p.addEventListener('mouseenter', () => highlightCategory(p.dataset.cat));
      p.addEventListener('mouseleave', () => highlightCategory(null));
    });
  }
  function highlightCategory(cat) {
    if (!cat) {
      State.clusters.forEach(c => bubbleEl(c.id) && bubbleEl(c.id).classList.remove('dim'));
      return;
    }
    State.clusters.forEach(c => {
      const el = bubbleEl(c.id); if (!el) return;
      if (c.category === cat) el.classList.remove('dim'); else el.classList.add('dim');
    });
  }

  // --- Top events list
  function renderTop() {
    if (!$('#top-list')) return;
    const vis = visibleClusters();
    const top = [...vis].sort((a, b) => b.count - a.count).slice(0, 6);
    if (!top.length) {
      $('#top-list').innerHTML = `<div class="top-row"><span class="tr-bar"></span><span class="tr-text"><div class="tr-desc" style="color:var(--ink-faint);font-style:italic">No clusters in current view</div></span><span class="tr-count">—</span></div>`;
      return;
    }
    $('#top-list').innerHTML = top.map(c => {
      const barClass = c.mech === 'UNBLACKLIST' ? 'unbl' : (c.category === 'untriggered' ? 'na' : '');
      const desc = c.triggerDesc || `${c.mech === 'BLACKLIST' ? 'Freeze' : 'Unfreeze'} cluster, no public trigger`;
      return `<div class="top-row" data-cid="${c.id}">
        <span class="tr-bar ${barClass}"></span>
        <span class="tr-text">
          <div class="tr-date">${fmtDate(c.date)}</div>
          <div class="tr-desc">${escapeHtml(desc.slice(0, 64))}${desc.length > 64 ? '…' : ''}</div>
        </span>
        <span class="tr-count">${c.count}<small>×</small></span>
      </div>`;
    }).join('');
    $('#top-list').querySelectorAll('.top-row').forEach(row => {
      const id = row.dataset.cid;
      row.addEventListener('mouseenter', () => {
        const el = bubbleEl(id); if (el) el.classList.add('active');
        showDetail(id);
      });
      row.addEventListener('mouseleave', () => {
        const el = bubbleEl(id); if (el) el.classList.remove('active');
        showDetail(State.pinnedId);
      });
      row.addEventListener('click', () => {
        if (State.pinnedId === id) {
          State.pinnedId = null;
          const b = bubbleEl(id); if (b) b.classList.remove('pinned');
          showDetail(null);
        } else {
          if (State.pinnedId) {
            const prev = bubbleEl(State.pinnedId);
            if (prev) prev.classList.remove('pinned');
          }
          State.pinnedId = id;
          const b = bubbleEl(id); if (b) b.classList.add('pinned');
          showDetail(id);
        }
        updatePinHalo();
      });
    });
  }

  // --- Year bars
  function renderYearBars() {
    if (!$('#year-bars')) return;
    const years = {};
    for (const c of State.clusters) {
      const y = c.date.slice(0, 4);
      if (!years[y]) years[y] = { ofac: 0, court: 0, hack: 0, untriggered: 0, total: 0 };
      years[y][c.category] = (years[y][c.category] || 0) + c.count;
      years[y].total += c.count;
    }
    const yk = Object.keys(years).sort();
    const max = Math.max(...yk.map(y => years[y].total));
    const colors = { ofac: cssVar('--bl'), court: cssVar('--court'), hack: cssVar('--hack'), untriggered: cssVar('--na') };
    $('#year-bars').innerHTML = yk.map(y => {
      const data = years[y];
      const totH = (data.total / max) * 100;
      const segs = ['ofac', 'court', 'hack', 'untriggered'].map(cat => {
        if (!data[cat]) return '';
        const h = (data[cat] / data.total) * totH;
        return `<span class="yb-seg ${cat === 'untriggered' ? 'na' : (cat === 'ofac' ? '' : cat)}" style="background:${colors[cat]};height:${h.toFixed(2)}%"></span>`;
      }).join('');
      return `<div class="year-bar" title="${y}: ${data.total} wallets">
        <span class="yb-tot">${data.total >= 1000 ? (data.total / 1000).toFixed(1) + 'k' : data.total}</span>
        <div class="yb-stack">${segs}</div>
        <span class="yb-label">'${y.slice(2)}</span>
      </div>`;
    }).join('');
  }

  // --- Master update
  function updateAll() {
    drawTimeline();
    drawBrush();
    renderKPIs();
    renderDonut();
    renderTop();
    renderYearBars();
    updateChipCounts();
    showDetail(State.pinnedId);
  }

  // Init
  load().then(() => {
    bindFilters();
    syncChipState();
    updateAll();
    window.__dashState = State;
  });

  // Expose for tweaks
  window.__dashboard = {
    setDark(on) {
      document.body.classList.toggle('dark', !!on);
      $$('.theme-toggle button').forEach(b => b.classList.toggle('active', (b.dataset.theme === 'dark') === !!on));
      setTimeout(updateAll, 30);
    },
  };
})();
