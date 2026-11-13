/* Painel offline: lista rejistu iha dispozitivu no sinkronizasaun. */
(function () {
  'use strict';
  const store = window.SjamciOffline;
  const root = document.getElementById('hub');
  const username = root.dataset.username;
  const list = document.getElementById('queue');
  const status = document.getElementById('sync-status');
  const syncButton = document.getElementById('sync-now');
  const LABELS = { pending: 'Hein sinkroniza', synced: 'Sinkroniza ona', invalid: 'Presiza hadia' };

  store.watchNetwork(document.getElementById('net'));

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  async function render() {
    const records = (await store.all()).filter((r) => r.username === username);
    list.innerHTML = '';
    document.getElementById('empty').hidden = records.length > 0;
    const pending = records.filter((r) => r.status === 'pending').length;
    document.getElementById('pending-count').textContent = pending;
    syncButton.disabled = pending === 0;

    records.forEach((record) => {
      const item = el('li');
      const top = el('div', 'top');
      top.appendChild(el('span', 'name', `${record.label} — ${record.module.toUpperCase()}`));
      top.appendChild(el('span', 'tag ' + record.status, LABELS[record.status] || record.status));
      item.appendChild(top);
      item.appendChild(el('div', 'detail', 'Prienxe: ' + new Date(record.filledAt).toLocaleString()));
      if (record.status !== 'synced' && record.message) item.appendChild(el('div', 'detail', record.message));
      (record.notes || []).forEach((note) => item.appendChild(el('div', 'note', note)));

      const actions = el('div', 'actions');
      if (record.status !== 'synced') {
        const edit = el('a', 'btn alt small', 'Hadia');
        edit.href = `/offline/rejistu/${record.module}/?edit=${record.uuid}`;
        actions.appendChild(edit);
      } else if (record.url) {
        const open = el('a', 'btn alt small', 'Loke iha sistema');
        open.href = record.url;
        actions.appendChild(open);
      }
      const remove = el('button', 'btn danger small', record.status === 'synced' ? 'Hasai husi lista' : 'Hamoos');
      remove.type = 'button';
      remove.addEventListener('click', async () => {
        if (record.status !== 'synced' && !confirm('Hamoos rejistu ne\'e husi dispozitivu? Dadus seidauk haruka ba servidór.')) return;
        await store.remove(record.uuid);
        render();
      });
      actions.appendChild(remove);
      item.appendChild(actions);
      list.appendChild(item);
    });
  }

  async function sync() {
    if (!navigator.onLine) { status.textContent = 'Offline — rejistu sei haruka bainhira iha internet.'; return; }
    status.textContent = 'Sinkroniza hela…';
    const result = await store.syncAll(username, render);
    if (result.busy) return;
    await render();
    const parts = [];
    if (result.synced) parts.push(`${result.synced} haruka ona`);
    if (result.invalid) parts.push(`${result.invalid} presiza hadia`);
    if (result.waiting) parts.push(`${result.waiting} sei hein`);
    status.textContent = parts.length ? parts.join(', ') + '.' : 'La iha rejistu atu haruka.';
    document.getElementById('login-needed').hidden = !result.auth;
  }

  syncButton.addEventListener('click', sync);
  window.addEventListener('online', sync);

  // Instala aplikasaun
  let installEvent = null;
  const installButton = document.getElementById('install');
  window.addEventListener('beforeinstallprompt', (event) => {
    event.preventDefault();
    installEvent = event;
    installButton.hidden = false;
  });
  installButton.addEventListener('click', async () => {
    if (!installEvent) return;
    installEvent.prompt();
    await installEvent.userChoice;
    installButton.hidden = true;
  });

  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js', { scope: '/' }).then(() => navigator.serviceWorker.ready)
      .then((registration) => { if (registration.active) registration.active.postMessage('precache'); })
      .catch(() => {});
  }

  render().then(sync);
})();
