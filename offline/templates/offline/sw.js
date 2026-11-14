/* Service worker SJAMCI — rejistu offline.
   Só rai pajina formuláriu offline no nia ficheiru estátiku; pajina ho dadus
   benefisiáriu la rai iha dispozitivu. */
const CACHE = 'sjamci-offline-{{ version }}';
const PAGES = {{ pages_json|safe }};
const ASSETS = {{ assets_json|safe }};
const HUB = '{{ hub }}';

async function precache() {
  const cache = await caches.open(CACHE);
  await Promise.all([...PAGES, ...ASSETS].map(async (url) => {
    try {
      const response = await fetch(url, { credentials: 'same-origin' });
      // Pajina ne'ebé redireta ba login ka 403 la rai
      if (response.ok && !response.redirected) await cache.put(url, response);
    } catch (error) { /* offline: koko fali iha vizita tuir mai */ }
  }));
}

self.addEventListener('install', (event) => {
  event.waitUntil(precache().then(() => self.skipWaiting()));
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const names = await caches.keys();
    await Promise.all(names.filter((n) => n.startsWith('sjamci-offline-') && n !== CACHE).map((n) => caches.delete(n)));
    await self.clients.claim();
  })());
});

self.addEventListener('message', (event) => {
  if (event.data === 'precache') event.waitUntil(precache());
});

async function networkFirst(request, key) {
  const cache = await caches.open(CACHE);
  try {
    const response = await fetch(request);
    if (response.ok && !response.redirected) cache.put(key, response.clone());
    return response;
  } catch (error) {
    const cached = await cache.match(key);
    if (cached) return cached;
    throw error;
  }
}

async function cacheFirst(request, key) {
  const cache = await caches.open(CACHE);
  const cached = await cache.match(key);
  const refresh = fetch(request).then((response) => {
    if (response.ok) cache.put(key, response.clone());
    return response;
  });
  if (cached) { refresh.catch(() => {}); return cached; }
  return refresh;
}

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  if (PAGES.includes(url.pathname)) {
    event.respondWith(networkFirst(request, url.pathname));
  } else if (ASSETS.includes(url.pathname)) {
    event.respondWith(cacheFirst(request, url.pathname));
  } else if (request.mode === 'navigate') {
    // Pajina seluk presiza rede; se offline, hatudu painel offline
    event.respondWith(fetch(request).catch(async () => {
      const cached = await (await caches.open(CACHE)).match(HUB);
      return cached || new Response('Offline', { status: 503, headers: { 'Content-Type': 'text/plain' } });
    }));
  }
});
