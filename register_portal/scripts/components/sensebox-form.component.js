/**
 * SenseBox Form Component
 * 
 * Handles SenseBox device registration form rendering and submission.
 * Follows Design Principle #1 (Modular Design) and #10 (Separation of Concerns)
 * 
 * Attribution: This project uses the services of Claude and Anthropic PBC.
 */

class SenseBoxFormComponent {
    constructor() {
        this.formId = 'senseboxRegistrationForm';
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
                <div class="form-icon">📡</div>
                <div class="form-title">
                    <h3>Register SenseBox Device</h3>
                    <p>Connect your environmental sensor to the stewardship network</p>
                </div>
            </div>

            <div id="sensebox-status" class="status-message"></div>

            <form id="${this.formId}" class="form-grid">
                <div class="form-row">
                    <div class="form-group">
                        <label for="sensebox-serial">
                            SenseBox Serial Number *
                            <span class="tooltip">ℹ
                                <span class="tooltiptext">Your OpenSenseMap ID or device serial</span>
                            </span>
                        </label>
                        <input type="text" id="sensebox-serial" name="serial_number" 
                               placeholder="e.g., 68b11e9c48183d0008742820" required>
                        <span class="error-message"></span>
                    </div>
                    <div class="form-group">
                        <label for="sensebox-name">Device Name *</label>
                        <input type="text" id="sensebox-name" name="device_name" 
                               placeholder="e.g., School Garden Monitor" required>
                        <span class="error-message"></span>
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label for="location-name">Location Name *</label>
                        <input type="text" id="location-name" name="location_name" 
                               placeholder="e.g., School Garden Frankfurt Oder" required>
                        <span class="error-message"></span>
                    </div>
                    <div class="form-group">
                        <label for="timezone">Timezone</label>
                        <select id="timezone" name="timezone">
                            <option value="Europe/Berlin" selected>Europe/Berlin</option>
                            <option value="UTC">UTC</option>
                            <option value="Europe/London">Europe/London</option>
                            <option value="Europe/Paris">Europe/Paris</option>
                            <option value="America/New_York">America/New York</option>
                        </select>
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label for="latitude">Latitude *</label>
                        <input type="number" id="latitude" name="latitude" 
                               step="0.000001" placeholder="e.g., 52.3476" required>
                        <span class="error-message"></span>
                    </div>
                    <div class="form-group">
                        <label for="longitude">Longitude *</label>
                        <input type="number" id="longitude" name="longitude" 
                               step="0.000001" placeholder="e.g., 14.5506" required>
                        <span class="error-message"></span>
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label for="steward-email-device">Steward Email</label>
                        <input type="email" id="steward-email-device" name="steward_email" 
                               placeholder="Steward's email address">
                        <span class="error-message"></span>
                    </div>
                    <div class="form-group">
                        <label for="steward-stellar-device">
                            Steward Stellar Wallet *
                            <span class="tooltip">ℹ
                                <span class="tooltiptext">A unique muxed address will be created for this device</span>
                            </span>
                        </label>
                        <input type="text" id="steward-stellar-device" name="steward_stellar" 
                               required placeholder="G..." pattern="^G[A-Z2-7]{55}$">
                        <span class="error-message"></span>
                    </div>
                </div>

                ${this.renderSensorCategories()}

                <div class="form-actions">
                    <button type="button" class="btn btn-secondary" id="sensebox-clear-btn">
                        Clear Form
                    </button>
                    <button type="submit" class="btn btn-primary">
                        📡 Register Device
                    </button>
                </div>
            </form>

            <div id="sensebox-response" class="response-container"></div>
        `;
        
        const container = document.getElementById('formContainer');
        const section = document.createElement('div');
        section.id = 'sensebox-form';
        section.className = 'form-section';
        section.innerHTML = html;
        container.appendChild(section);
    }
    
    /**
     * Render sensor selection categories
     * @returns {string} HTML for sensor categories
     */
    renderSensorCategories() {
        return `
            <div class="sensor-category">
                <h4>🌡️ Environmental Sensors</h4>
                <div class="sensor-grid">
                    <label class="sensor-checkbox selected">
                        <input type="checkbox" name="sensors" value="hdc1080" checked>
                        <span>Temperature & Humidity (HDC1080)</span>
                    </label>
                    <label class="sensor-checkbox">
                        <input type="checkbox" name="sensors" value="bmp280">
                        <span>Air Pressure (BMP280 - EoL)</span>
                    </label>
                    <label class="sensor-checkbox selected">
                        <input type="checkbox" name="sensors" value="dps310" checked>
                        <span>Air Pressure (DPS310)</span>
                    </label>
                    <label class="sensor-checkbox selected">
                        <input type="checkbox" name="sensors" value="ltr329" checked>
                        <span>Light Intensity (LTR329)</span>
                    </label>
                    <label class="sensor-checkbox selected">
                        <input type="checkbox" name="sensors" value="veml6070" checked>
                        <span>UV Radiation (VEML6070)</span>
                    </label>
                </div>
            </div>

            <div class="sensor-category">
                <h4>🌿 Soil & Water Sensors</h4>
                <div class="sensor-grid">
                    <label class="sensor-checkbox selected">
                        <input type="checkbox" name="sensors" value="smt50" checked>
                        <span>Soil Moisture & Temp (SMT50)</span>
                    </label>
                    <label class="sensor-checkbox">
                        <input type="checkbox" name="sensors" value="water_temp_5m">
                        <span>Water Temperature (5m depth)</span>
                    </label>
                </div>
            </div>

            <div class="sensor-category">
                <h4>💨 Air Quality Sensors</h4>
                <div class="sensor-grid">
                    <label class="sensor-checkbox">
                        <input type="checkbox" name="sensors" value="sds011">
                        <span>PM2.5 & PM10 (SDS011)</span>
                    </label>
                    <label class="sensor-checkbox">
                        <input type="checkbox" name="sensors" value="sps30">
                        <span>PM1.0/2.5/4.0/10 (SPS30)</span>
                    </label>
                </div>
            </div>

            <div class="sensor-category">
                <h4>🌧️ Weather & Location Sensors</h4>
                <div class="sensor-grid">
                    <label class="sensor-checkbox">
                        <input type="checkbox" name="sensors" value="rg15">
                        <span>Rain Sensor (Hydreon RG-15)</span>
                    </label>
                    <label class="sensor-checkbox">
                        <input type="checkbox" name="sensors" value="cam_m8q">
                        <span>GPS Receiver (CAM-M8Q)</span>
                    </label>
                </div>
            </div>
        `;
    }
    
    /**
     * Attach event listeners
     */
    attachEventListeners() {
        this.form = document.getElementById(this.formId);
        this.statusElement = document.getElementById('sensebox-status');
        this.responseElement = document.getElementById('sensebox-response');
        
        if (this.form) {
            this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        }
        
        const clearBtn = document.getElementById('sensebox-clear-btn');
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
        
        this.debugService.log('📡 Starting SenseBox registration...', 'info');
        
        // Clear previous validation
        ValidationUtils.clearValidation(this.form);
        
        // Validate form
        const validation = this.validateForm();
        if (!validation.valid) {
            this.showStatus('Please fix the errors before submitting', 'error');
            return;
        }
        
        // Prepare data
        const senseboxData = this.prepareData();
        
        try {
            this.showStatus('Registering SenseBox as environmental observer...', 'info');
            
            const result = await this.apiService.registerObserver(senseboxData);
            
            this.debugService.log(`✅ SenseBox registered! ID: ${result.observer_id}`, 'success');
            
            this.showStatus('✓ SenseBox registered successfully!', 'success');
            this.displayResponse(result, senseboxData);
            
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
        
        // Validate serial number
        const serialResult = ValidationUtils.validateRequiredText(
            formData.get('serial_number'), 'Serial Number', 3, 50
        );
        const serialGroup = this.form.querySelector('[name="serial_number"]').closest('.form-group');
        if (!ValidationUtils.applyValidationResult(serialGroup, serialResult)) {
            isValid = false;
        }
        
        // Validate device name
        const nameResult = ValidationUtils.validateRequiredText(
            formData.get('device_name'), 'Device Name', 2, 100
        );
        const nameGroup = this.form.querySelector('[name="device_name"]').closest('.form-group');
        if (!ValidationUtils.applyValidationResult(nameGroup, nameResult)) {
            isValid = false;
        }
        
        // Validate location name
        const locationResult = ValidationUtils.validateRequiredText(
            formData.get('location_name'), 'Location Name', 2, 100
        );
        const locationGroup = this.form.querySelector('[name="location_name"]').closest('.form-group');
        if (!ValidationUtils.applyValidationResult(locationGroup, locationResult)) {
            isValid = false;
        }
        
        // Validate coordinates
        const latResult = ValidationUtils.validateLatitude(formData.get('latitude'));
        const latGroup = this.form.querySelector('[name="latitude"]').closest('.form-group');
        if (!ValidationUtils.applyValidationResult(latGroup, latResult)) {
            isValid = false;
        }
        
        const lonResult = ValidationUtils.validateLongitude(formData.get('longitude'));
        const lonGroup = this.form.querySelector('[name="longitude"]').closest('.form-group');
        if (!ValidationUtils.applyValidationResult(lonGroup, lonResult)) {
            isValid = false;
        }
        
        // Validate stellar address (required)
        const stellarResult = ValidationUtils.validateStellarAddress(
            formData.get('steward_stellar'), true
        );
        const stellarGroup = this.form.querySelector('[name="steward_stellar"]').closest('.form-group');
        if (!ValidationUtils.applyValidationResult(stellarGroup, stellarResult)) {
            isValid = false;
        }
        
        // Validate steward email (optional)
        const email = formData.get('steward_email');
        if (email && email.trim() !== '') {
            const emailResult = ValidationUtils.validateEmail(email);
            const emailGroup = this.form.querySelector('[name="steward_email"]').closest('.form-group');
            if (!ValidationUtils.applyValidationResult(emailGroup, emailResult)) {
                isValid = false;
            }
        }
        
        return { valid: isValid };
    }
    
    /**
     * Prepare registration data
     * @returns {Object} Formatted data for API
     */
    prepareData() {
        const formData = new FormData(this.form);
        const sensors = formData.getAll('sensors');
        
        // Map sensor capabilities
        const sensorCapabilities = {
            temperature: sensors.some(s => ['hdc1080', 'bmp280', 'dps310', 'smt50', 'water_temp_5m'].includes(s)),
            humidity: sensors.includes('hdc1080'),
            pressure: sensors.some(s => ['bmp280', 'dps310'].includes(s)),
            light: sensors.includes('ltr329'),
            uv: sensors.includes('veml6070'),
            moisture: sensors.includes('smt50'),
            particulate: sensors.some(s => ['sds011', 'sps30'].includes(s)),
            rain: sensors.includes('rg15'),
            gps: sensors.includes('cam_m8q')
        };
        
        return {
            observer_type: 'device',
            external_identity: {
                device_id: `SENS_${formData.get('serial_number')}`,
                name: formData.get('device_name'),
                serial: formData.get('serial_number'),
                steward_email: formData.get('steward_email') || null
            },
            essence: {
                location: {
                    lat: parseFloat(formData.get('latitude')),
                    lon: parseFloat(formData.get('longitude'))
                },
                location_name: formData.get('location_name'),
                sensors: sensors,
                timezone: formData.get('timezone'),
                steward_stellar: formData.get('steward_stellar'),
                registered_at: new Date().toISOString()
            },
            sensory_capacities: {
                sight: false,
                hearing: false,
                touch: false,
                smell: false,
                taste: false,
                intuition: false,
                technological: true,
                ...sensorCapabilities
            }
        };
    }
    
    /**
     * Display registration response
     * @param {Object} result - API response
     * @param {Object} originalData - Original form data
     */
    displayResponse(result, originalData) {
        const sensors = originalData.essence.sensors;
        const arduinoConfig = ArduinoConfigGenerator.generateConfig(
            sensors,
            result.observer_id,
            originalData.external_identity.serial,
            result.muxed_wallet
        );
        
        const html = `
            <div class="response-header">📡 Device Registered with ${sensors.length} Sensors!</div>
            <div class="credentials-box">
                <div class="credential-item">
                    <span class="credential-label">Observer ID:</span>
                    <span class="credential-value">${result.observer_id}</span>
                </div>
                <div class="credential-item">
                    <span class="credential-label">Device ID:</span>
                    <span class="credential-value">${originalData.external_identity.device_id}</span>
                </div>
                <div class="credential-item">
                    <span class="credential-label">API Endpoint:</span>
                    <span class="credential-value">${CONFIG.getApiUrl()}/observe</span>
                </div>
                ${result.muxed_wallet ? `
                <div class="credential-item">
                    <span class="credential-label">Muxed Wallet:</span>
                    <span class="credential-value">${result.muxed_wallet}</span>
                </div>` : ''}
            </div>
            ${arduinoConfig}
            <p style="margin-top: 1rem; color: var(--text-light);">
                Your SenseBox is now part of the stewardship network. Each observation 
                contributes 7.14 UBECrc to the reciprocal economy.
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
const senseboxFormComponent = new SenseBoxFormComponent();

// Make available globally
window.senseboxFormComponent = senseboxFormComponent;

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SenseBoxFormComponent, senseboxFormComponent };
}
