
// Initialize Supabase client for the landing page
if (typeof supabase !== 'undefined' && window.SUPABASE_URL && window.SUPABASE_ANON_KEY) {
    if (!window.supabaseClient) {
        window.supabaseClient = supabase.createClient(window.SUPABASE_URL, window.SUPABASE_ANON_KEY);
    }
} else {
    console.error('Supabase library or configuration not found');
}

async function handleStartBuilding(e) {
    e.preventDefault();
    const targetUrl = e.currentTarget.getAttribute('href');

    // Safety check
    if (!window.supabaseClient) {
        console.warn('Supabase client not initialized, redirecting normally');
        window.location.href = targetUrl;
        return;
    }

    try {
        // Check session before routing to avoid any potential flash or unnecessary load
        const { data: { session } } = await window.supabaseClient.auth.getSession();

        if (session) {
            window.location.href = targetUrl;
        } else {
            // Determine existing redirect param or create new one
            const loginUrl = new URL('/login/', window.location.origin);
            loginUrl.searchParams.set('redirect', targetUrl);
            window.location.href = loginUrl.toString();
        }
    } catch (err) {
        console.error('Auth check failed:', err);
        window.location.href = targetUrl;
    }
}
