/**
 * API Service
 * 
 * Centralized API communication with built-in rate limiting and error handling.
 * Follows Design Principle #2 (Service Pattern), #5 (Async Operations), #9 (Rate Limiting)
 * 
 * Usage:
 *   const apiService = CONFIG.getService('api');
 *   const result = await apiService.registerObserver(data);
 * 
 * Attribution: This project uses the services of Claude and Anthropic PBC.
 */

class APIService {
    constructor() {
        this.baseUrl = null;
        this.debugService = null;
        this.rateLimitMap = new Map();
        this.defaultTimeout = 30000; // 30 seconds
        
        // Rate limit configuration (requests per minute)
        this.rateLimits = {
            'register': { limit: 10, window: 60000 },
            'observe': { limit: 20, window: 60000 },
            'stats': { limit: 30, window: 60000 },
            'default': { limit: 15, window: 60000 }
        };
        
        // Initialize when ready
        this.initialize();
    }
    
    /**
     * Initialize service - get dependencies from service registry
     */
    initialize() {
        try {
            this.baseUrl = CONFIG.getApiUrl();
            this.debugService = CONFIG.getService('debug');
            this.debugService.log(`✓ API Service initialized: ${this.baseUrl}`, 'success');
        } catch (error) {
            console.error('API Service initialization error:', error);
        }
    }
    
    /**
     * Check rate limit for an endpoint
     * @param {string} endpoint - Endpoint identifier
     * @returns {boolean} True if within rate limit
     */
    checkRateLimit(endpoint) {
        const config = this.rateLimits[endpoint] || this.rateLimits.default;
        const now = Date.now();
        
        if (!this.rateLimitMap.has(endpoint)) {
            this.rateLimitMap.set(endpoint, []);
        }
        
        const requests = this.rateLimitMap.get(endpoint);
        
        // Remove expired requests
        const validRequests = requests.filter(time => now - time < config.window);
        
        // Check if under limit
        if (validRequests.length >= config.limit) {
            const oldestRequest = Math.min(...validRequests);
            const waitTime = Math.ceil((config.window - (now - oldestRequest)) / 1000);
            
            this.debugService.log(
                `⚠️ Rate limit reached for ${endpoint}. Wait ${waitTime}s`, 
                'warning'
            );
            return false;
        }
        
        // Add current request
        validRequests.push(now);
        this.rateLimitMap.set(endpoint, validRequests);
        
        return true;
    }
    
    /**
     * Make HTTP request with error handling and rate limiting
     * @param {string} endpoint - API endpoint
     * @param {Object} options - Fetch options
     * @param {string} rateLimitKey - Key for rate limiting
     * @returns {Promise<Object>} Response data
     */
    async request(endpoint, options = {}, rateLimitKey = 'default') {
        // Check rate limit
        if (!this.checkRateLimit(rateLimitKey)) {
            throw new Error('Rate limit exceeded. Please wait before retrying.');
        }
        
        const url = CONFIG.getApiEndpoint(endpoint);
        
        this.debugService.log(`📡 Request: ${options.method || 'GET'} ${url}`, 'info');
        
        // Set default headers
        const headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            ...options.headers
        };
        
        // Create abort controller for timeout
        const controller = new AbortController();
        const timeout = setTimeout(
            () => controller.abort(), 
            options.timeout || this.defaultTimeout
        );
        
        try {
            const response = await fetch(url, {
                ...options,
                headers,
                signal: controller.signal
            });
            
            clearTimeout(timeout);
            
            // Parse response
            const data = await response.json();
            
            if (!response.ok) {
                this.debugService.log(
                    `❌ API Error: ${response.status} - ${data.detail || data.error}`, 
                    'error'
                );
                throw new Error(data.detail || data.error || `HTTP ${response.status}`);
            }
            
            this.debugService.log(`✅ Response received successfully`, 'success');
            return data;
            
        } catch (error) {
            clearTimeout(timeout);
            
            if (error.name === 'AbortError') {
                this.debugService.log('⏱️ Request timeout', 'error');
                throw new Error('Request timeout. Please try again.');
            }
            
            this.debugService.log(`💥 Request failed: ${error.message}`, 'error');
            throw error;
        }
    }
    
    /**
     * Register a new observer (steward or device)
     * @param {Object} observerData - Observer registration data
     * @returns {Promise<Object>} Registration response
     */
    async registerObserver(observerData) {
        this.debugService.log(
            `📝 Registering observer: ${observerData.observer_type}`, 
            'info'
        );
        
        return await this.request(
            'observers/register',
            {
                method: 'POST',
                body: JSON.stringify(observerData)
            },
            'register'
        );
    }
    
    /**
     * Submit an observation
     * @param {Object} observationData - Observation data
     * @returns {Promise<Object>} Submission response
     */
    async submitObservation(observationData) {
        return await this.request(
            'observe',
            {
                method: 'POST',
                body: JSON.stringify(observationData)
            },
            'observe'
        );
    }
    
    /**
     * Get system statistics
     * @returns {Promise<Object>} System stats
     */
    async getSystemStats() {
        return await this.request(
            'system/stats',
            { method: 'GET' },
            'stats'
        );
    }
    
    /**
     * Health check
     * @returns {Promise<Object>} Health status
     */
    async healthCheck() {
        try {
            const response = await fetch(`${this.baseUrl}/api/v2/health`);
            return {
                healthy: response.ok,
                status: response.status
            };
        } catch (error) {
            return {
                healthy: false,
                error: error.message
            };
        }
    }
    
    /**
     * Test API connection
     * @returns {Promise<boolean>} Connection status
     */
    async testConnection() {
        this.debugService.log(`🔌 Testing API connection...`, 'info');
        
        try {
            const health = await this.healthCheck();
            
            if (health.healthy) {
                this.debugService.log(`✅ API is healthy!`, 'success');
                return true;
            } else {
                this.debugService.log(
                    `⚠️ API returned status ${health.status}`, 
                    'warning'
                );
                return false;
            }
        } catch (error) {
            this.debugService.log(
                `❌ Cannot reach API: ${error.message}`, 
                'error'
            );
            return false;
        }
    }
}

// Create singleton instance and register with CONFIG
const apiService = new APIService();

// Register service when CONFIG is available
if (typeof CONFIG !== 'undefined') {
    CONFIG.registerService('api', apiService);
    
    // Test connection on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            apiService.testConnection();
        });
    } else {
        apiService.testConnection();
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { APIService, apiService };
}
