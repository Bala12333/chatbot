/**
 * Service Worker for Crop Crystalline Chatbot
 * Provides offline support and caching
 */

const CACHE_NAME = 'crop-chatbot-v1';
const urlsToCache = [
    '/',
    '/static/css/style.css',
    '/static/js/chatbot.js',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(urlsToCache))
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Return cached version or fetch from network
                return response || fetch(event.request);
            })
    );
});