/* Formuláriu rejistu offline: kaskata munisípiu → postu → suku, GPS, rai iha dispozitivu. */
(function () {
  'use strict';
  const store = window.SjamciOffline;
  const form = document.getElementById('offline-form');
  const moduleKey = form.dataset.module;
  const username = form.dataset.username;
  const geo = JSON.parse(document.getElementById('geo-data').textContent);
  const editId = new URLSearchParams(location.search).get('edit');
  let editing = null;

  store.watchNetwork(document.getElementById('net'));

  // ── Kaskata lokalizasaun (la presiza rede) ────────────────
  const municipality = form.querySelector('[data-geo="municipality"]');
  const post = form.querySelector('[data-geo="administrativepost"]');
  const village = form.querySelector('[data-geo="village"]');

  function fill(select, items, selected) {
    select.innerHTML = '';
    select.appendChild(new Option('---------', ''));
    items.forEach((item) => select.appendChild(new Option(item.name, item.id)));
    select.value = selected || '';
  }
  function refreshPosts(selected) {
    const id = Number(municipality.value);
    fill(post, id ? geo.posts.filter((p) => p.municipality_id === id) : [], selected);
    refreshVillages();
  }
  function refreshVillages(selected) {
    const id = Number(post.value);
    fill(village, id ? geo.villages.filter((v) => v.administrativepost_id === id) : [], selected);
  }
  if (municipality && post && village) {
    municipality.addEventListener('change', () => refreshPosts());
    post.addEventListener('change', () => refreshVillages());
    refreshPosts();
  }

  // ── GPS (la'o maski la iha internet) ──────────────────────
  const gpsButton = document.getElementById('gps');
  const gpsStatus = document.getElementById('gps-status');
  if (gpsButton) {
    gpsButton.addEventListener('click', () => {
      if (!navigator.geolocation) { gpsStatus.textContent = 'Dispozitivu la suporta GPS.'; return; }
      gpsStatus.textContent = 'Buka hela pozisaun…';
      navigator.geolocation.getCurrentPosition((position) => {
        form.querySelector('[data-step="location"] [name="latitude"]').value = position.coords.latitude.toFixed(6);
        form.querySelector('[data-step="location"] [name="longitude"]').value = position.coords.longitude.toFixed(6);
        gpsStatus.textContent = `Pozisaun hetan (presizaun ±${Math.round(position.coords.accuracy)} m).`;
      }, (error) => {
        gpsStatus.textContent = 'La konsege hetan pozisaun: ' + error.message;
      }, { enableHighAccuracy: true, timeout: 20000 });
    });
  }

  // ── Halibur kampu sira kada pasu ──────────────────────────
  function collect() {
    const fields = [];
    form.querySelectorAll('fieldset[data-step]').forEach((fieldset) => {
      const step = fieldset.dataset.step;
      fieldset.querySelectorAll('[name]').forEach((el) => {
        const key = `${step}.${el.name}`;
        if (el.type === 'file') {
          if (el.files.length) fields.push({ k: key, v: el.files[0], name: el.files[0].name });
          else if (editing) {
            const kept = editing.fields.find((f) => f.k === key);
            if (kept) fields.push(kept);
          }
        } else if (el.type === 'checkbox') {
          if (el.checked) fields.push({ k: key, v: el.value || 'on' });
        } else if (el.type === 'radio') {
          if (el.checked) fields.push({ k: key, v: el.value });
        } else if (el.multiple) {
          Array.from(el.selectedOptions).forEach((o) => fields.push({ k: key, v: o.value }));
        } else if (el.value !== '') {
          fields.push({ k: key, v: el.value });
        }
      });
    });
    return fields;
  }

  function showErrors(record) {
    const box = document.getElementById('server-errors');
    if (!record.message) return;
    box.hidden = false;
    box.textContent = record.message;
    Object.entries(record.errors || {}).forEach(([step, byField]) => {
      Object.entries(byField).forEach(([name, messages]) => {
        const el = form.querySelector(`fieldset[data-step="${step}"] [name="${name}"]`);
        if (!el) return;
        const wrapper = el.closest('.field');
        wrapper.classList.add('bad');
        const note = document.createElement('div');
        note.className = 'err';
        note.textContent = messages.join(' ');
        wrapper.appendChild(note);
      });
    });
  }

  async function loadForEdit() {
    if (!editId) return;
    editing = await store.get(editId);
    if (!editing || editing.module !== moduleKey) { editing = null; return; }
    const values = {};
    editing.fields.forEach((f) => { if (!(f.v instanceof Blob)) (values[f.k] = values[f.k] || []).push(f.v); });
    const pick = (key) => (values[key] || [''])[0];
    if (municipality) {
      municipality.value = pick('location.municipality');
      refreshPosts(pick('location.administrativepost'));
      refreshVillages(pick('location.village'));
    }
    form.querySelectorAll('fieldset[data-step]').forEach((fieldset) => {
      fieldset.querySelectorAll('[name]').forEach((el) => {
        if (el.dataset.geo || el.type === 'file') return;
        const key = `${fieldset.dataset.step}.${el.name}`;
        if (el.type === 'checkbox' || el.type === 'radio') el.checked = (values[key] || []).includes(el.value || 'on');
        else if (key in values) el.value = values[key][0];
      });
    });
    editing.fields.filter((f) => f.v instanceof Blob).forEach((f) => {
      const [step, name] = f.k.split('.');
      const el = form.querySelector(`fieldset[data-step="${step}"] [name="${name}"]`);
      if (el) {
        el.required = false;
        const note = document.createElement('div');
        note.className = 'help';
        note.textContent = `Ficheiru rai ona: ${f.name}. Hili foun se hakarak troka.`;
        el.closest('.field').appendChild(note);
      }
    });
    showErrors(editing);
  }

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const button = form.querySelector('button[type="submit"]');
    button.disabled = true;
    const name = (form.querySelector('fieldset[data-step="benef"] [name="name"]') || {}).value || '(la iha naran)';
    try {
      await store.put({
        uuid: editing ? editing.uuid : store.newId(),
        module: moduleKey,
        label: name,
        username,
        filledAt: editing ? editing.filledAt : new Date().toISOString(),
        status: 'pending',
        fields: collect(),
      });
      location.href = form.dataset.hub + '?saved=1';
    } catch (error) {
      button.disabled = false;
      const box = document.getElementById('server-errors');
      box.hidden = false;
      box.textContent = 'La konsege rai iha dispozitivu: ' + error.message;
    }
  });

  loadForEdit();
})();
