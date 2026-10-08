// Service worker: siden virker offline (dækningen på kirkegården er dårlig). Alt serveres fra cachen og
// opdateres i baggrunden (stale-while-revalidate).
//
// VIGTIGT: Bump VERSION ved hvert deploy, der ændrer index.html, gravsteder.json, kortet, fonte eller ikoner.
// Ellers kan en gammel side hænge fast i cachen hos dem, der allerede har besøgt siden. Se CLAUDE.md.
const VERSION = '2026-10-08j';
const CACHE = 'gravsteder-' + VERSION;
const CORE = ['./', './index.html', './gravsteder.json', './ruter.json', './manifest.webmanifest'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;
  // Cache først, opdatér i baggrunden. Rettetilstandens eksport henter gravsteder.json med cache: 'no-store'
  // og ?t=…; den skal uden om cachen, så en ny fil aldrig flettes oven på en gammel.
  if (url.pathname.endsWith('/gravsteder.json') && url.search) {
    e.respondWith(fetch(req));
    return;
  }
  e.respondWith(
    caches.open(CACHE).then(c => c.match(req, { ignoreSearch: true }).then(hit => {
      const net = fetch(req).then(r => { if (r.ok) c.put(req, r.clone()); return r; }).catch(() => hit);
      return hit || net;
    }))
  );
});
