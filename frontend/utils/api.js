/**
 * API Service Layer for EaseForm
 * Centralized API client for all backend communication
 */

// ============================================
// API CLIENT - UPDATED
// ============================================

var API = (function () {
    // In-flight requests for deduplication
    var inFlightRequests = new Map();

    /**
     * Stale-While-Revalidate Helper
     * @param {string} cacheKey - Key for caching
     * @param {Function} fetchPromise - Function returning a promise for fresh data
     * @param {number} ttl - TTL in milliseconds
     * @param {Function} onUpdate - Optional callback for silent updates
     */
    async function fetchWithSWR(cacheKey, fetchPromise, ttl, onUpdate) {
        // 1. Check Cache
        var entry = window.CacheUtils.getEntry(cacheKey);
        var now = Date.now();
        var isStale = !entry || entry.expiry < now;

        // 2. If valid cache exists, return immediately (No network)
        if (entry && !isStale) {
            window.Logger.debug('SWR', 'Cache Hit (Valid)', cacheKey);
            return entry.data;
        }

        // 3. Prepare Fetch (Deduplicated)
        var fetchAction = async function () {
            try {
                // Check if already in flight
                if (inFlightRequests.has(cacheKey)) {
                    window.Logger.debug('SWR', 'Deduping request', cacheKey);
                    return inFlightRequests.get(cacheKey);
                }

                // Create new request
                window.Logger.debug('SWR', 'Fetching fresh', cacheKey);
                var promise = fetchPromise().then(function (data) {
                    window.CacheUtils.set(cacheKey, data, ttl);
                    inFlightRequests.delete(cacheKey);
                    return data;
                }).catch(function (err) {
                    inFlightRequests.delete(cacheKey);
                    throw err;
                });

                inFlightRequests.set(cacheKey, promise);
                return promise;
            } catch (e) {
                inFlightRequests.delete(cacheKey);
                throw e;
            }
        };

        // 4. Handle Stale/Missing Scenarios
        if (entry) {
            // Cache exists but is stale -> Return stale immediately, fetch in background
            window.Logger.debug('SWR', 'Cache Hit (Stale) - Revalidating', cacheKey);

            // Trigger background fetch
            fetchAction().then(function (freshData) {
                // If data changed and callback provided
                if (onUpdate && JSON.stringify(freshData) !== JSON.stringify(entry.data)) {
                    window.Logger.info('SWR', 'Data updated silently', cacheKey);
                    onUpdate(freshData);
                }
            }).catch(function (err) {
                window.Logger.warn('SWR', 'Background revalidation failed', { key: cacheKey, error: err });
            });

            return entry.data;
        } else {
            // No cache -> Must await fetch
            window.Logger.debug('SWR', 'Cache Miss - Awaiting fetch', cacheKey);
            return await fetchAction();
        }
    }

    // ============================================
    // BASE API REQUEST
    // ============================================

    var baseURL = window.API_BASE_URL;
    if (!baseURL) {
        window.Logger.error('API', 'API_BASE_URL not defined', 'Check config.js generation');
        throw new Error('Configuration Missing: API_BASE_URL is not defined.');
    }

    // Client should be ready if loaded in correct order
    var supabaseClient = window.supabaseClient;

    /**
     * Get current user's JWT token
     */
    async function getAuthToken() {
        if (!supabaseClient) {
            throw new Error('Supabase client not initialized');
        }

        var session = await supabaseClient.auth.getSession();
        if (!session.data.session) {
            throw new Error('No active session');
        }

        return session.data.session.access_token;
    }

    /**
     * Make authenticated API request
     */
    async function request(endpoint, options) {
        options = options || {};

        var url = baseURL + endpoint;
        var headers = options.headers || {};

        // Add auth token if required
        if (options.auth !== false) {
            try {
                var token = await getAuthToken();
                headers['Authorization'] = 'Bearer ' + token;
            } catch (error) {
                window.Logger.error('API', 'Auth error', error);
                throw error;
            }
        }

        // Add content type for JSON
        if (options.body && typeof options.body === 'object') {
            headers['Content-Type'] = 'application/json';
            options.body = JSON.stringify(options.body);
        }

        var config = {
            method: options.method || 'GET',
            headers: headers
        };

        if (options.body) {
            config.body = options.body;
        }

        try {
            // Setup timeout
            var controller = new AbortController();
            var timeoutId = setTimeout(function () { controller.abort(); }, 60000); // 60s timeout for Render cold starts
            config.signal = controller.signal;

            var response = await fetch(url, config);
            clearTimeout(timeoutId);

            // Handle non-JSON responses
            var contentType = response.headers.get('content-type');
            var data;

            if (contentType && contentType.includes('application/json')) {
                data = await response.json();
            } else {
                data = await response.text();
            }

            if (!response.ok) {
                throw {
                    status: response.status,
                    message: data.detail || data.message || data,
                    data: data
                };
            }

            return data;

        } catch (error) {
            if (error.name === 'AbortError') {
                window.Logger.error('API', 'Request timed out', url);
                throw new Error('Request timed out. Please check your connection.');
            }
            window.Logger.error('API', 'Request failed', error);
            throw error;
        }
    }

    // ============================================
    // FORMS API
    // ============================================

    var forms = {
        /**
         * Create a new form
         */
        create: async function (formData) {
            var result = await request('/forms', {
                method: 'POST',
                body: formData
            });
            // Invalidate forms list
            window.CacheUtils.invalidate('forms_list');
            return result;
        },

        /**
         * Get all forms for current user
         */
        /**
         * Get all forms for current user
         * @param {Function} onUpdate - Optional callback for silent updates
         */
        list: async function (onUpdate) {
            return await fetchWithSWR(
                'forms_list',
                async function () { return await request('/forms'); },
                window.CacheUtils.TTL.FORMS_LIST,
                onUpdate
            );
        },

        /**
         * Get a specific form by ID (Private/Host)
         * @param {string} formId
         * @param {Function} onUpdate - Optional callback for silent updates
         */
        get: async function (formId, onUpdate) {
            return await fetchWithSWR(
                'form_' + formId,
                async function () { return await request('/forms/' + formId); },
                window.CacheUtils.TTL.FORM_DETAILS,
                onUpdate
            );
        },

        /**
         * Get a public form by ID (Public/Respondent)
         * @param {string} formId
         * @param {Function} onUpdate - Optional callback for silent updates
         */
        getPublic: async function (formId, onUpdate) {
            return await fetchWithSWR(
                'public_form_' + formId,
                async function () {
                    return await request('/public/forms/' + formId, { auth: false });
                },
                window.CacheUtils.TTL.FORM_DETAILS,
                onUpdate
            );
        },

        /**
         * Update a form
         */
        update: async function (formId, formData) {
            var result = await request('/forms/' + formId, {
                method: 'PUT',
                body: formData
            });
            // Invalidate specific form and list
            window.CacheUtils.invalidate('form_' + formId);
            window.CacheUtils.invalidate('forms_list');
            return result;
        },

        /**
         * Stop receiving responses for a form (One-way)
         */
        stop: async function (formId) {
            var result = await request('/forms/' + formId + '/stop', {
                method: 'PATCH'
            });
            // Invalidate specific form and list
            window.CacheUtils.invalidate('form_' + formId);
            window.CacheUtils.invalidate('forms_list');
            return result;
        },

        /**
         * Delete a form (Deprecated/Admin only)
         * Kept for backward compatibility but UI should use stop()
         */
        delete: async function (formId) {
            var result = await request('/forms/' + formId, {
                method: 'DELETE'
            });
            window.CacheUtils.invalidate('form_' + formId);
            window.CacheUtils.invalidate('forms_list');
            return result;
        }
    };

    // ============================================
    // RESPONSES API
    // ============================================

    var responses = {
        /**
         * Submit a response to a form
         */
        submit: async function (formId, answers) {
            var result = await request('/forms/' + formId + '/responses', {
                method: 'POST',
                body: { answers: answers },
                auth: false  // Public endpoint
            });

            // Invalidate responses cache if exists (useful for host testing)
            window.CacheUtils.invalidate('responses_' + formId);

            return result;
        },

        /**
         * Get all responses for a form (owner only)
         * @param {string} formId
         * @param {Function} onUpdate - Optional callback for silent updates
         */
        list: async function (formId, onUpdate) {
            return await fetchWithSWR(
                'responses_' + formId,
                async function () { return await request('/forms/' + formId + '/responses'); },
                window.CacheUtils.TTL.RESPONSES,
                onUpdate
            );
        },

        /**
         * Delete a response
         */
        delete: async function (responseId) {
            var result = await request('/responses/' + responseId, {
                method: 'DELETE'
            });
            // Need to invalidate specific response list. 
            // Issue: We don't have formId here efficiently. 
            // Strategy: Invalidate all response lists? Or Pattern?
            // "responses_"
            window.CacheUtils.invalidatePattern(/^responses_/);
            return result;
        }
    };

    // ============================================
    // USER API
    // ============================================

    var user = {
        /**
         * Get current user profile (Cached)
         * @param {Function} onUpdate - Optional callback for silent updates
         */
        getProfile: async function (onUpdate) {
            return await fetchWithSWR(
                'user_profile',
                async function () {
                    // Fetch from Supabase Auth
                    var session = await supabaseClient.auth.getSession();
                    var currentUser = session.data.session?.user;

                    if (!currentUser) {
                        throw new Error('No active session');
                    }

                    // Construct profile logic
                    return {
                        id: currentUser.id,
                        email: currentUser.email,
                        name: currentUser.user_metadata?.full_name || currentUser.email.split('@')[0],
                        initial: (currentUser.user_metadata?.full_name || currentUser.email).charAt(0).toUpperCase()
                    };
                },
                window.CacheUtils.TTL.USER_PROFILE,
                onUpdate
            );
        }
    };

    // ============================================
    // PUBLIC API
    // ============================================

    window.Logger.info('API', 'Service Initialized', Object.keys(forms));

    return {
        forms: forms,
        responses: responses,
        user: user,
        request: request
    };
})();

// Export to window
window.API = API;
