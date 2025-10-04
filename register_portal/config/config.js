/**
 * Configuration Module
 * 
 * Single source of truth for all application configuration.
 * Follows Design Principle #4 (Single Source of Truth) and #8 (No Duplicate Configuration)
 * 
 * Usage:
 *   import { CONFIG } from './config/config.js';
 *   const apiUrl = CONFIG.getApiUrl();
 * 
 * Attribution: This project uses the services of Claude and Anthropic PBC.
 */

// Environment detection
const ENVIRONMENT = {
    DEVELOPMENT: 'development',
    STAGING: 'staging',
    PRODUCTION: 'production'
};

// Determine current environment
const getCurrentEnvironment = () => {
    const hostname = window.location.hostname;
    
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return ENVIRONMENT.DEVELOPMENT;
    } else if (hostname.includes('staging')) {
        return ENVIRONMENT.STAGING;
    }
    return ENVIRONMENT.PRODUCTION;
};

// Environment-specific configurations
const ENV_CONFIG = {
    [ENVIRONMENT.DEVELOPMENT]: {
        API_HOST: '92.205.28.58',
        API_PORT: '8000',
        DEBUG_MODE: true,
        LOG_LEVEL: 'debug',
        ENABLE_MOCK: false
    },
    [ENVIRONMENT.STAGING]: {
        API_HOST: 'staging-api.ubec-living-science.org',
        API_PORT: '443',
        DEBUG_MODE: true,
        LOG_LEVEL: 'info',
        ENABLE_MOCK: false
    },
    [ENVIRONMENT.PRODUCTION]: {
        API_HOST: 'api.ubec-living-science.org',
        API_PORT: '443',
        DEBUG_MODE: false,
        LOG_LEVEL: 'error',
        ENABLE_MOCK: false
    }
};

// Application constants (environment-independent)
const APP_CONSTANTS = {
    // API Configuration
    API_VERSION: 'v2',
    API_TIMEOUT: 30000, // 30 seconds
    
    // Observation intervals
    OBSERVATION_INTERVAL: 900000, // 15 minutes in milliseconds
    
    // Form validation
    STELLAR_ADDRESS_PATTERN: /^G[A-Z2-7]{55}$/,
    EMAIL_PATTERN: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    
    // Sensor configurations
    SENSOR_CATEGORIES: {
        ENVIRONMENTAL: 'environmental',
        SOIL_WATER: 'soil_water',
        AIR_QUALITY: 'air_quality',
        WEATHER: 'weather'
    },
    
    // Default timezone
    DEFAULT_TIMEZONE: 'Europe/Berlin',
    
    // Attribution
    ATTRIBUTION: 'This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.'
};

// Main configuration class
class Configuration {
    constructor() {
        this.env = getCurrentEnvironment();
        this.config = ENV_CONFIG[this.env];
        this._serviceRegistry = new Map();
        
        // Log environment on initialization
        if (this.config.DEBUG_MODE) {
            console.log(`🔧 Configuration initialized for: ${this.env}`);
        }
    }
    
    /**
     * Get full API base URL
     * @returns {string} Complete API base URL
     */
    getApiUrl() {
        const protocol = this.config.API_PORT === '443' ? 'https' : 'http';
        return `${protocol}://${this.config.API_HOST}:${this.config.API_PORT}`;
    }
    
    /**
     * Get API endpoint for a specific version
     * @param {string} endpoint - Endpoint path
     * @returns {string} Full API endpoint URL
     */
    getApiEndpoint(endpoint) {
        const base = this.getApiUrl();
        const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
        return `${base}/api/${APP_CONSTANTS.API_VERSION}/${cleanEndpoint}`;
    }
    
    /**
     * Check if debug mode is enabled
     * @returns {boolean}
     */
    isDebugMode() {
        return this.config.DEBUG_MODE;
    }
    
    /**
     * Get log level
     * @returns {string}
     */
    getLogLevel() {
        return this.config.LOG_LEVEL;
    }
    
    /**
     * Get environment name
     * @returns {string}
     */
    getEnvironment() {
        return this.env;
    }
    
    /**
     * Get application constant
     * @param {string} key - Constant key
     * @returns {*} Constant value
     */
    getConstant(key) {
        return APP_CONSTANTS[key];
    }
    
    /**
     * Check if stellar address is valid
     * @param {string} address - Stellar address to validate
     * @returns {boolean}
     */
    isValidStellarAddress(address) {
        return APP_CONSTANTS.STELLAR_ADDRESS_PATTERN.test(address);
    }
    
    /**
     * Check if email is valid
     * @param {string} email - Email to validate
     * @returns {boolean}
     */
    isValidEmail(email) {
        return APP_CONSTANTS.EMAIL_PATTERN.test(email);
    }
    
    /**
     * Service Registry Methods (Design Principle #3)
     * Register a service in the central registry
     */
    registerService(name, service) {
        if (this._serviceRegistry.has(name)) {
            console.warn(`⚠️ Service '${name}' is being overwritten`);
        }
        this._serviceRegistry.set(name, service);
        
        if (this.isDebugMode()) {
            console.log(`✓ Service registered: ${name}`);
        }
    }
    
    /**
     * Get a service from the registry
     * @param {string} name - Service name
     * @returns {*} Service instance
     */
    getService(name) {
        if (!this._serviceRegistry.has(name)) {
            throw new Error(`Service '${name}' not found in registry`);
        }
        return this._serviceRegistry.get(name);
    }
    
    /**
     * Check if service is registered
     * @param {string} name - Service name
     * @returns {boolean}
     */
    hasService(name) {
        return this._serviceRegistry.has(name);
    }
}

// Create and export singleton instance
const CONFIG = new Configuration();

// Make CONFIG available globally
window.CONFIG = CONFIG;

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CONFIG, ENVIRONMENT, APP_CONSTANTS };
}
