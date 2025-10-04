// sensebox_registration_muxed.js
// Enhanced SenseBox registration handler with Stellar muxed account support

async function registerSenseBox(event) {
    event.preventDefault();
    
    const statusEl = document.getElementById('sensebox-status');
    const responseEl = document.getElementById('sensebox-response');
    
    // Get form data
    const formData = new FormData(event.target);
    const sensors = formData.getAll('sensors');
    
    // Get owner's Stellar wallet (required for muxed accounts)
    const ownerStellar = formData.get('owner_stellar') || prompt('Please enter your Stellar wallet address (G...)');
    
    if (!ownerStellar || !ownerStellar.startsWith('G')) {
        statusEl.className = 'status-message error';
        statusEl.textContent = 'Error: Valid Stellar wallet address required (must start with G)';
        statusEl.style.display = 'block';
        return;
    }
    
    const senseboxData = {
        observer_type: 'device',
        external_identity: {
            device_id: `SENS_${formData.get('serial_number')}`,
            serial_number: formData.get('serial_number'),
            name: formData.get('name'),
            owner_email: formData.get('owner_email')
        },
        essence: {
            location: {
                lat: parseFloat(formData.get('latitude')),
                lon: parseFloat(formData.get('longitude'))
            },
            location_name: formData.get('location_name'),
            sensors: sensors,
            timezone: formData.get('timezone'),
            owner_stellar: ownerStellar,  // User's main wallet
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
            temperature: sensors.includes('temperature'),
            humidity: sensors.includes('humidity'),
            pressure: sensors.includes('pressure'),
            light: sensors.includes('light'),
            soil: sensors.includes('soil_moisture')
        }
    };

    try {
        statusEl.className = 'status-message';
        statusEl.textContent = 'Registering SenseBox and creating muxed account...';
        statusEl.style.display = 'block';

        const response = await fetch(`${API_BASE}/api/v2/observers/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(senseboxData)
        });

        const result = await response.json();

        if (response.ok && result.success) {
            statusEl.className = 'status-message success';
            statusEl.textContent = '✓ SenseBox registered with muxed account!';
            
            responseEl.innerHTML = `
                <div class="response-header">📡 Device Registered with Muxed Account!</div>
                <div class="credentials-box">
                    <div class="credential-item">
                        <span class="credential-label">Observer ID:</span>
                        <span class="credential-value">${result.observer_id}</span>
                    </div>
                    <div class="credential-item">
                        <span class="credential-label">Device ID:</span>
                        <span class="credential-value">SENS_${formData.get('serial_number')}</span>
                    </div>
                    <div class="credential-item">
                        <span class="credential-label">Owner Wallet (Main):</span>
                        <span class="credential-value" style="font-size: 0.8em;">${ownerStellar}</span>
                    </div>
                    ${result.muxed_wallet ? `
                    <div class="credential-item">
                        <span class="credential-label">Device Muxed Wallet:</span>
                        <span class="credential-value" style="font-size: 0.8em; color: #4CAF50;">${result.muxed_wallet}</span>
                    </div>
                    ` : ''}
                    <div class="credential-item">
                        <span class="credential-label">API Endpoint:</span>
                        <span class="credential-value">${API_BASE}/observe</span>
                    </div>
                </div>
                <div style="margin-top: 1rem; padding: 1rem; background: #E8F5E9; border-radius: 8px; border: 1px solid #4CAF50;">
                    <strong>🎯 Muxed Account Benefits:</strong><br>
                    • All UBEC rewards for this device go to your main wallet<br>
                    • Device contributions are tracked individually<br>
                    • No separate wallet management needed<br>
                    • Perfect for managing multiple devices
                </div>
                <p style="margin-top: 1rem; color: var(--text-light);">
                    <strong>Important:</strong> Configure your SenseBox to send observations to the endpoint above.
                    Your device now has its own muxed Stellar address while all rewards flow to your main wallet.
                </p>
            `;
            responseEl.classList.add('active');
        } else {
            statusEl.className = 'status-message error';
            statusEl.textContent = `Error: ${result.detail || result.error || 'Registration failed'}`;
        }
    } catch (error) {
        statusEl.className = 'status-message error';
        statusEl.textContent = `Error: ${error.message}`;
    }
}

// Function to validate Stellar address
function validateStellarAddress(address) {
    // Basic validation - starts with G and is 56 characters
    return address && address.startsWith('G') && address.length === 56;
}

// Function to show muxed account explanation
function showMuxedInfo() {
    alert(`
Stellar Multiplexed Accounts Explained:

When you register a SenseBox, we create a special "muxed" address for it.

• Your main wallet: G... (receives all funds)
• Device muxed address: M... (virtual address for tracking)

Benefits:
✓ Track rewards per device
✓ All funds go to your main wallet
✓ No extra accounts to manage
✓ Perfect for multiple devices

Example:
If you have 3 SenseBoxes, each gets its own M... address,
but all UBEC tokens go to your single G... wallet.
    `);
}
