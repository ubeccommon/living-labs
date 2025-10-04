/**
 * Main Application Orchestrator
 * 
 * Single entry point for the application - initializes all components and manages navigation.
 * Follows Design Principle #2 (Service Pattern with Centralized Execution)
 * 
 * This is the ONLY file that executes code directly. All other modules expose services
 * through the service registry.
 * 
 * Attribution: This project uses the services of Claude and Anthropic PBC.
 */

class Application {
    constructor() {
        this.currentTab = 'steward';
        this.components = {};
        this.initialized = false;
    }
    
    /**
     * Initialize the application
     * This is the single entry point for all initialization
     */
    async init() {
        if (this.initialized) {
            console.warn('Application already initialized');
            return;
        }
        
        try {
            console.log('🌱 Environmental Stewardship Portal');
            console.log(`Attribution: ${CONFIG.getConstant('ATTRIBUTION')}`);
            
            // Wait for DOM to be ready
            if (document.readyState === 'loading') {
                await new Promise(resolve => {
                    document.addEventListener('DOMContentLoaded', resolve);
                });
            }
            
            // Initialize all components
            this.initializeComponents();
            
            // Set up navigation
            this.setupNavigation();
            
            // Test API connection
            await this.testAPIConnection();
            
            this.initialized = true;
            
            const debugService = CONFIG.getService('debug');
            debugService.log('✅ Application initialized successfully', 'success');
            
        } catch (error) {
            console.error('💥 Application initialization failed:', error);
        }
    }
    
    /**
     * Initialize all components
     */
    initializeComponents() {
        // Initialize form components
        if (typeof stewardFormComponent !== 'undefined') {
            stewardFormComponent.initialize();
            this.components.steward = stewardFormComponent;
        }
        
        if (typeof senseboxFormComponent !== 'undefined') {
            senseboxFormComponent.initialize();
            this.components.sensebox = senseboxFormComponent;
        }
        
        if (typeof statusComponent !== 'undefined') {
            statusComponent.initialize();
            this.components.status = statusComponent;
        }
        
        const debugService = CONFIG.getService('debug');
        debugService.log(`✓ Initialized ${Object.keys(this.components).length} components`, 'info');
    }
    
    /**
     * Set up navigation between tabs
     */
    setupNavigation() {
        const navTabs = document.querySelectorAll('.nav-tab');
        
        navTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                const tabName = tab.getAttribute('data-tab');
                this.switchTab(tabName);
            });
        });
    }
    
    /**
     * Switch between tabs
     * @param {string} tabName - Name of tab to switch to
     */
    switchTab(tabName) {
        if (this.currentTab === tabName) {
            return; // Already on this tab
        }
        
        const debugService = CONFIG.getService('debug');
        debugService.log(`Switching to tab: ${tabName}`, 'info');
        
        // Update navigation tabs
        document.querySelectorAll('.nav-tab').forEach(t => {
            t.classList.remove('active');
            if (t.getAttribute('data-tab') === tabName) {
                t.classList.add('active');
            }
        });
        
        // Hide all form sections
        document.querySelectorAll('.form-section').forEach(f => {
            f.classList.remove('active');
        });
        
        // Show selected form section
        const targetSection = document.getElementById(`${tabName}-form`);
        if (targetSection) {
            targetSection.classList.add('active');
        }
        
        // Notify component about visibility change
        if (this.currentTab && this.components[this.currentTab] && 
            typeof this.components[this.currentTab].hide === 'function') {
            this.components[this.currentTab].hide();
        }
        
        if (this.components[tabName] && typeof this.components[tabName].show === 'function') {
            this.components[tabName].show();
        }
        
        this.currentTab = tabName;
    }
    
    /**
     * Test API connection on startup
     */
    async testAPIConnection() {
        const apiService = CONFIG.getService('api');
        const debugService = CONFIG.getService('debug');
        
        debugService.log('🔌 Testing API connection...', 'info');
        
        try {
            const isHealthy = await apiService.testConnection();
            
            if (!isHealthy) {
                this.showAPIWarning();
            }
        } catch (error) {
            debugService.log(`⚠️ API connection test failed: ${error.message}`, 'warning');
            this.showAPIWarning();
        }
    }
    
    /**
     * Show API connection warning
     */
    showAPIWarning() {
        const warning = document.createElement('div');
        warning.className = 'status-message warning active';
        warning.style.cssText = 'position: fixed; top: 80px; left: 50%; transform: translateX(-50%); z-index: 1000; max-width: 600px;';
        warning.innerHTML = `
            <strong>⚠️ API Connection Issue</strong><br>
            Unable to connect to the API server at ${CONFIG.getApiUrl()}. 
            Please check your connection or contact support.
        `;
        
        document.body.appendChild(warning);
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            warning.style.transition = 'opacity 0.5s';
            warning.style.opacity = '0';
            setTimeout(() => warning.remove(), 500);
        }, 10000);
    }
    
    /**
     * Handle global keyboard shortcuts
     * @param {KeyboardEvent} e - Keyboard event
     */
    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + D to toggle debug console
        if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
            e.preventDefault();
            const debugService = CONFIG.getService('debug');
            debugService.toggle();
        }
        
        // Escape to clear any active modals or close debug console
        if (e.key === 'Escape') {
            const debugService = CONFIG.getService('debug');
            if (debugService.isVisible) {
                debugService.hide();
            }
        }
    }
    
    /**
     * Clean up resources
     */
    destroy() {
        // Stop any running intervals
        if (this.components.status) {
            this.components.status.stopAutoRefresh();
        }
        
        // Remove event listeners
        document.removeEventListener('keydown', this.handleKeyboardShortcuts);
        
        this.initialized = false;
    }
}

// ==========================================
// APPLICATION BOOTSTRAP
// This is the ONLY code that executes immediately
// ==========================================

// Create application instance
const app = new Application();

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        app.init();
    });
} else {
    app.init();
}

// Set up keyboard shortcuts
document.addEventListener('keydown', (e) => app.handleKeyboardShortcuts(e));

// Make app available globally for debugging
window.app = app;

// Handle page unload
window.addEventListener('beforeunload', () => {
    app.destroy();
});

// Console signature
console.log('%c' + 
    '╔══════════════════════════════════════════════════════════╗\n' +
    '║  🌱 Environmental Stewardship Portal                     ║\n' +
    '║  Living Science Initiative                               ║\n' +
    '║  Freie Waldorfschule Frankfurt (Oder)                    ║\n' +
    '║                                                          ║\n' +
    '║  Attribution: This project uses the services of          ║\n' +
    '║  Claude and Anthropic PBC                                ║\n' +
    '╚══════════════════════════════════════════════════════════╝',
    'color: #4CAF50; font-family: monospace; font-size: 12px;'
);

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { Application, app };
}
