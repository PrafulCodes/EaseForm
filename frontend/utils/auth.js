// ============================================
// AUTHENTICATION UTILITIES
// ============================================
// Helper functions for Supabase Auth operations
// Following EaseForm's database architecture rules

// Get Supabase client from config
function getSupabaseClient() {
    if (!window.APP_CONFIG) {
        window.Logger.error('AUTH', 'APP_CONFIG not loaded. Make sure config.js is included.');
        return null;
    }

    const { url, anonKey } = window.APP_CONFIG.supabase;
    return window.supabase.createClient(url, anonKey);
}

// ============================================
// SESSION MANAGEMENT
// ============================================

/**
 * Check if user is authenticated
 * @returns {Promise<{isAuthenticated: boolean, session: object|null, user: object|null}>}
 */
async function checkAuth() {
    const supabase = getSupabaseClient();
    if (!supabase) return { isAuthenticated: false, session: null, user: null };

    const { data: { session }, error } = await supabase.auth.getSession();

    if (error) {
        window.Logger.error('AUTH', 'Error checking auth', error);
        return { isAuthenticated: false, session: null, user: null };
    }

    return {
        isAuthenticated: !!session,
        session: session,
        user: session?.user || null
    };
}

/**
 * Require authentication - redirect to login if not authenticated
 * Use this on protected pages (dashboard, create-form, etc.)
 * @param {string} redirectUrl - URL to redirect to after login (optional)
 */
async function requireAuth(redirectUrl = null) {
    const { isAuthenticated, user } = await checkAuth();

    if (!isAuthenticated) {
        // Save current page for redirect after login
        const returnTo = redirectUrl || window.location.pathname;
        sessionStorage.setItem('returnTo', returnTo);

        // Redirect to login
        window.location.href = '/login/';
        return null;
    }

    return user;
}

/**
 * Get current user's ID (auth.uid())
 * This is the ID used for RLS policies
 * @returns {Promise<string|null>}
 */
async function getCurrentUserId() {
    const { user } = await checkAuth();
    return user?.id || null;
}

/**
 * Get current user's email
 * @returns {Promise<string|null>}
 */
async function getCurrentUserEmail() {
    const { user } = await checkAuth();
    return user?.email || null;
}

// ============================================
// SIGN OUT
// ============================================

/**
 * Sign out the current user
 * @param {string} redirectUrl - Where to redirect after sign out (default: landing page)
 */
async function signOut(redirectUrl = '/landing/index.html') {
    const supabase = getSupabaseClient();
    if (!supabase) return;

    const { error } = await supabase.auth.signOut();

    if (error) {
        window.Logger.error('AUTH', 'Error signing out', error);
        return;
    }

    // Clear any stored data
    sessionStorage.clear();

    // Clear application cache if available
    if (window.CacheUtils) {
        window.CacheUtils.clear();
    }

    // Redirect
    window.location.href = redirectUrl;
}

// ============================================
// HOST PROFILE OPERATIONS
// ============================================

/**
 * Get the current host's profile from public.hosts table
 * @returns {Promise<object|null>}
 */
async function getCurrentHostProfile() {
    const supabase = getSupabaseClient();
    if (!supabase) return null;

    const userId = await getCurrentUserId();
    if (!userId) return null;

    // RLS will automatically filter to only this user's data
    const { data, error } = await supabase
        .from('hosts')
        .select('*')
        .eq('id', userId)
        .single();

    if (error) {
        window.Logger.error('AUTH', 'Error fetching host profile', error);
        return null;
    }

    return data;
}

/**
 * Create a host profile after signup
 * This should be called after successful authentication
 * @param {string} name - Host's name
 * @param {string} email - Host's email
 * @returns {Promise<object|null>}
 */
async function createHostProfile(name, email) {
    const supabase = getSupabaseClient();
    if (!supabase) return null;

    const userId = await getCurrentUserId();
    if (!userId) {
        window.Logger.error('AUTH', 'No authenticated user found');
        return null;
    }

    const { data, error } = await supabase
        .from('hosts')
        .insert([
            {
                id: userId, // Must match auth.users.id
                name: name,
                email: email,
                active_forms_count: 0
            }
        ])
        .select()
        .single();

    if (error) {
        window.Logger.error('AUTH', 'Error creating host profile', error);
        return null;
    }

    return data;
}

/**
 * Update the current host's profile
 * @param {object} updates - Fields to update (name, email, etc.)
 * @returns {Promise<object|null>}
 */
async function updateHostProfile(updates) {
    const supabase = getSupabaseClient();
    if (!supabase) return null;

    const userId = await getCurrentUserId();
    if (!userId) return null;

    // RLS ensures user can only update their own profile
    const { data, error } = await supabase
        .from('hosts')
        .update(updates)
        .eq('id', userId)
        .select()
        .single();

    if (error) {
        window.Logger.error('AUTH', 'Error updating host profile', error);
        return null;
    }

    return data;
}

// ============================================
// AUTH STATE LISTENER
// ============================================

/**
 * Listen for auth state changes
 * @param {function} callback - Called when auth state changes
 */
function onAuthStateChange(callback) {
    const supabase = getSupabaseClient();
    if (!supabase) return;

    supabase.auth.onAuthStateChange((event, session) => {
        callback(event, session);
    });
}

// ============================================
// EXPORT FOR USE IN OTHER FILES
// ============================================
window.AuthUtils = {
    checkAuth,
    requireAuth,
    getCurrentUserId,
    getCurrentUserEmail,
    signOut,
    getCurrentHostProfile,
    createHostProfile,
    updateHostProfile,
    onAuthStateChange,
    getSupabaseClient
};
