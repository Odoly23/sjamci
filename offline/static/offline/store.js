/* Armazenamentu lokál (IndexedDB) no sinkronizasaun ba rejistu offline. */
(function () {
  'use strict';
  const DB_NAME = 'sjamci-offline';
  const STORE = 'queue';
  let syncing = false;

  function open() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, 1);
      request.onupgradeneeded = () => request.result.createObjectStore(STORE, { keyPath: 'uuid' });
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async function run(mode, action) {
    const db = await open();
    return new Promise((resolve, reject) => {
      const tx = db.transaction(STORE, mode);
      const request = action(tx.objectStore(STORE));
      tx.oncomplete = () => resolve(request && request.result);
      tx.onerror = () => reject(tx.error);
    });
  }

  const put = (record) => run('readwrite', (s) => s.put(record));
  const get = (uuid) => run('readonly', (s) => s.get(uuid));
  const remove = (uuid) => run('readwrite', (s) => s.delete(uuid));
  async function all() {
    const records = (await run('readonly', (s) => s.getAll())) || [];
    return records.sort((a, b) => (a.filledAt < b.filledAt ? 1 : -1));
  }

  function newId() {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    const b = crypto.getRandomValues(new Uint8Array(16));
    b[6] = (b[6] & 0x0f) | 0x40; b[8] = (b[8] & 0x3f) | 0x80;
    const h = Array.from(b, (x) => x.toString(16).padStart(2, '0')).join('');
    return `${h.slice(0, 8)}-${h.slice(8, 12)}-${h.slice(12, 16)}-${h.slice(16, 20)}-${h.slice(20)}`;
  }

  function csrfToken() {
    const match = document.cookie.match(/(?:^|; )csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : '';
  }

  /* Haruka rejistu ida. Fó fali: 'synced' | 'invalid' | 'auth' | 'offline' */
  async function syncOne(record) {
    const body = new FormData();
    body.append('uuid', record.uuid);
    body.append('module', record.module);
    body.append('filled_at', record.filledAt);
    for (const field of record.fields) {
      if (field.v instanceof Blob) body.append(field.k, field.v, field.name || 'ficheiru');
      else body.append(field.k, field.v);
    }
    let response;
    try {
      response = await fetch('/offline/sync/', {
        method: 'POST', body, credentials: 'same-origin', redirect: 'manual',
        headers: { 'X-CSRFToken': csrfToken(), 'X-Requested-With': 'XMLHttpRequest' },
      });
    } catch (error) {
      return 'offline';
    }
    let data = null;
    try { data = await response.json(); } catch (error) { /* la'ós JSON: sesaun remata ka erru proxy */ }

    if (response.ok && data && data.status === 'ok') {
      // Dadus pesoál hasai husi dispozitivu; rai de'it rezumu no nota husi servidór
      await put({ uuid: record.uuid, module: record.module, label: record.label, username: record.username,
        filledAt: record.filledAt, status: 'synced', url: data.url, notes: data.messages || [], fields: [] });
      return 'synced';
    }
    if (response.status === 422 && data) {
      record.status = 'invalid';
      record.message = data.message || 'Dadus la válidu.';
      record.errors = data.errors || {};
      await put(record);
      return 'invalid';
    }
    if (response.status >= 500) {
      // Erru servidór: rejistu hein nafatin, maibé hatudu razaun ba utilizador
      record.message = (data && data.message) || 'Erru iha servidór. Sei koko fali.';
      await put(record);
      return 'offline';
    }
    if (response.status === 403 && data && data.status === 'forbidden') {
      record.status = 'invalid';
      record.message = data.message;
      await put(record);
      return 'invalid';
    }
    return 'auth';   // 401, 403 CSRF, redireta ba login
  }

  /* Haruka rejistu hotu ne'ebé hein hela. */
  async function syncAll(username, onProgress) {
    if (syncing) return { busy: true };
    syncing = true;
    const summary = { synced: 0, invalid: 0, waiting: 0, auth: false };
    try {
      const pending = (await all()).filter((r) => r.status === 'pending' && r.username === username).reverse();
      for (const record of pending) {
        const outcome = await syncOne(record);
        if (outcome === 'synced') summary.synced += 1;
        else if (outcome === 'invalid') summary.invalid += 1;
        else {
          summary.waiting += 1;
          if (outcome === 'auth') summary.auth = true;
          if (outcome === 'auth' || outcome === 'offline') {
            summary.waiting = pending.length - summary.synced - summary.invalid;
            break;
          }
        }
        if (onProgress) onProgress();
      }
    } finally {
      syncing = false;
    }
    return summary;
  }

  function watchNetwork(element) {
    const update = () => {
      element.textContent = navigator.onLine ? 'Online' : 'Offline';
      element.className = 'net ' + (navigator.onLine ? 'on' : 'off');
    };
    window.addEventListener('online', update);
    window.addEventListener('offline', update);
    update();
  }

  window.SjamciOffline = { put, get, remove, all, newId, syncAll, watchNetwork };
})();
