// Dot-plot results charts (Tables II and III of the paper).
// Each row: [object, unseen?, axisOrientation, axisDisplacement, jointState]
// Each metric: { p: PokeNet, g: GAPartNet, s: ScrewNet } as [mean, 95% CI half-width]; null = not predicted/reported.

(function () {
  const SERIES = [
    { key: 's', name: 'ScrewNet', color: '#0f98a8', r: 4.5 },
    { key: 'g', name: 'GAPartNet', color: '#d9674a', r: 4.5 },
    { key: 'p', name: 'PokeNet (ours)', color: '#4b4fc4', r: 6 },
  ];
  const METRICS = [
    { title: 'Axis orientation error', unit: '°' },
    { title: 'Axis displacement error', unit: 'cm' },
    { title: 'Joint state error', unit: 'deg / cm' },
  ];
  const m = (p, g, s) => ({ p, g, s });

  const REAL = [
    ['Microwave', false, m([13.88, 0.96], [18.62, 1.12], [28.42, 1.36]), m([11.42, 1.24], [12.77, 1.31], [17.58, 1.22]), m([13.15, 1.12], null, [29.11, 1.09])],
    ['Fridge', false, m([16.97, 1.05], [21.41, 1.46], [30.97, 1.07]), m([16.34, 1.27], [20.82, 0.98], [31.66, 1.38]), m([12.59, 1.16], null, [27.54, 1.41])],
    ['Drawer', false, m([17.62, 1.39], [22.88, 0.91], [35.33, 1.28]), m([13.04, 1.18], [18.41, 1.32], [33.85, 1.11]), m([12.71, 1.08], null, [25.62, 0.94])],
    ['Dishwasher', false, m([20.44, 1.12], [23.73, 1.18], [30.84, 0.99]), m([21.72, 1.05], [26.28, 1.45], [28.87, 1.42]), m([20.06, 1.30], null, [32.18, 1.22])],
    ['Slider knife', true, m([14.18, 3.25], [58.64, 4.09], [28.22, 3.43]), m([6.38, 4.14], [9.42, 3.82], [17.47, 3.18]), null],
    ['Stapler', true, m([16.26, 4.98], [19.17, 5.15], [36.81, 4.32]), m([8.19, 3.36], [13.04, 3.92], [16.34, 3.41]), null],
  ];

  const SIM = [
    ['Microwave', false, m([7.26, 1.08], [9.71, 1.12], [21.13, 1.07]), m([5.26, 0.97], [6.37, 1.21], [14.28, 1.03]), m([9.31, 1.09], null, [18.47, 0.96])],
    ['Washing machine', false, m([7.48, 1.01], [10.57, 1.33], [21.78, 0.88]), m([6.23, 1.15], [7.92, 1.08], [11.64, 1.22]), m([7.11, 1.34], null, [21.36, 1.27])],
    ['Laptop', false, m([6.14, 1.23], [7.28, 0.95], [22.69, 1.14]), m([4.68, 1.07], [5.72, 1.44], [12.37, 0.91]), m([8.21, 1.07], null, [17.42, 1.38])],
    ['Fridge', false, m([8.92, 0.97], [11.74, 1.18], [26.87, 1.25]), m([6.77, 1.31], [8.83, 0.86], [13.58, 1.09]), m([9.48, 0.91], null, [24.21, 1.11])],
    ['Drawer', false, m([7.36, 1.14], [10.07, 1.09], [23.58, 0.93]), m([4.59, 0.88], [6.77, 1.12], [10.96, 1.36]), m([6.91, 1.12], null, [20.66, 0.84])],
    ['Trashcan', false, m([8.51, 1.08], [9.34, 0.86], [24.72, 1.31]), m([4.92, 1.13], [7.37, 1.27], [14.61, 0.99]), m([10.03, 1.36], null, [19.18, 1.43])],
    ['Window', false, m([7.16, 0.89], [9.39, 1.24], [20.93, 1.17]), m([5.73, 1.41], [6.58, 1.14], [12.83, 1.02]), m([6.88, 1.05], null, [21.57, 0.98])],
    ['Door', false, m([9.03, 1.12], [9.88, 1.43], [24.05, 1.08]), m([5.06, 1.33], [8.11, 0.92], [13.47, 1.20]), m([7.95, 1.14], null, [23.62, 1.26])],
    ['Fan', false, m([7.84, 0.95], [9.93, 1.02], [22.41, 0.99]), m([4.51, 1.07], [7.68, 1.34], [11.72, 1.28]), m([6.59, 1.18], null, [20.84, 1.21])],
    ['Scissors', false, m([6.12, 1.06], [8.85, 1.20], [21.62, 1.34]), m([5.87, 0.82], [8.21, 1.25], [10.73, 0.90]), m([8.36, 1.06], null, [24.39, 1.32])],
    ['Bucket', false, m([8.21, 0.96], [10.66, 1.26], [20.74, 0.92]), m([4.38, 1.22], [6.97, 1.10], [12.42, 1.35]), m([7.44, 1.03], null, [22.53, 1.09])],
    ['Plier', true, m([8.14, 1.23], [10.63, 1.08], [27.84, 1.19]), m([6.58, 1.29], [6.94, 1.12], [13.66, 0.88]), m([11.37, 0.99], null, [19.47, 1.31])],
    ['Toilet', true, m([8.52, 1.01], [12.08, 0.96], [29.31, 1.15]), m([5.23, 0.93], [7.76, 1.18], [14.12, 1.33]), m([9.97, 1.09], null, [21.66, 0.97])],
    ['Furniture', true, m([13.15, 0.90], [17.24, 1.11], [26.47, 1.28]), m([5.87, 1.36], [8.62, 0.91], [11.95, 1.07]), m([10.94, 1.27], null, [25.88, 1.44])],
    ['Box', true, m([11.42, 1.07], [19.37, 1.36], [25.72, 0.91]), m([5.11, 0.95], [7.23, 1.06], [12.31, 1.24]), m([13.82, 1.38], null, [26.18, 0.84])],
  ];
  // simulation rows: order each group by PokeNet axis-orientation error
  const byOurs = (a, b) => (a[1] - b[1]) || (a[2].p[0] - b[2].p[0]);
  SIM.sort(byOurs);

  const NS = 'http://www.w3.org/2000/svg';
  const C = { ink: '#1d1f2b', muted: '#5d6072', grid: '#ece6dc', track: '#e4ded3', band: '#f6f3ee', surface: '#ffffff' };

  function el(tag, attrs, parent, text) {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    if (text != null) e.textContent = text;
    if (parent) parent.appendChild(e);
    return e;
  }

  function niceScale(max) {
    const raw = max / 5;
    const mag = Math.pow(10, Math.floor(Math.log10(raw)));
    const step = [1, 2, 2.5, 5, 10].map(f => f * mag).find(s => s >= raw);
    return { step, max: Math.ceil(max / step) * step };
  }

  const fmt = v => v.toFixed(1);

  // rows -> layout with group gaps
  function layout(rows) {
    const ROW = 38, GAP = 26;
    let y = 0, prev = null;
    const out = [], groups = [];
    rows.forEach((r, i) => {
      if (r[1] !== prev) {
        y += (i === 0 ? 22 : GAP);
        groups.push({ unseen: r[1], y0: y - 18, start: out.length });
        prev = r[1];
      }
      out.push({ row: r, y: y + ROW / 2 + 4 });
      y += ROW;
      groups[groups.length - 1].y1 = y;
    });
    return { rows: out, groups, height: y };
  }

  function drawPanel(host, rows, mi, width, labelW, tip) {
    const L = layout(rows);
    const top = 44, plotL = labelW + 8, plotR = width - 14;
    const axisY = top + L.height + 8;
    const H = axisY + 30;
    const svg = el('svg', { width, height: H, viewBox: `0 0 ${width} ${H}`, role: 'img',
      'aria-label': `${METRICS[mi].title} (${METRICS[mi].unit}), lower is better` }, host);

    // scale
    let maxV = 0;
    rows.forEach(r => { const d = r[2 + mi]; if (d) SERIES.forEach(s => { if (d[s.key]) maxV = Math.max(maxV, d[s.key][0] + d[s.key][1]); }); });
    const sc = niceScale(maxV);
    const x = v => plotL + (v / sc.max) * (plotR - plotL);

    // title
    el('text', { x: plotL, y: 18, 'font-size': 14.5, 'font-weight': 600, fill: C.ink }, svg, METRICS[mi].title + ' ');
    const t = svg.lastChild;
    el('tspan', { fill: C.muted, 'font-weight': 400 }, t, `(${METRICS[mi].unit})`);
    el('text', { x: plotR, y: 36, 'font-size': 11.5, fill: C.muted, 'text-anchor': 'end' }, svg, 'lower is better');

    // unseen band + group headers
    L.groups.forEach(g => {
      if (g.unseen) el('rect', { x: 0, y: top + g.y0 - 4, width, height: g.y1 - g.y0 + 8, fill: C.band, rx: 6 }, svg);
      if (labelW > 0) el('text', { x: 4, y: top + g.y0 + 6, 'font-size': 10.5, 'font-weight': 700, 'letter-spacing': '0.08em',
        fill: g.unseen ? '#b4543a' : C.muted }, svg, g.unseen ? 'UNSEEN CATEGORIES' : 'TRAINING CATEGORIES');
    });

    // grid + axis
    for (let v = 0; v <= sc.max + 1e-9; v += sc.step) {
      el('line', { x1: x(v), x2: x(v), y1: top + 4, y2: axisY, stroke: C.grid, 'stroke-width': 1 }, svg);
      el('text', { x: x(v), y: axisY + 18, 'font-size': 11.5, fill: C.muted, 'text-anchor': 'middle' }, svg,
        String(+v.toFixed(2)));
    }
    el('line', { x1: plotL, x2: plotR, y1: axisY, y2: axisY, stroke: '#cfc6b8', 'stroke-width': 1 }, svg);

    L.rows.forEach(({ row, y }) => {
      const cy = top + y;
      const d = row[2 + mi];
      if (labelW > 0) el('text', { x: labelW, y: cy + 4.5, 'font-size': 13.5, fill: C.ink, 'text-anchor': 'end',
        'font-weight': row[1] ? 600 : 400 }, svg, row[0]);
      if (!d) {
        el('text', { x: (plotL + plotR) / 2, y: cy + 4, 'font-size': 12, fill: C.muted, 'text-anchor': 'middle' }, svg, 'not reported');
        return;
      }
      const present = SERIES.filter(s => d[s.key]);
      const means = present.map(s => d[s.key][0]);
      el('line', { x1: x(Math.min(...means)), x2: x(Math.max(...means)), y1: cy, y2: cy, stroke: C.track,
        'stroke-width': 2, 'stroke-linecap': 'round' }, svg);
      present.forEach(s => {
        const [mu, ci] = d[s.key];
        el('rect', { x: x(mu - ci), y: cy - 3, width: Math.max(2, x(mu + ci) - x(mu - ci)), height: 6, rx: 3,
          fill: s.color, 'fill-opacity': 0.25 }, svg);
      });
      present.forEach(s => {
        el('circle', { cx: x(d[s.key][0]), cy, r: s.r, fill: s.color, stroke: C.surface, 'stroke-width': 2 }, svg);
      });
      el('text', { x: x(d.p[0]), y: cy - 10, 'font-size': 11.5, 'font-weight': 600, fill: C.ink, 'text-anchor': 'middle' },
        svg, fmt(d.p[0]));

      // hit target: the whole row
      const hit = el('rect', { x: 0, y: cy - 19, width, height: 38, fill: 'transparent', tabindex: 0,
        'aria-label': `${row[0]}: ` + present.map(s => `${s.name} ${d[s.key][0]} ± ${d[s.key][1]}`).join(', ') }, svg);
      const show = ev => tip.show(ev, row[0], METRICS[mi], d, hit);
      hit.addEventListener('pointerenter', show);
      hit.addEventListener('pointermove', show);
      hit.addEventListener('focus', show);
      hit.addEventListener('pointerleave', tip.hide);
      hit.addEventListener('blur', tip.hide);
    });
  }

  function makeTip(card) {
    const box = document.createElement('div');
    box.className = 'dp-tip';
    box.hidden = true;
    card.appendChild(box);
    return {
      show(ev, name, metric, d, target) {
        box.replaceChildren();
        const h = document.createElement('div');
        h.className = 'dp-tip-h';
        h.textContent = `${name} · ${metric.title.replace(' error', '')}`;
        box.appendChild(h);
        [...SERIES].reverse().forEach(s => {
          if (!d[s.key]) return;
          const r = document.createElement('div');
          r.className = 'dp-tip-row';
          const k = document.createElement('i');
          k.style.background = s.color;
          const v = document.createElement('b');
          v.textContent = `${d[s.key][0].toFixed(2)} ± ${d[s.key][1].toFixed(2)}`;
          const n = document.createElement('span');
          n.textContent = s.name;
          r.append(k, v, n);
          box.appendChild(r);
        });
        box.hidden = false;
        const cr = card.getBoundingClientRect();
        let px, py;
        if (ev.clientX != null && ev.type !== 'focus') { px = ev.clientX - cr.left; py = ev.clientY - cr.top; }
        else { const tr = target.getBoundingClientRect(); px = tr.left - cr.left + tr.width / 2; py = tr.top - cr.top; }
        const bw = box.offsetWidth;
        box.style.left = Math.min(Math.max(8, px + 14), cr.width - bw - 8) + 'px';
        box.style.top = (py + 16) + 'px';
      },
      hide() { box.hidden = true; },
    };
  }

  function buildTable(details, rows) {
    const t = document.createElement('table');
    t.className = 'res';
    const head = t.createTHead().insertRow();
    ['Object', 'Metric', 'PokeNet (ours)', 'GAPartNet', 'ScrewNet'].forEach(h => {
      const th = document.createElement('th'); th.textContent = h; head.appendChild(th);
    });
    const body = t.createTBody();
    rows.forEach(r => METRICS.forEach((mt, mi) => {
      const d = r[2 + mi];
      const tr = body.insertRow();
      [mi === 0 ? r[0] + (r[1] ? ' (unseen)' : '') : '', `${mt.title} (${mt.unit})`]
        .concat(['p', 'g', 's'].map(k => (d && d[k]) ? `${d[k][0].toFixed(2)} ± ${d[k][1].toFixed(2)}` : '—'))
        .forEach(v => { tr.insertCell().textContent = v; });
    }));
    const wrap = document.createElement('div');
    wrap.className = 'table-scroll';
    wrap.appendChild(t);
    details.appendChild(wrap);
  }

  function mount(card, rows) {
    const host = card.querySelector('.dp-panels');
    const tip = makeTip(card);
    buildTable(card.querySelector('details.dp-table'), rows);
    let lastW = 0;
    function render() {
      const W = host.clientWidth;
      if (!W || W === lastW) return;
      lastW = W;
      host.replaceChildren();
      const wide = W >= 860;
      const labelW = wide ? 150 : 118;
      if (wide) {
        const pw = Math.floor((W - labelW - 2 * 18) / 3);
        METRICS.forEach((_, mi) => drawPanel(host, rows, mi, mi === 0 ? pw + labelW : pw, mi === 0 ? labelW : 0, tip));
      } else {
        METRICS.forEach((_, mi) => drawPanel(host, rows, mi, W, labelW, tip));
      }
      host.classList.toggle('wide', wide);
    }
    render();
    new ResizeObserver(render).observe(host);
  }

  mount(document.getElementById('chart-real'), REAL);
  mount(document.getElementById('chart-sim'), SIM);
})();
