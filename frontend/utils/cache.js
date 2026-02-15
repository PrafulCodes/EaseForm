/**
 * Cache Utility for EaseForm
 * Handles client-side caching with stale-while-revalidate strategy
 */

var CacheUtils = (function () {
    var CACHE_VERSION = "v3";
    var CACHE_PREFIX = "easeform_cache_" + CACHE_VERSION + "_";
    // DEBUG flag removed in favor of Logger

    // TTL Constants (in milliseconds)
    var TTL = {
        FORMS_LIST: 60 * 1000,       // 60 seconds
        FORM_DETAILS: 2 * 60 * 1000, // 2 minutes
        RESPONSES: 30 * 1000,        // 30 seconds
        USER_PROFILE: 5 * 60 * 1000  // 5 minutes
    };

    // Level 1: In-Memory Cache
    var memoryCache = {};

    /**
     * Set data in cache (L1 + L2)
     * @param {string} key - Cache key
     * @param {any} data - Data to cache
     * @param {number} ttl - Time to live in ms (optional, defaults to 5 min)
     */
    function setCache(key, data, ttl) {
        ttl = ttl || (5 * 60 * 1000);
        try {
            var payload = {
                data: data,
                timestamp: Date.now(),
                expiry: Date.now() + ttl
            };

            // Set L1
            memoryCache[key] = payload;

            // Set L2
            // Don't restart L2 writes if one fails (e.g. quota exceeded)
            try {
                sessionStorage.setItem(CACHE_PREFIX + key, JSON.stringify(payload));
            } catch (e) {
                window.Logger.warn('CACHE', "L2 Cache (SessionStorage) failed", e);
            }

            window.Logger.debug('CACHE', `SET: ${key} (TTL: ${ttl}ms)`);
        } catch (e) {
            window.Logger.error('CACHE', "Failed to set cache", e);
        }
    }

    /**
     * Get data from cache (L1 -> L2)
     * @param {string} key - Cache key
     * @returns {any|null} Cached data or null if expired/missing
     */
    function getCache(key) {
        var entry = getEntry(key);
        if (!entry) return null;

        if (entry.expiry > Date.now()) {
            return entry.data;
        } else {
            // Expired - but we don't delete here anymore for SWR
            // Actually, for strict 'get', we should probably return null
            // but keep the data for 'getEntry' callers
            return null;
        }
    }

    /**
     * Get full cache entry (data + metadata) regardless of expiry
     * Used for Stale-While-Revalidate
     */
    function getEntry(key) {
        var now = Date.now();

        // 1. Try L1 (Memory)
        if (memoryCache[key]) {
            // window.Logger.debug('CACHE', `L1 HIT: ${key}`);
            return memoryCache[key];
        }

        // 2. Try L2 (SessionStorage)
        try {
            var raw = sessionStorage.getItem(CACHE_PREFIX + key);
            if (!raw) {
                window.Logger.debug('CACHE', `MISS: ${key}`);
                return null;
            }

            var payload = JSON.parse(raw);
            // Hydrate L1
            memoryCache[key] = payload;
            window.Logger.debug('CACHE', `L2 HIT: ${key}`);
            return payload;
        } catch (e) {
            window.Logger.error('CACHE', "Failed to parse L2 cache", e);
            return null;
        }
    }

    /**
     * Invalidate specific key
     */
    function invalidate(key) {
        delete memoryCache[key];
        sessionStorage.removeItem(CACHE_PREFIX + key);
        window.Logger.debug('CACHE', `INVALIDATED: ${key}`);
    }

    /**
     * Invalidate keys matching a pattern (regex or substring)
     */
    function invalidatePattern(pattern) {
        // Clear L1
        Object.keys(memoryCache).forEach(function (key) {
            if (key.match(pattern)) {
                delete memoryCache[key];
            }
        });

        // Clear L2
        Object.keys(sessionStorage).forEach(function (key) {
            if (key.startsWith(CACHE_PREFIX)) {
                var cleanKey = key.replace(CACHE_PREFIX, '');
                if (cleanKey.match(pattern)) {
                    sessionStorage.removeItem(key);
                }
            }
        });
        window.Logger.debug('CACHE', `Invalidated pattern: ${pattern}`);
    }

    /**
     * Clear all EaseForm cache items
     */
    function clearCache() {
        memoryCache = {};
        try {
            Object.keys(sessionStorage).forEach(function (key) {
                if (key.startsWith(CACHE_PREFIX)) {
                    sessionStorage.removeItem(key);
                }
            });
            window.Logger.info('CACHE', "Cleared");
        } catch (e) {
            window.Logger.error('CACHE', "Failed to clear cache", e);
        }
    }

    return {
        set: setCache,
        get: getCache,
        getEntry: getEntry,
        invalidate: invalidate,
        invalidatePattern: invalidatePattern,
        clear: clearCache,
        TTL: TTL,
        PREFIX: CACHE_PREFIX
    };
})();

// Export to window
window.CacheUtils = CacheUtils;
