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
        state: 'loading', // 'loading' | 'authenticated' | 'unauthenticated'
        session: null,
        user: null,
        _readyResolvers: [],

        init: async function () {
            // 1. Wait for Supabase Client
            if (!window.supabaseClient) {
                console.warn('AuthGuard: Supabase client not ready, waiting...');
                try {
                    await window.waitForSupabase();
                } catch (e) {
                    console.error('AuthGuard: Failed to wait for Supabase client', e);
                    return;
                }
            }



            // 2. Setup Listener (Critical: handle state changes globally)
            window.supabaseClient.auth.onAuthStateChange((event, session) => {
                this._handleStateChange(event, session);
            });

            // 3. Initial Check
            try {
                const { data: { session } } = await window.supabaseClient.auth.getSession();
                this._handleStateChange('INITIAL_CHECK', session);
            } catch (err) {
                console.error('AuthGuard: Initial check error', err);
                this._handleStateChange('INITIAL_CHECK_ERROR', null);
            }
        },

        _handleStateChange: function (event, session) {
            console.log(`AuthGuard: State Change [${event}]`, session ? 'Session Active' : 'No Session');

            this.session = session;
            this.user = session ? session.user : null;
            const previousState = this.state;

            if (session) {
                this.state = 'authenticated';

                // If on login page, redirect to dashboard or returnUrl
                if (window.location.pathname.includes('/login')) {
                    this._handleLoginRedirect();
                    return;
                }

                // On protected pages, just show content
                this.showContent();

            } else {
                this.state = 'unauthenticated';

                // If on protected page, redirect to login
                if (!window.location.pathname.includes('/login') && window.location.pathname !== '/') {
                    this._handleLogoutRedirect();
                    return;
                }

                // If on login or landing, show content
                this.showContent();
            }

            // Resolve any waiters
            if (previousState === 'loading' && this.state !== 'loading') {
                this._resolveReady();
            }
        },

        _handleLoginRedirect: function () {
            // Check for redirect param
            const params = new URLSearchParams(window.location.search);
            const redirectParam = params.get('redirect');
            const returnTo = sessionStorage.getItem('returnTo');

            let target = '/dashboard/';
            if (redirectParam) {
                target = redirectParam;
            } else if (returnTo) {
                target = returnTo;
                sessionStorage.removeItem('returnTo');
            }

            console.log('AuthGuard: Redirecting to', target);
            window.location.href = target;
        },

        _handleLogoutRedirect: function () {
            console.log('AuthGuard: Redirecting to login');
            sessionStorage.setItem('returnTo', window.location.href);
            window.location.href = '/login/';
        },

        // Helper for other scripts to wait for auth
        waitForAuth: function () {
            if (this.state !== 'loading') {
                return Promise.resolve(this.state === 'authenticated');
            }
            return new Promise(resolve => {
                this._readyResolvers.push(() => resolve(this.state === 'authenticated'));
            });
        },

        _resolveReady: function () {
            this._readyResolvers.forEach(resolve => resolve(this.state === 'authenticated'));
            this._readyResolvers = [];
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
