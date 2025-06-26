// Service Worker for NYC Nightlife iOS PWA
const CACHE_NAME = 'nyc-nightlife-v1';
const urlsToCache = [
    '/ios_webapp.html',
    '/mobile',
    '/public'
];

// Install service worker
self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                return cache.addAll(urlsToCache);
            })
    );
});

// Fetch event
self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                // Return cached version or fetch from network
                return response || fetch(event.request);
            }
        )
    );
});