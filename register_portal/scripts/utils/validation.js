/**
 * Validation Utilities
 * 
 * Reusable validation functions for form inputs.
 * Follows Design Principle #12 (Method Singularity) - Each validation method appears once
 * 
 * Attribution: This project uses the services of Claude and Anthropic PBC.
 */

const ValidationUtils = {
    /**
     * Validate email address
     * @param {string} email - Email to validate
     * @returns {Object} Validation result
     */
    validateEmail(email) {
        if (!email || email.trim() === '') {
            return { valid: false, error: 'Email is required' };
        }
        
        if (!CONFIG.isValidEmail(email)) {
            return { valid: false, error: 'Invalid email format' };
        }
        
        return { valid: true };
    },
    
    /**
     * Validate Stellar wallet address
     * @param {string} address - Stellar address to validate
     * @param {boolean} required - Whether the field is required
     * @returns {Object} Validation result
     */
    validateStellarAddress(address, required = false) {
        if (!address || address.trim() === '') {
            if (required) {
                return { valid: false, error: 'Stellar address is required' };
            }
            return { valid: true }; // Optional field, empty is ok
        }
        
        if (!CONFIG.isValidStellarAddress(address)) {
            return { 
                valid: false, 
                error: 'Invalid Stellar address. Must start with G and be 56 characters' 
            };
        }
        
        return { valid: true };
    },
    
    /**
     * Validate required text field
     * @param {string} value - Value to validate
     * @param {string} fieldName - Field name for error message
     * @param {number} minLength - Minimum length (optional)
     * @param {number} maxLength - Maximum length (optional)
     * @returns {Object} Validation result
     */
    validateRequiredText(value, fieldName, minLength = 1, maxLength = null) {
        if (!value || value.trim() === '') {
            return { valid: false, error: `${fieldName} is required` };
        }
        
        if (value.length < minLength) {
            return { 
                valid: false, 
                error: `${fieldName} must be at least ${minLength} characters` 
            };
        }
        
        if (maxLength && value.length > maxLength) {
            return { 
                valid: false, 
                error: `${fieldName} must be less than ${maxLength} characters` 
            };
        }
        
        return { valid: true };
    },
    
    /**
     * Validate latitude coordinate
     * @param {string|number} lat - Latitude to validate
     * @returns {Object} Validation result
     */
    validateLatitude(lat) {
        if (lat === '' || lat === null || lat === undefined) {
            return { valid: false, error: 'Latitude is required' };
        }
        
        const numLat = parseFloat(lat);
        
        if (isNaN(numLat)) {
            return { valid: false, error: 'Latitude must be a number' };
        }
        
        if (numLat < -90 || numLat > 90) {
            return { valid: false, error: 'Latitude must be between -90 and 90' };
        }
        
        return { valid: true, value: numLat };
    },
    
    /**
     * Validate longitude coordinate
     * @param {string|number} lon - Longitude to validate
     * @returns {Object} Validation result
     */
    validateLongitude(lon) {
        if (lon === '' || lon === null || lon === undefined) {
            return { valid: false, error: 'Longitude is required' };
        }
        
        const numLon = parseFloat(lon);
        
        if (isNaN(numLon)) {
            return { valid: false, error: 'Longitude must be a number' };
        }
        
        if (numLon < -180 || numLon > 180) {
            return { valid: false, error: 'Longitude must be between -180 and 180' };
        }
        
        return { valid: true, value: numLon };
    },
    
    /**
     * Validate form group and display error
     * @param {HTMLElement} formGroup - Form group element
     * @param {Object} validationResult - Validation result
     * @returns {boolean} True if valid
     */
    applyValidationResult(formGroup, validationResult) {
        if (!formGroup) return false;
        
        // Remove existing error state
        formGroup.classList.remove('has-error', 'has-success');
        
        const errorElement = formGroup.querySelector('.error-message');
        if (errorElement) {
            errorElement.textContent = '';
        }
        
        if (!validationResult.valid) {
            formGroup.classList.add('has-error');
            if (errorElement) {
                errorElement.textContent = validationResult.error;
            }
            return false;
        }
        
        formGroup.classList.add('has-success');
        return true;
    },
    
    /**
     * Validate entire form
     * @param {HTMLFormElement} form - Form element
     * @param {Object} validators - Object mapping field names to validator functions
     * @returns {Object} Validation results
     */
    validateForm(form, validators) {
        const formData = new FormData(form);
        const errors = {};
        let isValid = true;
        
        for (const [fieldName, validator] of Object.entries(validators)) {
            const value = formData.get(fieldName);
            const result = validator(value);
            
            if (!result.valid) {
                errors[fieldName] = result.error;
                isValid = false;
                
                // Apply visual feedback to form group
                const input = form.querySelector(`[name="${fieldName}"]`);
                if (input) {
                    const formGroup = input.closest('.form-group');
                    if (formGroup) {
                        this.applyValidationResult(formGroup, result);
                    }
                }
            }
        }
        
        return { valid: isValid, errors };
    },
    
    /**
     * Clear all validation states in a form
     * @param {HTMLFormElement} form - Form element
     */
    clearValidation(form) {
        const formGroups = form.querySelectorAll('.form-group');
        formGroups.forEach(group => {
            group.classList.remove('has-error', 'has-success');
            const errorMsg = group.querySelector('.error-message');
            if (errorMsg) {
                errorMsg.textContent = '';
            }
        });
    }
};

// Make available globally
window.ValidationUtils = ValidationUtils;

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ValidationUtils };
}
