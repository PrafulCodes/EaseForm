// ============================================
// AUTH GUARD UTILITY
// ============================================
// Prevents "flash of unauthenticated content" by
// hiding the page until auth state is confirmed.

(function () {
    // Immediate style injection to hide body content
    const style = document.createElement('style');
    style.id = 'auth-guard-style';
    style.innerHTML = 'body { visibility: hidden !important; opacity: 0 !important; transition: opacity 0.2s ease; }';
    document.head.appendChild(style);

    window.AuthGuard = {
        init: async function () {
            // Wait for Supabase client to be available
            if (!window.supabaseClient) {
                // If this script runs before config.js finishes, wait a bit
                // In production, script order should ensure config.js runs first
                if (window.supabase) {
                    // Try to initialize it if config is present but not client
                    if (window.APP_CONFIG && window.supabase.createClient) {
                        const { url, anonKey } = window.APP_CONFIG.supabase;
                        window.supabaseClient = window.supabase.createClient(url, anonKey);
                    }
                }
            }

            // Retry client check with a small delay if still missing (race condition safety)
            if (!window.supabaseClient) {
                console.warn('AuthGuard: Supabase client not ready, retrying...');
                setTimeout(() => window.AuthGuard.init(), 50);
                return;
            }

            try {
                // 1. Check Session
                const { data: { session }, error } = await window.supabaseClient.auth.getSession();

                if (error || !session) {
                    // UNATUTHENTICATED
                    console.log('AuthGuard: No session, redirecting to login');

                    // Store return URL if not already stored
                    if (window.location.pathname !== '/login/' && window.location.pathname !== '/') {
                        sessionStorage.setItem('returnTo', window.location.href);
                    }

                    window.location.href = '/login/';
                    return;
                }

                // AUTHENTICATED
                console.log('AuthGuard: Session confirmed');

                // If we are on login page, redirect to dashboard
                if (window.location.pathname.includes('/login')) {
                    window.location.href = '/dashboard/';
                    return;
                }

                // Show content
                this.showContent();

            } catch (err) {
                console.error('AuthGuard: Error', err);
                window.location.href = '/login/';
            }
        },

        showContent: function () {
            const style = document.getElementById('auth-guard-style');
            if (style) {
                style.innerHTML = 'body { visibility: visible !important; opacity: 1 !important; transition: opacity 0.2s ease; }';
            } else {
                document.body.style.visibility = 'visible';
                document.body.style.opacity = '1';
            }
        }
    };
})();
