/**
 * Arduino Configuration Generator
 * 
 * Generates Arduino/C++ configuration code for SenseBox devices.
 * Follows Design Principle #12 (Method Singularity) - Single implementation
 * 
 * Attribution: This project uses the services of Claude and Anthropic PBC.
 */

const ArduinoConfigGenerator = {
    /**
     * Generate complete Arduino configuration
     * @param {Array} sensors - Array of sensor identifiers
     * @param {string} observerId - Observer ID from registration
     * @param {string} serialNumber - Device serial number
     * @param {string} muxedWallet - Muxed Stellar wallet address (optional)
     * @returns {string} HTML string containing Arduino configuration
     */
    generateConfig(sensors, observerId, serialNumber, muxedWallet = null) {
        const config = this.buildConfigString(sensors, observerId, serialNumber, muxedWallet);
        
        return `
            <div class="arduino-config">
                <h4>📋 Arduino Configuration</h4>
                <button class="copy-btn" onclick="ArduinoConfigGenerator.copyToClipboard('${observerId}')">
                    📋 Copy
                </button>
                <pre id="arduino-config-${observerId}">${config}</pre>
            </div>
        `;
    },
    
    /**
     * Build configuration string
     * @param {Array} sensors - Sensor array
     * @param {string} observerId - Observer ID
     * @param {string} serialNumber - Serial number
     * @param {string} muxedWallet - Muxed wallet
     * @returns {string} Configuration code
     */
    buildConfigString(sensors, observerId, serialNumber, muxedWallet) {
        const apiHost = CONFIG.config.API_HOST;
        const apiPort = CONFIG.config.API_PORT;
        
        let config = `// ========================================
// Phenomenological Observer Configuration
// Generated: ${new Date().toLocaleString()}
// ========================================

// API Configuration
const char* PHENO_API_HOST = "${apiHost}";
const int PHENO_API_PORT = ${apiPort};
const char* OBSERVER_ID = "${observerId}";
const char* DEVICE_ID = "SENS_${serialNumber}";
const char* API_ENDPOINT = "/observe";

// Observation interval (15 minutes = 900000 milliseconds)
const unsigned long OBSERVATION_INTERVAL = 900000UL;
`;

        // Add muxed wallet if provided
        if (muxedWallet) {
            config += `\n// Muxed Stellar Wallet for UBEC rewards\nconst char* MUXED_WALLET = "${muxedWallet}";\n`;
        }
        
        config += '\n// ========================================\n';
        config += '// Active Sensors Configuration\n';
        config += '// ========================================\n';
        
        // Add sensor defines
        const sensorDefines = this.getSensorDefines(sensors);
        config += sensorDefines.join('\n');
        
        config += '\n\n// ========================================\n';
        config += '// Include Required Libraries\n';
        config += '// ========================================\n';
        
        const libraries = this.getRequiredLibraries(sensors);
        config += libraries.join('\n');
        
        config += '\n\n// ========================================\n';
        config += '// Sensor Initialization\n';
        config += '// ========================================\n';
        config += '// Initialize sensors in setup() function\n';
        config += '// See SenseBox documentation for details\n';
        
        return config;
    },
    
    /**
     * Get sensor define statements
     * @param {Array} sensors - Sensor identifiers
     * @returns {Array} Array of #define statements
     */
    getSensorDefines(sensors) {
        const sensorMap = {
            'hdc1080': '#define USE_HDC1080    // Temperature & Humidity',
            'bmp280': '#define USE_BMP280     // Pressure & Temperature (End of Life)',
            'dps310': '#define USE_DPS310     // Pressure & Temperature (Recommended)',
            'ltr329': '#define USE_LTR329     // Light Intensity',
            'veml6070': '#define USE_VEML6070   // UV Radiation',
            'smt50': '#define USE_SMT50      // Soil Moisture & Temperature',
            'water_temp_5m': '#define USE_WATER_TEMP // 5m Water Thermometer',
            'sds011': '#define USE_SDS011     // PM2.5 & PM10 Particulate Matter',
            'sps30': '#define USE_SPS30      // Advanced Particulate Matter',
            'rg15': '#define USE_RG15       // Hydreon Rain Sensor',
            'cam_m8q': '#define USE_GPS        // CAM-M8Q GPS Receiver'
        };
        
        return sensors
            .filter(sensor => sensorMap[sensor])
            .map(sensor => sensorMap[sensor]);
    },
    
    /**
     * Get required library includes
     * @param {Array} sensors - Sensor identifiers
     * @returns {Array} Array of #include statements
     */
    getRequiredLibraries(sensors) {
        const libraries = [
            '#include <WiFi.h>',
            '#include <HTTPClient.h>',
            '#include <Wire.h>'
        ];
        
        // Add sensor-specific libraries
        if (sensors.includes('hdc1080')) {
            libraries.push('#include <HDC100X.h>');
        }
        if (sensors.includes('bmp280') || sensors.includes('dps310')) {
            libraries.push('#include <Adafruit_BMP280.h>');
        }
        if (sensors.includes('ltr329')) {
            libraries.push('#include <LTR3xx.h>');
        }
        if (sensors.includes('veml6070')) {
            libraries.push('#include <Adafruit_VEML6070.h>');
        }
        if (sensors.includes('sds011')) {
            libraries.push('#include <SdsDustSensor.h>');
        }
        if (sensors.includes('sps30')) {
            libraries.push('#include <sps30.h>');
        }
        if (sensors.includes('cam_m8q')) {
            libraries.push('#include <SparkFun_u-blox_GNSS_Arduino_Library.h>');
        }
        
        return libraries;
    },
    
    /**
     * Copy configuration to clipboard
     * @param {string} observerId - Observer ID for element targeting
     */
    copyToClipboard(observerId) {
        const configElement = document.getElementById(`arduino-config-${observerId}`);
        if (!configElement) return;
        
        const configText = configElement.textContent;
        
        navigator.clipboard.writeText(configText).then(() => {
            // Find button and update text
            const btn = configElement.parentElement.querySelector('.copy-btn');
            if (btn) {
                const originalText = btn.textContent;
                btn.textContent = '✓ Copied!';
                btn.style.background = 'var(--success)';
                
                setTimeout(() => {
                    btn.textContent = originalText;
                    btn.style.background = '';
                }, 2000);
            }
            
            // Log success if debug service available
            if (CONFIG.hasService('debug')) {
                CONFIG.getService('debug').log('✓ Configuration copied to clipboard', 'success');
            }
        }).catch(error => {
            console.error('Copy failed:', error);
            alert('Failed to copy configuration. Please copy manually.');
        });
    },
    
    /**
     * Generate sample observation code
     * @param {Array} sensors - Active sensors
     * @returns {string} Sample code for sending observations
     */
    generateObservationSample(sensors) {
        return `
// Sample observation submission code
void sendObservation() {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        
        // Construct API URL
        String url = String("http://") + PHENO_API_HOST + ":" + 
                     String(PHENO_API_PORT) + API_ENDPOINT;
        
        http.begin(url);
        http.addHeader("Content-Type", "application/json");
        
        // Build JSON observation
        String payload = buildObservationJSON();
        
        int httpResponseCode = http.POST(payload);
        
        if (httpResponseCode > 0) {
            String response = http.getString();
            Serial.println("Response: " + response);
        } else {
            Serial.println("Error: " + String(httpResponseCode));
        }
        
        http.end();
    }
}
`;
    }
};

// Make available globally
window.ArduinoConfigGenerator = ArduinoConfigGenerator;

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ArduinoConfigGenerator };
}
