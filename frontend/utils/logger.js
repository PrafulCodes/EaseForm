/**
 * Logger Utility
 * Centralizes logging to control verbosity and format.
 * 
 * Levels:
 * - DEBUG: Detailed logs for development (hidden in prod)
 * - INFO: General information (hidden in prod)
 * - WARN: Warnings (visible in prod)
 * - ERROR: Critical errors (visible in prod)
 */

const Logger = {
    // Detect if we are in production based on hostname or protocol
    isProduction: window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1',

    /**
     * Log a debug message (Dev only)
     * @param {string} category - The category of the log (e.g., 'API', 'Auth')
     * @param {string} message - The message to log
     * @param {any} data - Optional data to log
     */
    debug: function (category, message, data = null) {
        if (this.isProduction) return;
        this._log('gray', 'DEBUG', category, message, data);
    },

    /**
     * Log an info message (Dev only)
     */
    info: function (category, message, data = null) {
        if (this.isProduction) return;
        this._log('blue', 'INFO', category, message, data);
    },

    /**
     * Log a warning (Visible in Prod)
     */
    warn: function (category, message, data = null) {
        this._log('orange', 'WARN', category, message, data);
    },

    /**
     * Log an error (Visible in Prod)
     */
    error: function (category, message, data = null) {
        this._log('red', 'ERROR', category, message, data);
    },

    /**
     * Internal log formatter
     */
    _log: function (color, level, category, message, data) {
        const timestamp = new Date().toISOString().split('T')[1].slice(0, 8);
        const prefix = `%c[${timestamp}] [${level}] [${category}]`;
        const style = `color: ${color}; font-weight: bold;`;

        if (data) {
            console.log(prefix, style, message, data);
        } else {
            console.log(prefix, style, message);
        }
    }
};

// Expose to window
window.Logger = Logger;
