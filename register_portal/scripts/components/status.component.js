/**
 * Status Component
 * 
 * Displays system statistics and network status.
 * Follows Design Principle #1 (Modular Design) and #10 (Separation of Concerns)
 * 
 * Attribution: This project uses the services of Claude and Anthropic PBC.
 */

class StatusComponent {
    constructor() {
        this.debugService = null;
        this.apiService = null;
        this.loadingElement = null;
        this.contentElement = null;
        this.refreshInterval = null;
        this.autoRefreshDelay = 30000; // 30 seconds
    }
    
    /**
     * Initialize component
     */
    initialize() {
        this.debugService = CONFIG.getService('debug');
        this.apiService = CONFIG.getService('api');
        this.render();
    }
    
    /**
     * Render component HTML
     */
    render() {
        const html = `
            <div class="form-header">
                <div class="form-icon">📊</div>
                <div class="form-title">
                    <h3>Network Status</h3>
                    <p>Current state of the stewardship network and phenomenological observations</p>
                </div>
            </div>

            <div class="loading" id="status-loading">
                <div class="spinner"></div>
                <p>Checking network awareness...</p>
            </div>

            <div id="status-content"></div>
        `;
        
        const container = document.getElementById('formContainer');
        const section = document.createElement('div');
        section.id = 'status-form';
        section.className = 'form-section';
        section.innerHTML = html;
        container.appendChild(section);
        
        this.loadingElement = document.getElementById('status-loading');
        this.contentElement = document.getElementById('status-content');
    }
    
    /**
     * Load and display system statistics
     */
    async loadStats() {
        if (!this.loadingElement || !this.contentElement) return;
        
        this.loadingElement.classList.add('active');
        this.contentElement.innerHTML = '';
        
        try {
            const data = await this.apiService.getSystemStats();
            this.displayStats(data);
            this.debugService.log('✅ System stats loaded', 'success');
        } catch (error) {
            this.displayError(error.message);
            this.debugService.log(`❌ Failed to load stats: ${error.message}`, 'error');
        } finally {
            this.loadingElement.classList.remove('active');
        }
    }
    
    /**
     * Display statistics
     * @param {Object} data - System statistics data
     */
    displayStats(data) {
        const html = `
            <div style="padding: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h4 style="color: var(--deep-green); margin: 0;">System Statistics</h4>
                    <button class="btn btn-sm btn-secondary" onclick="statusComponent.loadStats()">
                        🔄 Refresh
                    </button>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
                    <div style="background: var(--light-bg); padding: 1rem; border-radius: var(--radius-md);">
                        <div style="font-size: 2rem; color: var(--primary-green); font-weight: bold;">
                            ${data.total_observers || 0}
                        </div>
                        <div style="color: var(--text-light);">Registered Observers</div>
                    </div>
                    <div style="background: var(--light-bg); padding: 1rem; border-radius: var(--radius-md);">
                        <div style="font-size: 2rem; color: var(--primary-green); font-weight: bold;">
                            ${data.total_observations || 0}
                        </div>
                        <div style="color: var(--text-light);">Total Observations</div>
                    </div>
                    <div style="background: var(--light-bg); padding: 1rem; border-radius: var(--radius-md);">
                        <div style="font-size: 2rem; color: var(--primary-green); font-weight: bold;">
                            ${data.active_patterns || 0}
                        </div>
                        <div style="color: var(--text-light);">Active Patterns</div>
                    </div>
                </div>
                
                ${this.renderDetailedStats(data)}
                
                <div style="margin-top: 2rem; padding: 1rem; background: rgba(76, 175, 80, 0.05); border-radius: var(--radius-md); border-left: 4px solid var(--primary-green);">
                    <p style="margin: 0; color: var(--text-light); font-size: 0.875rem;">
                        <strong>Last Updated:</strong> ${new Date().toLocaleString()}<br>
                        <strong>Environment:</strong> ${CONFIG.getEnvironment()}<br>
                        <strong>API Endpoint:</strong> ${CONFIG.getApiUrl()}
                    </p>
                </div>
            </div>
        `;
        
        this.contentElement.innerHTML = html;
    }
    
    /**
     * Render detailed statistics if available
     * @param {Object} data - Statistics data
     * @returns {string} HTML for detailed stats
     */
    renderDetailedStats(data) {
        if (!data.observers_by_type && !data.recent_activity) {
            return '';
        }
        
        let html = '<div style="margin-top: 2rem;">';
        
        // Observer breakdown
        if (data.observers_by_type) {
            html += `
                <h5 style="color: var(--deep-green); margin-bottom: 1rem;">Observer Types</h5>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 0.75rem; margin-bottom: 2rem;">
            `;
            
            for (const [type, count] of Object.entries(data.observers_by_type)) {
                const icon = type === 'human' ? '🌍' : '📡';
                html += `
                    <div style="background: var(--white); padding: 0.75rem; border-radius: var(--radius-md); border: 1px solid var(--border);">
                        <div style="font-size: 1.5rem;">${icon}</div>
                        <div style="font-size: 1.25rem; font-weight: 600; color: var(--primary-green);">${count}</div>
                        <div style="font-size: 0.875rem; color: var(--text-light); text-transform: capitalize;">${type}</div>
                    </div>
                `;
            }
            
            html += '</div>';
        }
        
        // Recent activity
        if (data.recent_activity && data.recent_activity.length > 0) {
            html += `
                <h5 style="color: var(--deep-green); margin-bottom: 1rem;">Recent Activity</h5>
                <div style="background: var(--white); border-radius: var(--radius-md); overflow: hidden; border: 1px solid var(--border);">
            `;
            
            data.recent_activity.slice(0, 5).forEach((activity, index) => {
                html += `
                    <div style="padding: 0.75rem; ${index > 0 ? 'border-top: 1px solid var(--border);' : ''}">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <div style="font-weight: 500; color: var(--text-dark);">${activity.type || 'Activity'}</div>
                                <div style="font-size: 0.875rem; color: var(--text-light);">${activity.description || 'No description'}</div>
                            </div>
                            <div style="font-size: 0.75rem; color: var(--text-light); white-space: nowrap;">
                                ${new Date(activity.timestamp).toLocaleString()}
                            </div>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
        }
        
        html += '</div>';
        return html;
    }
    
    /**
     * Display error message
     * @param {string} message - Error message
     */
    displayError(message) {
        const html = `
            <div class="status-message error active">
                <strong>Failed to load system status</strong><br>
                ${message}
            </div>
            <div style="text-align: center; padding: 2rem;">
                <button class="btn btn-primary" onclick="statusComponent.loadStats()">
                    🔄 Try Again
                </button>
            </div>
        `;
        
        this.contentElement.innerHTML = html;
    }
    
    /**
     * Start auto-refresh
     */
    startAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        
        this.refreshInterval = setInterval(() => {
            // Only refresh if status tab is active
            const statusForm = document.getElementById('status-form');
            if (statusForm && statusForm.classList.contains('active')) {
                this.loadStats();
            }
        }, this.autoRefreshDelay);
    }
    
    /**
     * Stop auto-refresh
     */
    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
    
    /**
     * Show component (called when tab is activated)
     */
    show() {
        this.loadStats();
        // this.startAutoRefresh(); // Uncomment to enable auto-refresh
    }
    
    /**
     * Hide component (called when tab is deactivated)
     */
    hide() {
        this.stopAutoRefresh();
    }
}

// Create and export instance
const statusComponent = new StatusComponent();

// Make available globally
window.statusComponent = statusComponent;

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { StatusComponent, statusComponent };
}
