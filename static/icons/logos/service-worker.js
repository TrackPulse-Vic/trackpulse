
    // Based off of https://github.com/pwa-builder/PWABuilder/blob/main/docs/sw.js

    /*
      Welcome to our basic Service Worker! This Service Worker offers a basic offline experience
      while also being easily customizeable. You can add in your own code to implement the capabilities
      listed below, or change anything else you would like.


      Need an introduction to Service Workers? Check our docs here: https://docs.pwabuilder.com/#/home/sw-intro
      Want to learn more about how our Service Worker generation works? Check our docs here: https://docs.pwabuilder.com/#/studio/existing-app?id=add-a-service-worker

      Did you know that Service Workers offer many more capabilities than just offline? 
        - Background Sync: https://microsoft.github.io/win-student-devs/#/30DaysOfPWA/advanced-capabilities/06
        - Periodic Background Sync: https://web.dev/periodic-background-sync/
        - Push Notifications: https://microsoft.github.io/win-student-devs/#/30DaysOfPWA/advanced-capabilities/07?id=push-notifications-on-the-web
        - Badges: https://microsoft.github.io/win-student-devs/#/30DaysOfPWA/advanced-capabilities/07?id=application-badges
    */

    const CACHE_NAME = 'trackpulse-v3'

    /**
     *  @Lifecycle Activate
     *  New one activated when old isnt being used.
     *
     *  waitUntil(): activating ====> activated
     */
    self.addEventListener('activate', event => {
            event.waitUntil(
                caches.keys().then(keys => Promise.all(
                    keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
                )).then(() => self.clients.claim())
            )
    })

    /**
     *  @Functional Fetch
     *  All network requests are being intercepted here.
     *
     *  void respondWith(Promise<Response> r)
     */
        self.addEventListener('fetch', event => {
            const request = event.request
            const url = new URL(request.url)
            if (url.origin !== self.location.origin || request.method !== 'GET') return

            if (url.pathname.startsWith('/static/')) {
                event.respondWith(caches.match(request).then(cached => cached || fetch(request).then(response => {
                    const copy = response.clone()
                    caches.open(CACHE_NAME).then(cache => cache.put(request, copy))
                    return response
                })))
                return
            }

            event.respondWith(fetch(request).catch(() => caches.match(request)))
    })
