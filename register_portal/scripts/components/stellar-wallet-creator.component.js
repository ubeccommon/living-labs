/**
 * Stellar Wallet Creation Component
 * 
 * Guides users through creating a Stellar wallet if they don't have one
 * Follows Design Principle #12 (Method Singularity)
 * 
 * Attribution: This project uses the services of Claude and Anthropic PBC.
 * 
 * Version: 1.0.1 (Fixed API endpoint path)
 */

class StellarWalletCreator {
    constructor(containerId, apiService, debugService) {
        this.containerId = containerId;
        this.apiService = apiService;
        this.debugService = debugService;
        this.currentStep = 'initial';
        this.walletData = null;
        this.errorMessage = null;
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
     * Set steward info for wallet creation
     */
    setStewardInfo(name, email) {
        this.stewardName = name;
        this.stewardEmail = email;
    }
    
    /**
     * Render the wallet creation interface
     */
    render() {
        const container = document.getElementById(this.containerId);
        
        let content = '';
        switch(this.currentStep) {
            case 'initial':
                content = this.renderInitial();
                break;
            case 'creating':
                content = this.renderCreating();
                break;
            case 'success':
                content = this.renderSuccess();
                break;
            case 'error':
                content = this.renderError();
                break;
        }
        
        container.innerHTML = `
            <div class="wallet-creator">
                <div class="wallet-creator-header">
                    <h3>🔐 Stellar Wallet Setup</h3>
                    <p>Don't have a Stellar wallet? We'll create one for you!</p>
                </div>
                <div class="wallet-creator-body">
                    ${content}
                </div>
            </div>
        `;
    }
    
    /**
     * Render initial screen
     */
    renderInitial() {
        return `
            <div class="wallet-initial">
                <h4>What is a Stellar Wallet?</h4>
                <p>A Stellar wallet lets you receive UBECrc tokens for your environmental stewardship contributions.</p>
                
                <div class="wallet-features">
                    <div class="feature">
                        <span class="feature-icon">💰</span>
                        <span class="feature-text">We'll fund it with 5 XLM</span>
                    </div>
                    <div class="feature">
                        <span class="feature-icon">🎫</span>
                        <span class="feature-text">UBECrc trustline already set up</span>
                    </div>
                    <div class="feature">
                        <span class="feature-icon">🔐</span>
                        <span class="feature-text">Secure keypair generation</span>
                    </div>
                </div>
                
                <div class="wallet-actions">
                    <button id="btn-create-wallet" class="btn btn-primary">
                        ✨ Create My Wallet
                    </button>
                    <button id="btn-have-wallet" class="btn btn-secondary">
                        I Already Have a Wallet
                    </button>
                </div>
                
                <div class="wallet-info">
                    <p class="text-muted"><strong>What you'll receive:</strong></p>
                    <p class="text-muted">A public key (like an email address) and a secret key (like a password) that you'll need to save securely.</p>
                </div>
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
                        <strong>${this.walletData.trustline_created ? '✓ Active' : '⏳ Pending'}</strong>
                    </div>
                    <div class="info-row">
                        <span>🌐 Network:</span>
                        <strong>${this.walletData.network}</strong>
                    </div>
                </div>
                
                <div class="security-warning">
                    <strong>⚠️ CRITICAL: Save Your Keys Now!</strong>
                    <p>This is the ONLY time you'll see your secret key. Save it securely or you'll lose access to your funds forever.</p>
                </div>
                
                <div class="wallet-actions">
                    <button id="btn-download-keys" class="btn btn-primary">
                        📥 Download Credentials
                    </button>
                    <button id="btn-downloaded" class="btn btn-success" disabled>
                        ✓ I've Saved My Keys, Continue
                    </button>
                </div>
                
                <div class="wallet-next-steps">
                    <p class="text-muted">Once you've saved your secret key, complete the registration form to become a steward!</p>
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
     * FIXED: Now uses correct endpoint /api/v2/stellar/onboarding/create
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
        
        // Set creating state
        this.currentStep = 'creating';
        this.render();
        
        try {
            // FIXED: Correct endpoint path
            const response = await this.apiService.post('/api/v2/stellar/onboarding/create', {
                steward_email: email,
                steward_name: name
            });
            
            // Store wallet data
            this.walletData = response;
            
            // Emit custom event that wallet was created
            const event = new CustomEvent('walletCreated', { 
                detail: { 
                    publicKey: response.public_key,
                    secretKey: response.secret_key
                } 
            });
            document.dispatchEvent(event);
            
            // Show success
            this.currentStep = 'success';
            this.render();
            this.attachEventListeners();
            
            this.debugService.log('✓ Wallet created successfully', 'success');
            
        } catch (error) {
            console.error('Wallet creation failed:', error);
            this.errorMessage = error.message || 'Failed to create wallet. Please try again.';
            this.currentStep = 'error';
            this.render();
            this.attachEventListeners();
            
            this.debugService.log('✗ Wallet creation failed: ' + error.message, 'error');
        }
    }
    
    /**
     * Copy text to clipboard
     */
    copyToClipboard(elementId) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const text = element.textContent;
        navigator.clipboard.writeText(text).then(() => {
            this.debugService.log('📋 Copied to clipboard', 'success');
            
            // Visual feedback
            const originalText = element.parentElement.querySelector('.btn-copy').textContent;
            element.parentElement.querySelector('.btn-copy').textContent = '✓';
            setTimeout(() => {
                element.parentElement.querySelector('.btn-copy').textContent = originalText;
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
        if (!secretElement) return;
        
        secretElement.classList.toggle('secret-blur');
        
        const btn = secretElement.parentElement.querySelector('.btn-toggle');
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
