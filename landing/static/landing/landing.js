/* Pajina públiku SJAMCI: menu, slider, mapa munisípiu, gráfiku. */
(function () {
  'use strict';
  const T = JSON.parse(document.getElementById('i18n').textContent);
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fmt = (n) => Number(n).toLocaleString(document.documentElement.lang === 'en' ? 'en-GB' : 'pt-PT');

  // ── Menu telemovel ───────────────────────────────────────
  const burger = document.querySelector('.burger');
  const menu = document.getElementById('menu');
  burger.addEventListener('click', () => {
    const open = menu.classList.toggle('open');
    burger.setAttribute('aria-expanded', String(open));
  });
  menu.addEventListener('click', (event) => {
    if (event.target.tagName === 'A') { menu.classList.remove('open'); burger.setAttribute('aria-expanded', 'false'); }
  });

  // ── Slider ───────────────────────────────────────────────
  const slides = Array.from(document.querySelectorAll('.slide'));
  const dots = Array.from(document.querySelectorAll('.dot'));
  const pauseButton = document.querySelector('[data-pause]');
  let current = 0, timer = null, paused = reduceMotion;
  function show(index) {
    current = (index + slides.length) % slides.length;
    slides.forEach((s, i) => { s.classList.toggle('on', i === current); s.setAttribute('aria-hidden', String(i !== current)); });
    dots.forEach((d, i) => d.classList.toggle('on', i === current));
  }
  function schedule() {
    clearInterval(timer);
    if (!paused && slides.length > 1) timer = setInterval(() => show(current + 1), 6500);
    if (pauseButton) {
      pauseButton.innerHTML = paused ? '&#9654;' : '&#10074;&#10074;';
      pauseButton.setAttribute('aria-label', paused ? T.slide_play : T.slide_pause);
    }
  }
  document.querySelectorAll('.sl-btn[data-dir]').forEach((b) => b.addEventListener('click', () => { show(current + Number(b.dataset.dir)); schedule(); }));
  dots.forEach((d) => d.addEventListener('click', () => { show(Number(d.dataset.go)); schedule(); }));
  if (pauseButton) pauseButton.addEventListener('click', () => { paused = !paused; schedule(); });
  const slider = document.querySelector('.slider');
  slider.addEventListener('mouseenter', () => clearInterval(timer));
  slider.addEventListener('mouseleave', schedule);
  slider.addEventListener('focusin', () => clearInterval(timer));
  slider.addEventListener('focusout', schedule);
  show(0); schedule();

  // ── Númeru anima ─────────────────────────────────────────
  if (!reduceMotion && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        observer.unobserve(entry.target);
        const end = Number(entry.target.dataset.count) || 0, start = performance.now();
        const tick = (now) => {
          const p = Math.min(1, (now - start) / 900);
          entry.target.textContent = fmt(Math.round(end * (1 - Math.pow(1 - p, 3))));
          if (p < 1) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
      });
    }, { threshold: 0.4 });
    document.querySelectorAll('.num[data-count]').forEach((el) => observer.observe(el));
  }

  // ── Mapa Timor-Leste ─────────────────────────────────────
  const mapBox = document.getElementById('map');
  const tbody = document.querySelector('#mun-table tbody');
  const message = document.getElementById('stats-msg');
  const SVG = 'http://www.w3.org/2000/svg';
  const paths = {};
  let tip = null, selected = null, latest = null;

  function shade(value, max) {
    if (!value) return '#eef1f5';
    const t = max ? Math.sqrt(value / max) : 0;          // eskala raiz: diferensa ki'ik mós haree
    const a = [219, 231, 246], b = [31, 56, 100];
    return 'rgb(' + a.map((c, i) => Math.round(c + (b[i] - c) * t)).join(',') + ')';
  }

  function buildMap(geo) {
    let minX = 180, maxX = -180, minY = 90, maxY = -90;
    const rings = (g) => (g.type === 'MultiPolygon' ? g.coordinates.flat() : g.coordinates);
    geo.features.forEach((f) => rings(f.geometry).forEach((ring) => ring.forEach(([x, y]) => {
      minX = Math.min(minX, x); maxX = Math.max(maxX, x); minY = Math.min(minY, y); maxY = Math.max(maxY, y);
    })));
    const W = 1000, pad = 12, scale = (W - 2 * pad) / (maxX - minX);
    const k = Math.cos(((minY + maxY) / 2) * Math.PI / 180);      // korrije latitude
    const H = Math.round((maxY - minY) * scale / k + 2 * pad);
    const svg = document.createElementNS(SVG, 'svg');
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    svg.setAttribute('role', 'group');
    geo.features.forEach((f) => {
      const d = rings(f.geometry).map((ring) => 'M' + ring.map(([x, y]) =>
        `${(pad + (x - minX) * scale).toFixed(1)},${(pad + (maxY - y) * scale / k).toFixed(1)}`).join('L') + 'Z').join('');
      const path = document.createElementNS(SVG, 'path');
      path.setAttribute('d', d);
      path.setAttribute('fill', '#eef1f5');
      path.setAttribute('tabindex', '0');
      path.setAttribute('role', 'button');
      path.dataset.iso = f.properties.iso;
      path.dataset.name = f.properties.name;
      svg.appendChild(path);
      paths[f.properties.iso] = path;
      path.addEventListener('mousemove', (e) => showTip(path, e));
      path.addEventListener('mouseleave', hideTip);
      path.addEventListener('focus', () => showTip(path));
      path.addEventListener('blur', hideTip);
      path.addEventListener('click', () => select(path.dataset.iso));
      path.addEventListener('keydown', (e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); select(path.dataset.iso); } });
    });
    mapBox.appendChild(svg);
    tip = document.createElement('div');
    tip.className = 'tip';
    tip.hidden = true;
    mapBox.appendChild(tip);
  }

  function showTip(path, event) {
    const box = mapBox.getBoundingClientRect();
    let x, y;
    if (event) { x = event.clientX - box.left; y = event.clientY - box.top; }
    else { const r = path.getBoundingClientRect(); x = r.left + r.width / 2 - box.left; y = r.top + r.height / 2 - box.top; }
    tip.innerHTML = '';
    tip.append(path.dataset.label || path.dataset.name, document.createElement('br'));
    const strong = document.createElement('b');
    strong.textContent = fmt(path.dataset.count || 0);
    tip.append(strong, ' ' + T.beneficiaries.toLowerCase());
    tip.style.left = Math.max(70, Math.min(box.width - 70, x)) + 'px';
    tip.style.top = Math.max(46, y) + 'px';
    tip.hidden = false;
  }
  function hideTip() { if (tip) tip.hidden = true; }

  function select(iso) {
    selected = selected === iso ? null : iso;
    Object.values(paths).forEach((p) => p.classList.toggle('sel', p.dataset.iso === selected));
    tbody.querySelectorAll('tr').forEach((tr) => tr.classList.toggle('sel', !!selected && tr.dataset.iso === selected));
    const row = selected && tbody.querySelector(`tr[data-iso="${selected}"]`);
    if (row) row.scrollIntoView({ block: 'nearest' });
  }

  function renderMunicipalities(data) {
    const max = Math.max(0, ...data.municipalities.map((m) => m.count));
    Object.values(paths).forEach((p) => {
      p.dataset.count = 0; p.dataset.label = p.dataset.name; p.setAttribute('fill', shade(0, max));
      p.setAttribute('aria-label', `${p.dataset.name}: 0`);
    });
    tbody.innerHTML = '';
    data.municipalities.forEach((m) => {
      const path = paths[m.iso];
      if (path) {
        path.dataset.count = m.count; path.dataset.label = m.name;
        path.setAttribute('fill', shade(m.count, max));
        path.setAttribute('aria-label', `${m.name}: ${m.count} ${T.beneficiaries}`);
      }
      const tr = document.createElement('tr');
      tr.dataset.iso = m.iso || '';
      const name = document.createElement('td');
      name.textContent = m.name;
      const bar = document.createElement('span');
      bar.className = 'bar';
      bar.style.width = (max ? Math.max(2, (m.count / max) * 100) : 0) + '%';
      name.appendChild(bar);
      const count = document.createElement('td');
      count.className = 'r';
      count.textContent = fmt(m.count);
      tr.append(name, count);
      if (m.iso) tr.addEventListener('click', () => select(m.iso));
      tbody.appendChild(tr);
    });
    if (data.unlocated) {
      const tr = document.createElement('tr');
      const name = document.createElement('td'); name.textContent = T.no_location;
      const count = document.createElement('td'); count.className = 'r'; count.textContent = fmt(data.unlocated);
      tr.append(name, count); tr.style.cursor = 'default'; tr.style.color = '#5b6876';
      tbody.appendChild(tr);
    }
    document.getElementById('mun-total').textContent = fmt(data.totals.beneficiaries);
    if (selected) { const keep = selected; selected = null; select(keep); }
  }

  // ── Gráfiku ──────────────────────────────────────────────
  const charts = {};
  const INK = '#1c2733', GRID = '#e6ebf1';
  function chart(id, config) {
    if (charts[id]) charts[id].destroy();
    charts[id] = new Chart(document.getElementById(id), config);
  }
  function renderCharts(data) {
    if (!window.Chart) return;
    Chart.defaults.font.family = getComputedStyle(document.body).fontFamily;
    Chart.defaults.color = INK;
    const axes = { x: { grid: { display: false } }, y: { beginAtZero: true, grid: { color: GRID }, ticks: { precision: 0 } } };
    const activeYear = data.year;
    chart('chart-year', {
      type: 'bar',
      data: { labels: data.by_year.map((r) => r.year),
        datasets: [{ label: T.beneficiaries, data: data.by_year.map((r) => r.count), borderRadius: 4, maxBarThickness: 46,
          backgroundColor: data.by_year.map((r) => (!activeYear || r.year === activeYear ? '#1f3864' : '#b9c6da')) }] },
      options: { maintainAspectRatio: false, animation: !reduceMotion, plugins: { legend: { display: false } }, scales: axes,
        onClick: (_e, items) => { if (items.length) { yearSelect.value = String(data.by_year[items[0].index].year); load(); } } },
    });
    chart('chart-program', {
      type: 'bar',
      data: { labels: data.by_program.map((r) => r.name),
        datasets: [{ label: T.beneficiaries, data: data.by_program.map((r) => r.count), backgroundColor: '#1e7b46', borderRadius: 4, maxBarThickness: 34 }] },
      options: { indexAxis: 'y', maintainAspectRatio: false, animation: !reduceMotion, plugins: { legend: { display: false } },
        scales: { x: { beginAtZero: true, grid: { color: GRID }, ticks: { precision: 0 } }, y: { grid: { display: false } } } },
    });
    const sex = [[T.male, data.by_sex.male, '#1f3864'], [T.female, data.by_sex.female, '#c8102e'], [T.unknown, data.by_sex.unknown, '#9aa6b4']]
      .filter((row) => row[1] > 0);
    const total = sex.reduce((sum, row) => sum + row[1], 0);
    chart('chart-sex', {
      type: 'doughnut',
      data: { labels: sex.map((r) => `${r[0]} — ${fmt(r[1])} (${total ? Math.round((r[1] / total) * 100) : 0}%)`),
        datasets: [{ data: sex.map((r) => r[1]), backgroundColor: sex.map((r) => r[2]), borderColor: '#fff', borderWidth: 2 }] },
      options: { maintainAspectRatio: false, animation: !reduceMotion, cutout: '58%', plugins: { legend: { position: 'bottom', labels: { boxWidth: 12, padding: 14 } } } },
    });
  }

  // ── Karrega dadus ────────────────────────────────────────
  const yearSelect = document.getElementById('year');
  const csvLink = document.getElementById('csv');
  const csvBase = csvLink.getAttribute('href');
  async function load() {
    const year = yearSelect.value;
    csvLink.href = csvBase + (year ? `?year=${year}` : '');
    try {
      const response = await fetch('/publiku/estatistika/' + (year ? `?year=${year}` : ''), { headers: { Accept: 'application/json' } });
      if (!response.ok) throw new Error(response.status);
      latest = await response.json();
      message.hidden = true;
      renderMunicipalities(latest);
      renderCharts(latest);
      document.getElementById('stamp').textContent = latest.generated_at;
      if (!latest.totals.beneficiaries) { message.textContent = T.no_data; message.hidden = false; }
    } catch (error) {
      message.textContent = T.load_error;
      message.hidden = false;
    }
  }
  yearSelect.addEventListener('change', load);

  fetch(mapBox.dataset.geo).then((r) => r.json()).then(buildMap).catch(() => {}).then(load);
})();
