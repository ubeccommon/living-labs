/**
 * Debug Service
 * 
 * Centralized debug logging and console management.
 * Follows Design Principle #2 (Service Pattern) and #12 (Method Singularity)
 * 
 * Usage:
 *   const debugService = CONFIG.getService('debug');
 *   debugService.log('Message', 'info');
 * 
 * Attribution: This project uses the services of Claude and Anthropic PBC.
 */

class DebugService {
    constructor() {
        this.messages = [];
        this.maxMessages = 50;
        this.consoleElement = null;
        this.messagesElement = null;
        this.isVisible = false;
        
        // Initialize after DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initialize());
        } else {
            this.initialize();
        }
    }
    
    /**
     * Initialize debug console DOM elements
     */
    initialize() {
        this.consoleElement = document.getElementById('debugConsole');
        this.messagesElement = document.getElementById('debugMessages');
        
        // Set up close button
        const closeBtn = document.getElementById('closeDebug');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.hide());
        }
        
        // Show console if debug mode is enabled
        if (CONFIG.isDebugMode()) {
            this.show();
        }
    }
    
    /**
     * Log a message to the debug console
     * @param {string} message - Message to log
     * @param {string} type - Message type: 'info', 'success', 'error', 'warning'
     */
    log(message, type = 'info') {
        const logLevel = CONFIG.getLogLevel();
        
        // Check if message should be logged based on log level
        const levels = ['debug', 'info', 'warning', 'error'];
        const currentLevelIndex = levels.indexOf(logLevel);
        const messageLevelIndex = levels.indexOf(type === 'success' ? 'info' : type);
        
        if (messageLevelIndex < currentLevelIndex) {
            return; // Skip logging
        }
        
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = {
            timestamp,
            message,
            type
        };
        
        // Add to messages array
        this.messages.push(logEntry);
        
        // Limit message history
        if (this.messages.length > this.maxMessages) {
            this.messages.shift();
        }
        
        // Output to browser console
        const consoleMethod = type === 'error' ? 'error' : 
                            type === 'warning' ? 'warn' : 'log';
        console[consoleMethod](`[${type.toUpperCase()}]`, message);
        
        // Update UI if debug console exists
        if (this.messagesElement && CONFIG.isDebugMode()) {
            this.appendMessage(logEntry);
            this.show();
        }
    }
    
    /**
     * Append message to debug console UI
     * @param {Object} logEntry - Log entry object
     */
    appendMessage(logEntry) {
        if (!this.messagesElement) return;
        
        const colors = {
            error: '#ffcdd2',
            warning: '#fff3e0',
            success: '#c8e6c9',
            info: '#e1f5fe',
            debug: '#f3e5f5'
        };
        
        const color = colors[logEntry.type] || colors.info;
        
        const messageDiv = document.createElement('div');
        messageDiv.style.cssText = `
            background: ${color};
            padding: 2px 5px;
            margin: 2px 0;
            border-radius: 3px;
            font-size: 11px;
        `;
        messageDiv.textContent = `[${logEntry.timestamp}] ${logEntry.message}`;
        
        this.messagesElement.appendChild(messageDiv);
        this.messagesElement.scrollTop = this.messagesElement.scrollHeight;
    }
    
    /**
     * Show debug console
     */
    show() {
        if (this.consoleElement) {
            this.consoleElement.classList.add('active');
            this.isVisible = true;
        }
    }
    
    /**
     * Hide debug console
     */
    hide() {
        if (this.consoleElement) {
            this.consoleElement.classList.remove('active');
            this.isVisible = false;
        }
    }
    
    /**
     * Toggle debug console visibility
     */
    toggle() {
        if (this.isVisible) {
            this.hide();
        } else {
            this.show();
        }
    }
    
    /**
     * Clear all messages
     */
    clear() {
        this.messages = [];
        if (this.messagesElement) {
            this.messagesElement.innerHTML = '';
        }
    }
    
    /**
     * Get all log messages
     * @returns {Array} Array of log entries
     */
    getMessages() {
        return [...this.messages];
    }
    
    /**
     * Export logs as text
     * @returns {string} Formatted log text
     */
    exportLogs() {
        return this.messages
            .map(entry => `[${entry.timestamp}] [${entry.type.toUpperCase()}] ${entry.message}`)
            .join('\n');
    }
}

// Create singleton instance and register with CONFIG
const debugService = new DebugService();

// Register service when CONFIG is available
if (typeof CONFIG !== 'undefined') {
    CONFIG.registerService('debug', debugService);
} else {
    // Wait for CONFIG to be available
    document.addEventListener('DOMContentLoaded', () => {
        if (typeof CONFIG !== 'undefined') {
            CONFIG.registerService('debug', debugService);
        }
    });
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DebugService, debugService };
}
