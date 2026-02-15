/**
 * SUPABASE CLIENT INITIALIZATION
 * 
 * Centralized entry point for Supabase client.
 * Ensures strict initialization order:
 * 1. Config loaded
 * 2. Supabase client created
 * 3. Derived services (Auth, API) can run
 */

(function () {
    // Prevent double initialization
    if (window.supabaseClient) {
        window.Logger ? window.Logger.warn('Init', 'Supabase client already initialized') : console.warn('Supabase client already initialized');
        return;
    }

    // validate Config
    if (!window.APP_CONFIG || !window.APP_CONFIG.supabase) {
        const errorMsg = 'Configuration missing: APP_CONFIG.supabase not found. Ensure config.js is loaded before supabase-client.js';
        console.error(errorMsg);
        document.body.innerHTML = `<div style="padding: 20px; color: red; font-family: sans-serif;"><h1>System Error</h1><p>${errorMsg}</p></div>`;
        throw new Error(errorMsg);
    }

    const { url, anonKey } = window.APP_CONFIG.supabase;

    if (!url || !anonKey) {
        const errorMsg = 'Invalid Configuration: Supabase URL or Anon Key is missing.';
        console.error(errorMsg);
        throw new Error(errorMsg);
    }

    if (typeof window.supabase === 'undefined' || typeof window.supabase.createClient === 'undefined') {
        const errorMsg = 'Supabase JS library not loaded. Ensure supabase-js script tag is included.';
        console.error(errorMsg);
        throw new Error(errorMsg);
    }

    try {
        // Initialize Client
        window.supabaseClient = window.supabase.createClient(url, anonKey, {
            auth: {
                persistSession: true,
                autoRefreshToken: true,
                detectSessionInUrl: true
            }
        });

        // Log success
        if (window.Logger) {
            window.Logger.info('Init', 'Supabase client initialized successfully');
        } else {
            console.log('[Init] Supabase client initialized successfully');
        }

    } catch (err) {
        console.error('Failed to initialize Supabase client:', err);
        throw err;
    }
})();

// Helper to wait for client (for async scripts)
window.waitForSupabase = function () {
    return new Promise((resolve, reject) => {
        if (window.supabaseClient) {
            resolve(window.supabaseClient);
            return;
        }

        let attempts = 0;
        const maxAttempts = 50; // 5 seconds
        const interval = setInterval(() => {
            attempts++;
            if (window.supabaseClient) {
                clearInterval(interval);
                resolve(window.supabaseClient);
            } else if (attempts >= maxAttempts) {
                clearInterval(interval);
                reject(new Error('Timeout waiting for Supabase client'));
            }
        }, 100);
    });
};
