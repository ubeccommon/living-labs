/**
 * Steward Form Component
 * 
 * Handles steward registration form rendering and submission.
 * Follows Design Principle #1 (Modular Design) and #10 (Separation of Concerns)
 * 
 * Attribution: This project uses the services of Claude and Anthropic PBC.
 */

class StewardFormComponent {
    constructor() {
        this.formId = 'stewardRegistrationForm';
        this.form = null;
        this.statusElement = null;
        this.responseElement = null;
        this.debugService = null;
        this.apiService = null;
    }
    
    /**
     * Initialize component
     */
    initialize() {
        this.debugService = CONFIG.getService('debug');
        this.apiService = CONFIG.getService('api');
        this.render();
        this.attachEventListeners();
    }
    
    /**
     * Render form HTML
     */
    render() {
        const html = `
            <div class="form-header">
                <div class="form-icon">🌍</div>
                <div class="form-title">
                    <h3>Become an Environmental Steward</h3>
                    <p>Join our phenomenological observation network as a conscious steward of the Earth</p>
                </div>
            </div>

            <div id="steward-status" class="status-message"></div>

            <form id="${this.formId}" class="form-grid">
                <div class="form-row">
                    <div class="form-group">
                        <label for="steward-name">Full Name *</label>
                        <input type="text" id="steward-name" name="name" required>
                        <span class="error-message"></span>
                    </div>
                    <div class="form-group">
                        <label for="steward-email">Email Address *</label>
                        <input type="email" id="steward-email" name="email" required>
                        <span class="error-message"></span>
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label for="steward-organization">Organization/School</label>
                        <input type="text" id="steward-organization" name="organization" 
                               placeholder="e.g., Freie Waldorfschule Frankfurt (Oder)">
                    </div>
                    <div class="form-group">
                        <label for="steward-role">Stewardship Role</label>
                        <select id="steward-role" name="role">
                            <option value="steward">Environmental Steward</option>
                            <option value="guardian">Land Guardian</option>
                            <option value="observer">Phenomenon Observer</option>
                            <option value="student">Student Researcher</option>
                            <option value="teacher">Teacher Guide</option>
                            <option value="researcher">Scientific Researcher</option>
                        </select>
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label for="steward-stellar">
                            Stellar Wallet Address
                            <span class="tooltip">ℹ
                                <span class="tooltiptext">For receiving UBEC tokens in reciprocal exchange for your observations</span>
                            </span>
                        </label>
                        <input type="text" id="steward-stellar" name="stellar_address" 
                               placeholder="G..." pattern="^G[A-Z2-7]{55}$">
                        <span class="error-message"></span>
                    </div>
                    <div class="form-group">
                        <label for="steward-land">Land Relationship</label>
                        <input type="text" id="steward-land" name="land_relationship" 
                               placeholder="Describe your relationship with the land">
                    </div>
                </div>

                <div class="form-group">
                    <label>Sensory Capacities</label>
                    <div class="sensor-grid">
                        <label class="sensor-checkbox selected">
                            <input type="checkbox" name="capacities" value="sight" checked>
                            <span>👁️ Sight</span>
                        </label>
                        <label class="sensor-checkbox selected">
                            <input type="checkbox" name="capacities" value="hearing" checked>
                            <span>👂 Hearing</span>
                        </label>
                        <label class="sensor-checkbox selected">
                            <input type="checkbox" name="capacities" value="touch" checked>
                            <span>✋ Touch</span>
                        </label>
                        <label class="sensor-checkbox selected">
                            <input type="checkbox" name="capacities" value="smell" checked>
                            <span>👃 Smell</span>
                        </label>
                        <label class="sensor-checkbox">
                            <input type="checkbox" name="capacities" value="taste">
                            <span>👅 Taste</span>
                        </label>
                        <label class="sensor-checkbox selected">
                            <input type="checkbox" name="capacities" value="intuition" checked>
                            <span>💭 Intuition</span>
                        </label>
                    </div>
                </div>

                <div class="form-actions">
                    <button type="button" class="btn btn-secondary" id="steward-clear-btn">
                        Clear Form
                    </button>
                    <button type="submit" class="btn btn-primary">
                        🌟 Begin Stewardship Journey
                    </button>
                </div>
            </form>

            <div id="steward-response" class="response-container"></div>
        `;
        
        const container = document.getElementById('formContainer');
        const section = document.createElement('div');
        section.id = 'steward-form';
        section.className = 'form-section active';
        section.innerHTML = html;
        container.appendChild(section);
    }
    
    /**
     * Attach event listeners
     */
    attachEventListeners() {
        this.form = document.getElementById(this.formId);
        this.statusElement = document.getElementById('steward-status');
        this.responseElement = document.getElementById('steward-response');
        
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        }
        
        const clearBtn = document.getElementById('steward-clear-btn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clearForm());
        }
        
        // Add checkbox visual feedback
        const checkboxes = this.form.querySelectorAll('.sensor-checkbox');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('click', () => {
                const input = checkbox.querySelector('input');
                checkbox.classList.toggle('selected', input.checked);
            });
        });
    }
    
    /**
     * Handle form submission
     * @param {Event} e - Submit event
     */
    async handleSubmit(e) {
        e.preventDefault();
        
        this.debugService.log('🚀 Starting steward registration...', 'info');
        
        // Clear previous validation
        ValidationUtils.clearValidation(this.form);
        
        // Validate form
        const validation = this.validateForm();
        if (!validation.valid) {
            this.showStatus('Please fix the errors before submitting', 'error');
            return;
        }
        
        // Prepare data
        const stewardData = this.prepareData();
        
        try {
            this.showStatus('Connecting to the stewardship network...', 'info');
            
            const result = await this.apiService.registerObserver(stewardData);
            
            this.debugService.log(`✅ Steward registered! ID: ${result.observer_id}`, 'success');
            
            this.showStatus('✓ Steward registered successfully!', 'success');
            this.displayResponse(result, stewardData);
            
        } catch (error) {
            this.debugService.log(`💥 Registration failed: ${error.message}`, 'error');
            this.showStatus(`Error: ${error.message}`, 'error');
        }
    }
    
    /**
     * Validate form inputs
     * @returns {Object} Validation result
     */
    validateForm() {
        const formData = new FormData(this.form);
        let isValid = true;
        
        // Validate name
        const nameResult = ValidationUtils.validateRequiredText(
            formData.get('name'), 'Name', 2, 100
        );
        const nameGroup = this.form.querySelector('[name="name"]').closest('.form-group');
        if (!ValidationUtils.applyValidationResult(nameGroup, nameResult)) {
            isValid = false;
        }
        
        // Validate email
        const emailResult = ValidationUtils.validateEmail(formData.get('email'));
        const emailGroup = this.form.querySelector('[name="email"]').closest('.form-group');
        if (!ValidationUtils.applyValidationResult(emailGroup, emailResult)) {
            isValid = false;
        }
        
        // Validate Stellar address (optional)
        const stellarResult = ValidationUtils.validateStellarAddress(
            formData.get('stellar_address'), false
        );
        const stellarGroup = this.form.querySelector('[name="stellar_address"]').closest('.form-group');
        if (!ValidationUtils.applyValidationResult(stellarGroup, stellarResult)) {
            isValid = false;
        }
        
        return { valid: isValid };
    }
    
    /**
     * Prepare registration data
     * @returns {Object} Formatted data for API
     */
    prepareData() {
        const formData = new FormData(this.form);
        const capacities = formData.getAll('capacities');
        
        const sensoryCapacities = {
            sight: capacities.includes('sight'),
            hearing: capacities.includes('hearing'),
            touch: capacities.includes('touch'),
            smell: capacities.includes('smell'),
            taste: capacities.includes('taste'),
            intuition: capacities.includes('intuition'),
            technological: false
        };
        
        return {
            observer_type: 'human',
            external_identity: {
                name: formData.get('name'),
                email: formData.get('email'),
                role: formData.get('role') || 'steward',
                type: 'steward'
            },
            essence: {
                organization: formData.get('organization') || 'UBEC',
                stellar_address: formData.get('stellar_address') || '',
                land_relationship: formData.get('land_relationship') || '',
                registered_at: new Date().toISOString()
            },
            sensory_capacities: sensoryCapacities
        };
    }
    
    /**
     * Display registration response
     * @param {Object} result - API response
     * @param {Object} originalData - Original form data
     */
    displayResponse(result, originalData) {
        const html = `
            <div class="response-header">🎉 Welcome to the Stewardship Network!</div>
            <div class="credentials-box">
                <div class="credential-item">
                    <span class="credential-label">Observer ID:</span>
                    <span class="credential-value">${result.observer_id}</span>
                </div>
                <div class="credential-item">
                    <span class="credential-label">Name:</span>
                    <span class="credential-value">${originalData.external_identity.name}</span>
                </div>
                <div class="credential-item">
                    <span class="credential-label">Role:</span>
                    <span class="credential-value">${originalData.external_identity.role}</span>
                </div>
                ${result.muxed_wallet ? `
                <div class="credential-item">
                    <span class="credential-label">Muxed Wallet:</span>
                    <span class="credential-value">${result.muxed_wallet}</span>
                </div>` : ''}
            </div>
            <p style="margin-top: 1rem; color: var(--text-light);">
                You are now a recognized steward of the Earth. Your observations contribute to our 
                phenomenological understanding of the environment.
            </p>
        `;
        
        this.responseElement.innerHTML = html;
        this.responseElement.classList.add('active');
    }
    
    /**
     * Show status message
     * @param {string} message - Status message
     * @param {string} type - Message type (info, success, error)
     */
    showStatus(message, type = 'info') {
        this.statusElement.className = `status-message ${type} active`;
        this.statusElement.textContent = message;
    }
    
    /**
     * Clear form and reset state
     */
    clearForm() {
        this.form.reset();
        this.statusElement.classList.remove('active');
        this.responseElement.classList.remove('active');
        ValidationUtils.clearValidation(this.form);
        
        // Reset checkbox visual states
        const checkboxes = this.form.querySelectorAll('.sensor-checkbox');
        checkboxes.forEach(checkbox => {
            const input = checkbox.querySelector('input');
            checkbox.classList.toggle('selected', input.checked);
        });
    }
}

// Create and export instance
const stewardFormComponent = new StewardFormComponent();

// Make available globally
window.stewardFormComponent = stewardFormComponent;

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { StewardFormComponent, stewardFormComponent };
}
