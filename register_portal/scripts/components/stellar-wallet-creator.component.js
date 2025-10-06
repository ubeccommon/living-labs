/**
 * Stellar Wallet Creator Component - MULTILINGUAL VERSION
 * Supports: English, Deutsch (German), Polski (Polish)
 * 
 * Auto-detects language from page URL:
 * - steward-en.html → English
 * - steward-de.html → Deutsch
 * - steward-pl.html → Polski
 * 
 * Attribution: This project uses the services of Claude and Anthropic PBC
 */

class StellarWalletCreatorMultilingual {
    constructor(containerId, apiService, debugService) {
        this.containerId = containerId;
        this.apiService = apiService;
        this.debugService = debugService;
        
        // State management
        this.currentStep = 'initial'; // initial, creating, success, error
        this.walletData = null;
        this.stewardData = null;
        
        // Auto-detect language from URL
        this.language = this.detectLanguage();
        
        // Initialize translations
        this.translations = this.getTranslations();
    }
    
    /**
     * Detect language from current page URL
     */
    detectLanguage() {
        const path = window.location.pathname;
        
        if (path.includes('-de.html') || path.includes('/de/')) {
            return 'de';
        } else if (path.includes('-pl.html') || path.includes('/pl/')) {
            return 'pl';
        } else {
            return 'en'; // Default to English
        }
    }
    
    /**
     * Get translated string
     */
    t(key) {
        const keys = key.split('.');
        let value = this.translations[this.language];
        
        for (const k of keys) {
            value = value?.[k];
            if (value === undefined) {
                this.debugService.log(`Translation missing: ${key} (${this.language})`, 'warn');
                return key;
            }
        }
        
        return value;
    }
    
    /**
     * Complete translations object for all languages
     */
    getTranslations() {
        return {
            // ENGLISH
            en: {
                title: "Create Stellar Wallet",
                subtitle: "Get started with blockchain stewardship",
                
                initial: {
                    heading: "No Stellar Wallet Yet?",
                    description: "We can automatically create one for you!",
                    benefits: {
                        title: "What you'll receive:",
                        funded: "Account funded with 5 XLM",
                        trustline: "UBECrc trustline pre-configured",
                        ready: "Ready to receive rewards immediately"
                    },
                    security: {
                        title: "Security First",
                        point1: "You'll receive a public key (safe to share)",
                        point2: "And a secret key (NEVER share this)",
                        point3: "Save your secret key immediately - we can't recover it"
                    },
                    button: "🪴 Create Wallet for Me",
                    info: "What you'll receive: A public key (like an email address) and a secret key (like a password) that you'll need to save securely."
                },
                
                creating: {
                    heading: "Creating Your Wallet...",
                    steps: {
                        keypair: "Generating secure keypair",
                        funding: "Funding account with 5 XLM",
                        trustline: "Adding UBECrc trustline",
                        finalizing: "Finalizing setup"
                    },
                    wait: "This may take a few seconds..."
                },
                
                success: {
                    heading: "🎉 Wallet Created Successfully!",
                    critical: "CRITICAL: Save Your Keys Now!",
                    warning: "This is the ONLY time you'll see your secret key. If you lose it, your funds are gone forever.",
                    publicKey: {
                        label: "Public Key",
                        note: "(Safe to share - like an email address)"
                    },
                    secretKey: {
                        label: "Secret Key",
                        note: "(NEVER share - like a password)",
                        blur: "Click eye to reveal"
                    },
                    info: {
                        balance: "XLM Balance",
                        trustline: "UBECrc Trustline",
                        network: "Network"
                    },
                    trustlineStatus: {
                        added: "✓ Added",
                        notAdded: "✗ Not Added"
                    },
                    actions: {
                        download: "📥 Download Credentials",
                        saved: "✓ I've Saved My Keys",
                        lastChance: "LAST CHANCE: Have you saved your secret key?"
                    },
                    downloadContent: {
                        title: "STELLAR WALLET CREDENTIALS",
                        warning: "⚠️ CRITICAL: KEEP THIS FILE SECURE ⚠️",
                        created: "Created",
                        publicLabel: "Public Key (safe to share)",
                        secretLabel: "Secret Key (NEVER share)",
                        network: "Network",
                        balance: "Initial Balance",
                        trustline: "UBECrc Trustline"
                    }
                },
                
                error: {
                    heading: "❌ Wallet Creation Failed",
                    message: "We encountered an error creating your wallet. Please try again or enter your Stellar address manually.",
                    button: "Try Again",
                    fallback: "Or enter your Stellar address manually in the form above."
                },
                
                buttons: {
                    cancel: "Cancel",
                    close: "Close",
                    copy: "Copy",
                    copied: "✓",
                    show: "Show",
                    hide: "Hide"
                }
            },
            
            // GERMAN (DEUTSCH)
            de: {
                title: "Stellar Wallet Erstellen",
                subtitle: "Beginnen Sie mit Blockchain-Verwaltung",
                
                initial: {
                    heading: "Noch kein Stellar Wallet?",
                    description: "Wir können automatisch eines für Sie erstellen!",
                    benefits: {
                        title: "Was Sie erhalten:",
                        funded: "Konto mit 5 XLM finanziert",
                        trustline: "UBECrc Trustline vorkonfiguriert",
                        ready: "Sofort bereit für Belohnungen"
                    },
                    security: {
                        title: "Sicherheit zuerst",
                        point1: "Sie erhalten einen öffentlichen Schlüssel (sicher zu teilen)",
                        point2: "Und einen geheimen Schlüssel (NIEMALS teilen)",
                        point3: "Speichern Sie Ihren geheimen Schlüssel sofort - wir können ihn nicht wiederherstellen"
                    },
                    button: "🪴 Wallet Für Mich Erstellen",
                    info: "Was Sie erhalten: Einen öffentlichen Schlüssel (wie eine E-Mail-Adresse) und einen geheimen Schlüssel (wie ein Passwort), den Sie sicher aufbewahren müssen."
                },
                
                creating: {
                    heading: "Wallet Wird Erstellt...",
                    steps: {
                        keypair: "Sichere Schlüsselpaar generieren",
                        funding: "Konto mit 5 XLM finanzieren",
                        trustline: "UBECrc Trustline hinzufügen",
                        finalizing: "Setup abschließen"
                    },
                    wait: "Dies kann einige Sekunden dauern..."
                },
                
                success: {
                    heading: "🎉 Wallet Erfolgreich Erstellt!",
                    critical: "KRITISCH: Speichern Sie Ihre Schlüssel Jetzt!",
                    warning: "Dies ist das EINZIGE Mal, dass Sie Ihren geheimen Schlüssel sehen. Wenn Sie ihn verlieren, sind Ihre Mittel für immer verloren.",
                    publicKey: {
                        label: "Öffentlicher Schlüssel",
                        note: "(Sicher zu teilen - wie eine E-Mail-Adresse)"
                    },
                    secretKey: {
                        label: "Geheimer Schlüssel",
                        note: "(NIEMALS teilen - wie ein Passwort)",
                        blur: "Klicken Sie auf das Auge zum Anzeigen"
                    },
                    info: {
                        balance: "XLM Guthaben",
                        trustline: "UBECrc Trustline",
                        network: "Netzwerk"
                    },
                    trustlineStatus: {
                        added: "✓ Hinzugefügt",
                        notAdded: "✗ Nicht Hinzugefügt"
                    },
                    actions: {
                        download: "📥 Zugangsdaten Herunterladen",
                        saved: "✓ Ich Habe Meine Schlüssel Gespeichert",
                        lastChance: "LETZTE CHANCE: Haben Sie Ihren geheimen Schlüssel gespeichert?"
                    },
                    downloadContent: {
                        title: "STELLAR WALLET ZUGANGSDATEN",
                        warning: "⚠️ KRITISCH: DIESE DATEI SICHER AUFBEWAHREN ⚠️",
                        created: "Erstellt",
                        publicLabel: "Öffentlicher Schlüssel (sicher zu teilen)",
                        secretLabel: "Geheimer Schlüssel (NIEMALS teilen)",
                        network: "Netzwerk",
                        balance: "Anfangsguthaben",
                        trustline: "UBECrc Trustline"
                    }
                },
                
                error: {
                    heading: "❌ Wallet-Erstellung Fehlgeschlagen",
                    message: "Beim Erstellen Ihres Wallets ist ein Fehler aufgetreten. Bitte versuchen Sie es erneut oder geben Sie Ihre Stellar-Adresse manuell ein.",
                    button: "Erneut Versuchen",
                    fallback: "Oder geben Sie Ihre Stellar-Adresse manuell im obigen Formular ein."
                },
                
                buttons: {
                    cancel: "Abbrechen",
                    close: "Schließen",
                    copy: "Kopieren",
                    copied: "✓",
                    show: "Anzeigen",
                    hide: "Verbergen"
                }
            },
            
            // POLISH (POLSKI)
            pl: {
                title: "Utwórz Portfel Stellar",
                subtitle: "Zacznij zarządzanie blockchain",
                
                initial: {
                    heading: "Nie Masz Jeszcze Portfela Stellar?",
                    description: "Możemy automatycznie utworzyć jeden dla Ciebie!",
                    benefits: {
                        title: "Co otrzymasz:",
                        funded: "Konto zasilone 5 XLM",
                        trustline: "UBECrc trustline wstępnie skonfigurowany",
                        ready: "Gotowy do natychmiastowego otrzymywania nagród"
                    },
                    security: {
                        title: "Bezpieczeństwo Przede Wszystkim",
                        point1: "Otrzymasz klucz publiczny (bezpieczny do udostępnienia)",
                        point2: "I klucz tajny (NIGDY nie udostępniaj)",
                        point3: "Zapisz swój klucz tajny natychmiast - nie możemy go odzyskać"
                    },
                    button: "🪴 Utwórz Portfel Dla Mnie",
                    info: "Co otrzymasz: Klucz publiczny (jak adres e-mail) i klucz tajny (jak hasło), które musisz bezpiecznie zapisać."
                },
                
                creating: {
                    heading: "Tworzenie Portfela...",
                    steps: {
                        keypair: "Generowanie bezpiecznej pary kluczy",
                        funding: "Zasilanie konta 5 XLM",
                        trustline: "Dodawanie trustline UBECrc",
                        finalizing: "Finalizowanie konfiguracji"
                    },
                    wait: "To może potrwać kilka sekund..."
                },
                
                success: {
                    heading: "🎉 Portfel Utworzony Pomyślnie!",
                    critical: "KRYTYCZNE: Zapisz Swoje Klucze Teraz!",
                    warning: "To jest JEDYNY raz, kiedy zobaczysz swój klucz tajny. Jeśli go zgubisz, Twoje środki zostaną utracone na zawsze.",
                    publicKey: {
                        label: "Klucz Publiczny",
                        note: "(Bezpieczny do udostępnienia - jak adres e-mail)"
                    },
                    secretKey: {
                        label: "Klucz Tajny",
                        note: "(NIGDY nie udostępniaj - jak hasło)",
                        blur: "Kliknij oko, aby odsłonić"
                    },
                    info: {
                        balance: "Saldo XLM",
                        trustline: "Trustline UBECrc",
                        network: "Sieć"
                    },
                    trustlineStatus: {
                        added: "✓ Dodano",
                        notAdded: "✗ Nie Dodano"
                    },
                    actions: {
                        download: "📥 Pobierz Dane Logowania",
                        saved: "✓ Zapisałem Moje Klucze",
                        lastChance: "OSTATNIA SZANSA: Czy zapisałeś swój klucz tajny?"
                    },
                    downloadContent: {
                        title: "DANE LOGOWANIA PORTFELA STELLAR",
                        warning: "⚠️ KRYTYCZNE: ZACHOWAJ TEN PLIK W BEZPIECZNYM MIEJSCU ⚠️",
                        created: "Utworzono",
                        publicLabel: "Klucz publiczny (bezpieczny do udostępnienia)",
                        secretLabel: "Klucz tajny (NIGDY nie udostępniaj)",
                        network: "Sieć",
                        balance: "Saldo początkowe",
                        trustline: "Trustline UBECrc"
                    }
                },
                
                error: {
                    heading: "❌ Tworzenie Portfela Nie Powiodło Się",
                    message: "Napotkaliśmy błąd podczas tworzenia Twojego portfela. Spróbuj ponownie lub wprowadź adres Stellar ręcznie.",
                    button: "Spróbuj Ponownie",
                    fallback: "Lub wprowadź adres Stellar ręcznie w powyższym formularzu."
                },
                
                buttons: {
                    cancel: "Anuluj",
                    close: "Zamknij",
                    copy: "Kopiuj",
                    copied: "✓",
                    show: "Pokaż",
                    hide: "Ukryj"
                }
            }
        };
    }
    
    /**
     * Initialize the component
     */
    init() {
        this.debugService.log(`🌐 Wallet Creator initialized in ${this.language} (${this.getLanguageName()})`, 'info');
        this.render();
        this.attachEventListeners();
    }
    
    /**
     * Get language name
     */
    getLanguageName() {
        const names = {
            en: 'English',
            de: 'Deutsch',
            pl: 'Polski'
        };
        return names[this.language] || this.language;
    }
    
    /**
     * Main render method
     */
    render() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            this.debugService.error('Container not found:', this.containerId);
            return;
        }
        
        let html = '';
        
        switch (this.currentStep) {
            case 'initial':
                html = this.renderInitial();
                break;
            case 'creating':
                html = this.renderCreating();
                break;
            case 'success':
                html = this.renderSuccess();
                break;
            case 'error':
                html = this.renderError();
                break;
        }
        
        container.innerHTML = html;
        container.style.display = this.currentStep === 'initial' ? 'none' : 'block';
    }
    
    /**
     * Render initial wallet creation prompt
     */
    renderInitial() {
        return `
            <div class="wallet-creator">
                <div class="wallet-creator-header">
                    <h3>${this.t('initial.heading')}</h3>
                    <p>${this.t('initial.description')}</p>
                </div>
                
                <div class="wallet-creator-body">
                    <div class="wallet-benefits">
                        <h4>${this.t('initial.benefits.title')}</h4>
                        <ul>
                            <li>💰 ${this.t('initial.benefits.funded')}</li>
                            <li>🎫 ${this.t('initial.benefits.trustline')}</li>
                            <li>⚡ ${this.t('initial.benefits.ready')}</li>
                        </ul>
                    </div>
                    
                    <div class="wallet-security">
                        <h4>${this.t('initial.security.title')}</h4>
                        <ul>
                            <li>🔑 ${this.t('initial.security.point1')}</li>
                            <li>🔐 ${this.t('initial.security.point2')}</li>
                            <li>⚠️ ${this.t('initial.security.point3')}</li>
                        </ul>
                    </div>
                    
                    <button class="btn btn-primary" onclick="walletCreator.startCreation()">
                        ${this.t('initial.button')}
                    </button>
                    
                    <div class="wallet-info">
                        <p class="text-muted">${this.t('initial.info')}</p>
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
                        <h4>${this.t('creating.heading')}</h4>
                        <div class="creation-steps">
                            <div class="step completed">✓ ${this.t('creating.steps.keypair')}</div>
                            <div class="step active">⏳ ${this.t('creating.steps.funding')}</div>
                            <div class="step">⏳ ${this.t('creating.steps.trustline')}</div>
                            <div class="step">⏳ ${this.t('creating.steps.finalizing')}</div>
                        </div>
                        <p class="text-muted">${this.t('creating.wait')}</p>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Render success screen with wallet credentials - AS MODAL
     */
    renderSuccess() {
        if (!this.walletData) return '';
        
        return `
            <div class="wallet-modal-overlay" id="wallet-success-modal">
                <div class="wallet-modal">
                    <div class="wallet-modal-header">
                        <h3>${this.t('success.heading')}</h3>
                    </div>
                    
                    <div class="wallet-modal-body">
                        <div class="wallet-warning">
                            <strong>⚠️ ${this.t('success.critical')}</strong>
                            <p>${this.t('success.warning')}</p>
                        </div>
                        
                        <div class="wallet-credentials">
                            <div class="credential-group">
                                <label class="credential-label">
                                    🔑 ${this.t('success.publicKey.label')}
                                    <span class="credential-note">${this.t('success.publicKey.note')}</span>
                                </label>
                                <div class="credential-value-container">
                                    <code class="credential-value" id="wallet-public">${this.walletData.public_key}</code>
                                    <button class="btn-icon btn-copy" onclick="walletCreator.copyToClipboard('wallet-public')" title="${this.t('buttons.copy')}">
                                        📋
                                    </button>
                                </div>
                            </div>
                            
                            <div class="credential-group">
                                <label class="credential-label">
                                    🔐 ${this.t('success.secretKey.label')}
                                    <span class="credential-note">${this.t('success.secretKey.note')}</span>
                                </label>
                                <div class="credential-value-container">
                                    <code class="credential-value secret-key secret-blur" id="wallet-secret">${this.walletData.secret_key}</code>
                                    <button class="btn-icon btn-toggle" onclick="walletCreator.toggleSecretVisibility()" title="${this.t('buttons.show')}/${this.t('buttons.hide')}">
                                        👁️
                                    </button>
                                    <button class="btn-icon btn-copy" onclick="walletCreator.copyToClipboard('wallet-secret')" title="${this.t('buttons.copy')}">
                                        📋
                                    </button>
                                </div>
                            </div>
                        </div>
                        
                        <div class="wallet-info-grid">
                            <div class="info-item">
                                <span class="info-icon">💰</span>
                                <div class="info-content">
                                    <span class="info-label">${this.t('success.info.balance')}</span>
                                    <strong>${this.walletData.xlm_balance} XLM</strong>
                                </div>
                            </div>
                            <div class="info-item">
                                <span class="info-icon">🎫</span>
                                <div class="info-content">
                                    <span class="info-label">${this.t('success.info.trustline')}</span>
                                    <strong>${this.walletData.trustline_created ? 
                                        this.t('success.trustlineStatus.added') : 
                                        this.t('success.trustlineStatus.notAdded')}</strong>
                                </div>
                            </div>
                            <div class="info-item">
                                <span class="info-icon">🌐</span>
                                <div class="info-content">
                                    <span class="info-label">${this.t('success.info.network')}</span>
                                    <strong>${this.walletData.network}</strong>
                                </div>
                            </div>
                        </div>
                        
                        <div class="wallet-actions">
                            <button class="btn btn-secondary" onclick="walletCreator.downloadCredentials()">
                                ${this.t('success.actions.download')}
                            </button>
                            <button class="btn btn-primary" onclick="walletCreator.confirmSaved()">
                                ${this.t('success.actions.saved')}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Render error state
     */
    renderError() {
        return `
            <div class="wallet-creator">
                <div class="wallet-creator-body">
                    <div class="wallet-error">
                        <h4>${this.t('error.heading')}</h4>
                        <p>${this.t('error.message')}</p>
                        <button class="btn btn-primary" onclick="walletCreator.reset()">
                            ${this.t('error.button')}
                        </button>
                        <p class="text-muted" style="margin-top: 1rem;">
                            ${this.t('error.fallback')}
                        </p>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Event listeners are handled via onclick in HTML for simplicity
        // Could be refactored to use addEventListener for better practice
    }
    
    /**
     * Show the wallet creator
     */
    show() {
        const container = document.getElementById(this.containerId);
        if (container) {
            container.style.display = 'block';
            this.debugService.log('🪴 Wallet creator shown', 'info');
        }
    }
    
    /**
     * Hide the wallet creator
     */
    hide() {
        const container = document.getElementById(this.containerId);
        if (container) {
            container.style.display = 'none';
            this.debugService.log('Wallet creator hidden', 'info');
        }
    }
    
    /**
     * Reset to initial state
     */
    reset() {
        this.currentStep = 'initial';
        this.walletData = null;
        this.render();
        this.attachEventListeners();
    }
    
    /**
     * Start wallet creation process
     */
    async startCreation() {
        try {
            // Get steward data from form
            const form = document.getElementById('stewardForm');
            if (!form) {
                throw new Error('Steward form not found');
            }
            
            const formData = new FormData(form);
            this.stewardData = {
                name: formData.get('name'),
                email: formData.get('email')
            };
            
            if (!this.stewardData.name || !this.stewardData.email) {
                throw new Error('Please fill in your name and email first');
            }
            
            // Update UI to creating state
            this.currentStep = 'creating';
            this.render();
            
            this.debugService.log('🔄 Creating wallet...', 'info');
            
            // Call API to create wallet
            const response = await this.apiService.post('/api/v2/stellar/create-wallet', {
                steward_email: this.stewardData.email,
                steward_name: this.stewardData.name
            });
            
            if (response.success) {
                this.walletData = response;
                this.currentStep = 'success';
                this.debugService.log('✓ Wallet created successfully', 'success');
            } else {
                throw new Error(response.error || 'Wallet creation failed');
            }
            
            this.render();
            this.attachEventListeners();
            
        } catch (error) {
            this.debugService.error('✗ Wallet creation failed:', error);
            alert(error.message || 'Wallet creation failed. Please try again.');
            this.currentStep = 'error';
            this.render();
            this.attachEventListeners();
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
            btn.textContent = this.t('buttons.copied');
            btn.style.background = '#10b981';
            
            setTimeout(() => {
                btn.textContent = originalText;
                btn.style.background = '';
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy:', err);
            alert('Failed to copy. Please manually select and copy the text.');
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
        const t = this.translations[this.language].success.downloadContent;
        const stewardName = document.getElementById('stewardForm')?.elements['name']?.value || 'Steward';
        
        const content = `${t.title}
${'='.repeat(t.title.length)}

${t.warning}

${t.created}: ${new Date().toISOString()}

${t.publicLabel}:
${this.walletData.public_key}

${t.secretLabel}:
${this.walletData.secret_key}

${t.network}: ${this.walletData.network}
${t.balance}: ${this.walletData.xlm_balance} XLM
${t.trustline}: ${this.walletData.trustline_created ? '✓' : '✗'}

---
Steward: ${stewardName}
Language: ${this.getLanguageName()}
Attribution: This project uses the services of Claude and Anthropic PBC.
`;
        
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `stellar-wallet-${this.walletData.public_key.slice(0, 8)}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.debugService.log('📥 Credentials downloaded', 'success');
    }
    
    /**
     * Confirm credentials have been saved
     */
    confirmSaved() {
        const confirmed = confirm(this.t('success.actions.lastChance'));
        
        if (confirmed) {
            // Auto-fill public key into form
            const stellarInput = document.getElementById('stellarWallet');
            if (stellarInput) {
                stellarInput.value = this.walletData.public_key;
                this.debugService.log('✓ Public key auto-filled', 'success');
            }
            
            // Hide modal
            this.hide();
            
            // Scroll to form
            const form = document.getElementById('stewardForm');
            if (form) {
                form.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }
    }
}

// Make it available globally
window.StellarWalletCreatorMultilingual = StellarWalletCreatorMultilingual;

/**
 * Attribution: This project uses the services of Claude and Anthropic PBC
 * to inform our decisions and recommendations.
 */
