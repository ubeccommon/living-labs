/**
 * Stellar Wallet Creation Component
 * 
 * Guides users through creating a Stellar wallet if they don't have one
 * Follows Design Principle #12 (Method Singularity)
 * 
 * Attribution: This project uses the services of Claude and Anthropic PBC.
 * 
 * Version: 2.0.0 (Enhanced UX with Modal & Safety Confirmations)
 */

class StellarWalletCreator {
    constructor(containerId, apiService, debugService) {
        this.containerId = containerId;
        this.apiService = apiService;
        this.debugService = debugService;
        this.currentStep = 'initial';
        this.walletData = null;
        this.errorMessage = null;
        this.credentialsDownloaded = false;
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
        
        container.innerHTML = content;
    }
    
    /**
     * Render initial screen
     */
    renderInitial() {
        return `
            <div class="wallet-creator">
                <div class="wallet-creator-header">
                    <h3>🔐 Stellar Wallet Setup</h3>
                    <p>Don't have a Stellar wallet? We'll create one for you!</p>
                </div>
                <div class="wallet-creator-body">
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
                                <span class="feature-icon">🔒</span>
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
                </div>
            </div>
        `;
    }
    
    /**
     * Render wallet creation in progress
     */
    renderCreating() {
        return `
            <div class="wallet-creator">
                <div class="wallet-creator-body">
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
                </div>
            </div>
        `;
    }
    
    /**
     * Render success screen with wallet credentials - NOW AS MODAL
     */
    renderSuccess() {
        if (!this.walletData) return '';
        
        return `
            <div class="wallet-modal-overlay" id="wallet-modal-overlay">
                <div class="wallet-modal">
                    <div class="modal-header">
                        <div class="success-icon-large">🎉</div>
                        <h2>Your Wallet is Ready!</h2>
                        <div class="warning-pulse">
                            ⚠️ ONE-TIME VIEW ONLY ⚠️
                        </div>
                    </div>
                    
                    <div class="modal-body">
                        <div class="credentials-box">
                            <div class="credential-item">
                                <label class="credential-label">
                                    <span class="label-icon">✅</span>
                                    Public Key (Safe to Share)
                                </label>
                                <div class="credential-value-container">
                                    <code class="credential-value public-key" id="wallet-public">${this.walletData.public_key}</code>
                                    <button class="btn-icon btn-copy" onclick="walletCreator.copyToClipboard('wallet-public')" title="Copy">
                                        📋
                                    </button>
                                </div>
                            </div>
                            
                            <div class="credential-item critical-item">
                                <label class="credential-label critical-label">
                                    <span class="label-icon">🔐</span>
                                    Secret Key (NEVER SHARE!)
                                </label>
                                <div class="credential-value-container">
                                    <code class="credential-value secret-key secret-blur" id="wallet-secret">${this.walletData.secret_key}</code>
                                    <button class="btn-icon btn-toggle" onclick="walletCreator.toggleSecretVisibility()" title="Show/Hide">
                                        👁️
                                    </button>
                                    <button class="btn-icon btn-copy" onclick="walletCreator.copyToClipboard('wallet-secret')" title="Copy">
                                        📋
                                    </button>
                                </div>
                            </div>
                        </div>
                        
                        <div class="wallet-info-grid">
                            <div class="info-item">
                                <span class="info-icon">💰</span>
                                <div class="info-content">
                                    <span class="info-label">XLM Balance</span>
                                    <strong>${this.walletData.xlm_balance} XLM</strong>
                                </div>
                            </div>
                            <div class="info-item">
                                <span class="info-icon">🎫</span>
                                <div class="info-content">
                                    <span class="info-label">UBECrc Trustline</span>
                                    <strong>${this.walletData.trustline_created ? '✓ Active' : '⏳ Pending'}</strong>
                                </div>
                            </div>
                            <div class="info-item">
                                <span class="info-icon">🌐</span>
                                <div class="info-content">
                                    <span class="info-label">Network</span>
                                    <strong>${this.walletData.network}</strong>
                                </div>
                            </div>
                        </div>
                        
                        <div class="critical-warning-box">
                            <div class="warning-icon-large">⚠️</div>
                            <div class="warning-content">
                                <h3>CRITICAL: Save Your Keys NOW!</h3>
                                <p>This is the <strong>ONLY TIME</strong> you'll see your secret key.</p>
                                <p>If you lose it, you will <strong>PERMANENTLY LOSE ACCESS</strong> to your wallet and funds.</p>
                                <p class="warning-emphasis">There is NO way to recover a lost secret key!</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="modal-actions">
                        <button id="btn-download-keys" class="btn btn-primary btn-large" onclick="walletCreator.downloadCredentials()">
                            📥 Download Credentials File
                        </button>
                        
                        <button id="btn-continue" class="btn btn-success btn-large" disabled>
                            ✓ I've Saved My Keys - Continue
                        </button>
                        
                        <p class="action-hint" id="download-hint">
                            ⬆️ Please download your credentials first
                        </p>
                    </div>
                    
                    <div class="modal-footer">
                        <p class="footer-text">After clicking continue, you'll complete the registration form to become a steward.</p>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Render error screen
     */
    renderError() {
        return `
            <div class="wallet-creator">
                <div class="wallet-creator-body">
                    <div class="wallet-error">
                        <div class="error-icon">❌</div>
                        <h4>Wallet Creation Failed</h4>
                        <p>${this.errorMessage || 'An unexpected error occurred. Please try again.'}</p>
                        <button id="btn-retry" class="btn btn-primary">
                            🔄 Try Again
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Attach event listeners
     */
    attachEventListeners() {
        const container = document.getElementById(this.containerId);
        
        container.addEventListener('click', async (e) => {
            if (e.target.id === 'btn-create-wallet') {
                await this.createWallet();
            } else if (e.target.id === 'btn-have-wallet') {
                this.closeCreator();
            } else if (e.target.id === 'btn-retry') {
                this.currentStep = 'initial';
                this.errorMessage = null;
                this.render();
                this.attachEventListeners();
            } else if (e.target.id === 'btn-continue') {
                await this.confirmAndContinue();
            }
        });
        
        // For success modal, enable continue button after download
        if (this.currentStep === 'success') {
            // Prevent modal close by clicking overlay
            const overlay = document.getElementById('wallet-modal-overlay');
            if (overlay) {
                overlay.addEventListener('click', (e) => {
                    if (e.target.id === 'wallet-modal-overlay') {
                        this.showWarning('You must save your credentials before continuing!');
                    }
                });
            }
            
            // Enable continue button after 8 seconds AND download
            setTimeout(() => {
                this.enableContinueIfDownloaded();
            }, 8000);
        }
    }
    
    /**
     * Enable continue button if credentials were downloaded
     */
    enableContinueIfDownloaded() {
        if (this.credentialsDownloaded) {
            const btn = document.getElementById('btn-continue');
            const hint = document.getElementById('download-hint');
            if (btn) {
                btn.disabled = false;
                btn.classList.add('btn-pulse');
            }
            if (hint) {
                hint.textContent = '✓ Credentials downloaded - you may continue';
                hint.style.color = '#10b981';
            }
        }
    }
    
    /**
     * Show warning message
     */
    showWarning(message) {
        alert(message);
    }
    
    /**
     * Confirm before continuing
     */
    async confirmAndContinue() {
        // First confirmation
        const confirmed1 = confirm(
            '⚠️ FINAL WARNING ⚠️\n\n' +
            'Have you saved your secret key?\n\n' +
            'If you continue without saving it, you will PERMANENTLY LOSE ACCESS to your wallet.\n\n' +
            'Click CANCEL to go back and save your keys.\n' +
            'Click OK only if you have saved them.'
        );
        
        if (!confirmed1) {
            return;
        }
        
        // Second confirmation (extra safety)
        const confirmed2 = confirm(
            '⚠️ LAST CHANCE ⚠️\n\n' +
            'Are you ABSOLUTELY SURE you saved your secret key?\n\n' +
            'Did you:\n' +
            '✓ Download the credentials file?\n' +
            '✓ OR write down the secret key?\n' +
            '✓ OR save it to a password manager?\n\n' +
            'This is your LAST opportunity to see it!\n\n' +
            'Click CANCEL to go back.\n' +
            'Click OK to proceed (you cannot go back).'
        );
        
        if (confirmed2) {
            this.fillFormAndClose();
        }
    }
    
    /**
     * Create new wallet via API
     */
    async createWallet() {
        // Get steward info from main form
        const stewardForm = document.getElementById('stewardForm');
        if (!stewardForm) {
            this.showWarning('Please fill in your name and email in the registration form first.');
            return;
        }
        
        const formData = new FormData(stewardForm);
        const name = formData.get('name');
        const email = formData.get('email');
        
        if (!name || !email) {
            this.showWarning('Please fill in your name and email in the registration form first.');
            return;
        }
        
        // Set creating state
        this.currentStep = 'creating';
        this.render();
        
        try {
            const response = await this.apiService.post('/api/v2/stellar/create-wallet', {
                steward_email: email,
                steward_name: name
            });
            
            // Store wallet data
            this.walletData = response;
            this.credentialsDownloaded = false;
            
            // Emit custom event
            const event = new CustomEvent('walletCreated', { 
                detail: { 
                    publicKey: response.public_key,
                    secretKey: response.secret_key
                } 
            });
            document.dispatchEvent(event);
            
            // Show success modal
            this.currentStep = 'success';
            this.render();
            this.attachEventListeners();
            
            // Scroll to top to ensure modal is visible
            window.scrollTo({ top: 0, behavior: 'smooth' });
            
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
            const btn = element.parentElement.querySelector('.btn-copy');
            const originalText = btn.textContent;
            btn.textContent = '✓';
            btn.style.background = '#10b981';
            
            setTimeout(() => {
                btn.textContent = originalText;
                btn.style.background = '';
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy:', err);
            this.showWarning('Failed to copy. Please manually select and copy the text.');
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

HOW TO USE YOUR WALLET:
- Public Key: Share this to receive UBECrc tokens
- Secret Key: Keep this private - needed to send tokens
- Recommended: Store in a password manager or encrypted storage

For support, contact: support@ubec.earth
`;
        
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `stellar-wallet-${this.walletData.public_key.substring(0, 8)}-${Date.now()}.txt`;
        a.click();
        URL.revokeObjectURL(url);
        
        // Mark as downloaded
        this.credentialsDownloaded = true;
        this.enableContinueIfDownloaded();
        
        this.debugService.log('📥 Credentials downloaded', 'success');
        
        // Show confirmation
        setTimeout(() => {
            alert('✓ Credentials file downloaded!\n\nPlease store it in a secure location.\n\nYou can now click "Continue" to complete registration.');
        }, 500);
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
        
        // Scroll to the stellar input field
        if (stellarInput) {
            stellarInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
            stellarInput.focus();
        }
    }
    
    /**
     * Close the wallet creator
     */
    closeCreator() {
        const container = document.getElementById(this.containerId);
        if (container) {
            container.style.display = 'none';
        }
        
        // Reset state
        this.currentStep = 'initial';
        this.credentialsDownloaded = false;
    }
}

// Export for use in registration forms
window.StellarWalletCreator = StellarWalletCreator;
