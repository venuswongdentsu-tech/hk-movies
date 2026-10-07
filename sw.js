/* 香港電影週報 — service worker（離線快取） */
const VER = "hkmv-20261007-d0dc5ec2";
const CORE = ["./", "./index.html", "./manifest.webmanifest", "./data.js",
              "./icons/icon-192.png", "./icons/icon-512.png", "./icons/apple-touch-icon.png"];

self.addEventListener("install", e => {
  e.waitUntil((async () => {
    const c = await caches.open(VER);
    await c.addAll(CORE.map(u => new Request(u, { cache: "reload" }))).catch(() => {});
    self.skipWaiting();
  })());
});

self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(k => k !== VER).map(k => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener("message", e => { if (e.data === "skipWaiting") self.skipWaiting(); });

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;

  // 導覽請求：網絡優先，斷網時回落快取（保證 index.html 每週更新）
  if (req.mode === "navigate") {
    e.respondWith((async () => {
      try {
        const fresh = await fetch(req);
        const c = await caches.open(VER);
        c.put("./index.html", fresh.clone());
        return fresh;
      } catch (err) {
        const c = await caches.open(VER);
        return (await c.match("./index.html")) || (await c.match("./")) ||
               new Response("離線", { status: 503 });
      }
    })());
    return;
  }

  // 資料檔：網絡優先（每週更新必須即刻生效），斷網時回落快取
  if (url.pathname.endsWith("/data.js")) {
    e.respondWith((async () => {
      try {
        const fresh = await fetch(req, { cache: "no-store" });
        const c = await caches.open(VER);
        if (fresh && fresh.ok) c.put("./data.js", fresh.clone());
        return fresh;
      } catch (err) {
        const c = await caches.open(VER);
        return (await c.match("./data.js")) || new Response("", { status: 503 });
      }
    })());
    return;
  }

  // 其他同源資源：快取優先，背景更新
  e.respondWith((async () => {
    const c = await caches.open(VER);
    const hit = await c.match(req);
    const net = fetch(req).then(r => { if (r && r.ok) c.put(req, r.clone()); return r; }).catch(() => null);
    return hit || (await net) || new Response("", { status: 504 });
  })());
});
