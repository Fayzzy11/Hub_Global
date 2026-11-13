/* Service worker du hub : rend l'application installable et utilisable hors ligne.
   Stratégie « réseau d'abord » : la version en ligne est toujours préférée, la copie
   en cache ne sert que sans connexion. Les appels à l'API de GitHub (données privées)
   ne sont jamais mis en cache ici. */
const CACHE = "hub-v9";
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", e => e.waitUntil(caches.keys().then(k => Promise.all(k.filter(n => n !== CACHE).map(n => caches.delete(n)))).then(() => self.clients.claim())));
self.addEventListener("fetch", e => {
  const u = new URL(e.request.url);
  if (e.request.method !== "GET" || u.hostname === "api.github.com") return;
  e.respondWith(
    fetch(e.request).then(r => { if (r.ok || r.type === "opaque") { const copie = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copie)); } return r; })
      .catch(() => caches.match(e.request, { ignoreSearch: u.origin === location.origin }).then(r => r || Response.error()))
  );
});
