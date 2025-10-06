/**
 * Stellar Wallet Creation Component
 * 
 * Guides users through creating a Stellar wallet if they don't have one
 * Follows Design Principle #12 (Method Singularity)
 * 
 * Attribution: This project uses the services of Claude and Anthropic PBC.
 */

class StellarWalletCreator {
    constructor(containerId, apiService, debugService) {
        this.containerId = containerId;
        this.apiService = apiService;
        this.debugService = debugService;
        this.currentStep = 'initial';
        this.walletData = null;
    }
    
    /**
     * Initialize the wallet creation interface
     */
    init() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container ${this.containerId} not found`);
            return;
        }
        
        this.render();
        this.attachEventListeners();
    }
    
    /**
     * Render the wallet creation interface
     */
    render() {
        const container = document.getElementById(this.containerId);
        
        const html = `
            <div class="wallet-creator">
                <div class="wallet-creator-header">
                    <h3>🔐 Stellar Wallet Setup</h3>
                    <p>Don't have a Stellar wallet? We'll create one for you!</p>
                </div>
                
                <div id="wallet-creator-content">
                    ${this.renderContent()}
                </div>
            </div>
        `;
        
        container.innerHTML = html;
    }
    
    /**
     * Render content based on current step
     */
    renderContent() {
        switch (this.currentStep) {
            case 'initial':
                return this.renderInitialChoice();
            case 'creating':
                return this.renderCreating();
            case 'success':
                return this.renderSuccess();
            case 'error':
                return this.renderError();
            default:
                return this.renderInitialChoice();
        }
    }
    
    /**
     * Render initial choice screen
     */
    renderInitialChoice() {
        return `
            <div class="wallet-choice">
                <div class="choice-card">
                    <div class="choice-icon">✨</div>
                    <h4>I don't have a Stellar wallet</h4>
                    <p>We'll create a new wallet for you, fund it with 5 XLM, and add the UBECrc token.</p>
                    <button id="btn-create-wallet" class="btn btn-primary">
                        Create Wallet for Me
                    </button>
                </div>
                
                <div class="choice-divider">OR</div>
                
                <div class="choice-card">
                    <div class="choice-icon">👛</div>
                    <h4>I already have a Stellar wallet</h4>
                    <p>Enter your public key in the registration form above.</p>
                    <button id="btn-have-wallet" class="btn btn-secondary">
                        I'll Enter My Own
                    </button>
                </div>
            </div>
            
            <div class="info-box" style="margin-top: 2rem;">
                <strong>What is a Stellar wallet?</strong>
                <p>A Stellar wallet is your gateway to receiving UBECrc tokens as rewards for your environmental observations. 
                It consists of a public key (like an email address) and a secret key (like a password).</p>
            </div>
        `;
    }
    
    /**
     * Render wallet creation in progress
     */
    renderCreating() {
        return `
            <div class="wallet-creating">
                <div class="loading-spinner"></div>
                <h4>Creating Your Wallet...</h4>
                <div class="creation-steps">
                    <div class="step completed">✓ Generating secure keypair</div>
                    <div class="step active">⏳ Funding account with 5 XLM</div>
                    <div class="step">⏳ Adding UBECrc trustline</div>
                    <div class="step">⏳ Finalizing setup</div>
                </div>
                <p class="text-muted">This may take a few seconds...</p>
            </div>
        `;
    }
    
    /**
     * Render success screen with wallet credentials
     */
    renderSuccess() {
        if (!this.walletData) return '';
        
        return `
            <div class="wallet-success">
                <div class="success-icon">🎉</div>
                <h4>Your Wallet is Ready!</h4>
                
                <div class="credentials-box critical">
                    <div class="credential-item">
                        <span class="credential-label">Public Key (Share this):</span>
                        <div class="credential-value-container">
                            <code class="credential-value" id="wallet-public">${this.walletData.public_key}</code>
                            <button class="btn-copy" onclick="walletCreator.copyToClipboard('wallet-public')">📋</button>
                        </div>
                    </div>
                    
                    <div class="credential-item critical-item">
                        <span class="credential-label">Secret Key (NEVER share this!):</span>
                        <div class="credential-value-container">
                            <code class="credential-value secret-blur" id="wallet-secret">${this.walletData.secret_key}</code>
                            <button class="btn-toggle" onclick="walletCreator.toggleSecretVisibility()">👁️</button>
                            <button class="btn-copy" onclick="walletCreator.copyToClipboard('wallet-secret')">📋</button>
                        </div>
                    </div>
                </div>
                
                <div class="wallet-info">
                    <div class="info-row">
                        <span>💰 XLM Balance:</span>
                        <strong>${this.walletData.xlm_balance} XLM</strong>
                    </div>
                    <div class="info-row">
                        <span>🎫 UBECrc Trustline:</span>
                        <strong>${this.walletData.trustline_created ? '✓ Active' : '⚠️ Not created'}</strong>
                    </div>
                    <div class="info-row">
                        <span>🌐 Network:</span>
                        <strong>${this.walletData.network === 'testnet' ? 'Testnet' : 'Mainnet'}</strong>
                    </div>
                </div>
                
                ${this.walletData.warning ? `
                    <div class="warning-box">⚠️ ${this.walletData.warning}</div>
                ` : ''}
                
                <div class="security-notice">
                    <h5>🔒 Critical Security Instructions</h5>
                    <ul>
                        <li><strong>Save your secret key NOW</strong> - Write it down or save it in a password manager</li>
                        <li><strong>NEVER share your secret key</strong> with anyone - Not even support staff</li>
                        <li><strong>This is your only chance</strong> to see your secret key - We cannot recover it</li>
                        <li><strong>Public key is safe to share</strong> - Use it to receive tokens</li>
                    </ul>
                </div>
                
                <div class="action-buttons">
                    <button id="btn-downloaded" class="btn btn-primary" disabled>
                        ✓ I've Saved My Secret Key
                    </button>
                    <button id="btn-download-keys" class="btn btn-secondary">
                        📥 Download Credentials
                    </button>
                </div>
                
                <div class="next-steps">
                    <p>Your public key has been automatically filled in the registration form above. 
                    Once you've saved your secret key, complete the registration form to become a steward!</p>
                </div>
            </div>
        `;
    }
    
    /**
     * Render error screen
     */
    renderError() {
        return `
            <div class="wallet-error">
                <div class="error-icon">❌</div>
                <h4>Wallet Creation Failed</h4>
                <p>${this.errorMessage || 'An unexpected error occurred. Please try again.'}</p>
                <button id="btn-retry" class="btn btn-primary">
                    Try Again
                </button>
            </div>
        `;
    }
    
    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Delegate events from container
        const container = document.getElementById(this.containerId);
        
        container.addEventListener('click', async (e) => {
            if (e.target.id === 'btn-create-wallet') {
                await this.createWallet();
            } else if (e.target.id === 'btn-have-wallet') {
                this.closeCreator();
            } else if (e.target.id === 'btn-retry') {
                this.currentStep = 'initial';
                this.render();
                this.attachEventListeners();
            } else if (e.target.id === 'btn-download-keys') {
                this.downloadCredentials();
            } else if (e.target.id === 'btn-downloaded') {
                this.fillFormAndClose();
            }
        });
        
        // Enable "I've saved" button after delay
        setTimeout(() => {
            const btn = document.getElementById('btn-downloaded');
            if (btn) {
                btn.disabled = false;
            }
        }, 5000); // 5 second delay to encourage reading
    }
    
    /**
     * Create new wallet via API
     */
    async createWallet() {
        // Get steward info from main form
        const stewardForm = document.getElementById('stewardForm');
        if (!stewardForm) {
            alert('Please fill in your name and email in the registration form first.');
            return;
        }
        
        const formData = new FormData(stewardForm);
        const name = formData.get('name');
        const email = formData.get('email');
        
        if (!name || !email) {
            alert('Please fill in your name and email in the registration form first.');
            return;
        }
        
        // Show creating screen
        this.currentStep = 'creating';
        this.render();
        
        try {
            const response = await fetch('/api/v2/stellar/create-wallet', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    steward_name: name,
                    steward_email: email
                })
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                this.walletData = data;
                this.currentStep = 'success';
                this.debugService.log('✅ Wallet created successfully', 'success');
            } else {
                throw new Error(data.detail || 'Wallet creation failed');
            }
        } catch (error) {
            this.errorMessage = error.message;
            this.currentStep = 'error';
            this.debugService.log(`❌ Wallet creation error: ${error.message}`, 'error');
        }
        
        this.render();
        this.attachEventListeners();
    }
    
    /**
     * Copy text to clipboard
     */
    copyToClipboard(elementId) {
        const element = document.getElementById(elementId);
        const text = element.textContent;
        
        navigator.clipboard.writeText(text).then(() => {
            // Visual feedback
            const btn = event.target;
            const originalText = btn.textContent;
            btn.textContent = '✓';
            setTimeout(() => {
                btn.textContent = originalText;
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy:', err);
        });
    }
    
    /**
     * Toggle secret key visibility
     */
    toggleSecretVisibility() {
        const secretElement = document.getElementById('wallet-secret');
        secretElement.classList.toggle('secret-blur');
        
        const btn = event.target;
        btn.textContent = secretElement.classList.contains('secret-blur') ? '👁️' : '🙈';
    }
    
    /**
     * Download credentials as text file
     */
    downloadCredentials() {
        const content = `STELLAR WALLET CREDENTIALS
==========================

⚠️ CRITICAL: KEEP THIS FILE SECURE ⚠️

Steward: ${document.getElementById('stewardForm')?.elements['name']?.value}
Created: ${new Date().toISOString()}

Public Key (safe to share):
${this.walletData.public_key}

Secret Key (NEVER share):
${this.walletData.secret_key}

Network: ${this.walletData.network}
Initial Balance: ${this.walletData.xlm_balance} XLM
UBECrc Trustline: ${this.walletData.trustline_created ? 'Active' : 'Not created'}

SECURITY REMINDERS:
- Store this file in a secure location
- Never share your secret key with anyone
- This key cannot be recovered if lost
- Use only the public key to receive tokens
`;
        
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `stellar-wallet-${this.walletData.public_key.substring(0, 8)}.txt`;
        a.click();
        URL.revokeObjectURL(url);
        
        this.debugService.log('📥 Credentials downloaded', 'success');
    }
    
    /**
     * Fill form with public key and close creator
     */
    fillFormAndClose() {
        const stellarInput = document.getElementById('stellarWallet') || 
                            document.querySelector('input[name="stellar_address"]');
        
        if (stellarInput && this.walletData) {
            stellarInput.value = this.walletData.public_key;
            this.debugService.log('✓ Public key added to form', 'success');
        }
        
        this.closeCreator();
    }
    
    /**
     * Close the wallet creator
     */
    closeCreator() {
        const container = document.getElementById(this.containerId);
        if (container) {
            container.style.display = 'none';
        }
    }
}

// Export for use in registration forms
window.StellarWalletCreator = StellarWalletCreator;
