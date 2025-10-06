# Stellar Onboarding Service Integration Guide

## Overview

This guide details how to integrate the Stellar Onboarding Service into the UBEC registration portal. The service guides new stewards through wallet creation, automatically funds accounts with 5 XLM, and sets up UBECrc trustlines.

**Attribution**: This project uses the services of Claude and Anthropic PBC to inform our decisions and recommendations. This project was made possible with the assistance of Claude and Anthropic PBC.

---

## Architecture Compliance

### Design Principles Applied

✅ **Principle #1 (Modular Design)**: Each component is self-contained with clear boundaries  
✅ **Principle #2 (Service Pattern)**: All modules are services, only `main.py` executes  
✅ **Principle #3 (Service Registry)**: Dependencies managed through central registry  
✅ **Principle #4 (Single Source of Truth)**: Database is authoritative  
✅ **Principle #5 (Strict Async)**: All I/O operations use async/await  
✅ **Principle #10 (Separation of Concerns)**: Clear layers for business logic, API, and UI  
✅ **Principle #12 (Method Singularity)**: No duplicate methods across codebase  

---

## File Structure

```
/home/claude/
├── stellar_onboarding_service.py       # Core service (NEW)
├── stellar_onboarding_routes.py        # API routes (NEW)
├── main.py                             # Add router registration here
└── config.py                           # Add configuration here

/home/claude/register_portal/
├── scripts/
│   └── components/
│       └── stellar-wallet-creator.component.js  # Frontend component (NEW)
├── styles/
│   └── stellar-wallet-creator.css               # Component styles (NEW)
└── steward-en.html                              # Update to include component
```

---

## Step 1: Update Configuration

### Add to `.env` file:

```bash
# ==================================================
# Stellar Onboarding Configuration
# ==================================================

# Funding Source Account (distributes XLM to new accounts)
# This can be the same as DISTRIBUTOR account or a dedicated funding account
STELLAR_FUNDING_PUBLIC=GDGQ4KNH22PZEN4G27HHDQ7LLQVFCO7CQUND7SMK7VH4YTHUVXEJUBEC
STELLAR_FUNDING_SECRET=YOUR_FUNDING_SECRET_KEY_HERE

# UBECrc Token Configuration (already exists, reference here)
UBECRC_ASSET_CODE=UBECrc
UBECRC_ISSUER=GAWLPSGBZVQP4ZMIKBN6DXHO6RRWWFP6F2BNRW52YALJOH7P7UJSUBEC

# Onboarding Settings
STELLAR_ONBOARDING_ENABLED=true
STELLAR_MIN_FUNDING_AMOUNT=5.0  # Minimum XLM to fund new accounts
```

### Add to `config.py`:

```python
# Stellar Onboarding Configuration
class StellarOnboardingConfig:
    """Configuration for Stellar account creation and funding"""
    
    enabled: bool = os.getenv('STELLAR_ONBOARDING_ENABLED', 'false').lower() == 'true'
    funding_public: str = os.getenv('STELLAR_FUNDING_PUBLIC', '')
    funding_secret: str = os.getenv('STELLAR_FUNDING_SECRET', '')
    min_funding_amount: Decimal = Decimal(os.getenv('STELLAR_MIN_FUNDING_AMOUNT', '5.0'))
    
    @property
    def is_configured(self) -> bool:
        return bool(self.enabled and self.funding_public and self.funding_secret)

# Add to main Config class
stellar_onboarding = StellarOnboardingConfig()
```

---

## Step 2: Register Service in Service Registry

### Update `service_registry.py`:

```python
from stellar_onboarding_service import StellarOnboardingService

async def initialize_stellar_onboarding(config):
    """Initialize Stellar onboarding service"""
    if not config.stellar_onboarding.is_configured:
        logger.warning("Stellar onboarding not configured")
        return None
    
    onboarding_config = {
        'stellar_horizon_url': config.stellar.horizon_url,
        'stellar_network': config.stellar.network,
        'funding_source_public': config.stellar_onboarding.funding_public,
        'funding_source_secret': config.stellar_onboarding.funding_secret,
        'ubecrc_asset_code': 'UBECrc',
        'ubecrc_issuer': config.stellar.ubecrc_issuer
    }
    
    service = StellarOnboardingService(onboarding_config)
    
    # Check funding account status
    status = await service.check_funding_account_balance()
    if status.get('warning'):
        logger.warning(f"Onboarding service: {status['warning']}")
    
    logger.info("Stellar onboarding service initialized")
    return service

# Add to ServiceRegistry.__init__
async def __init__(self):
    # ... existing code ...
    
    # Initialize Stellar onboarding service
    stellar_onboarding = await initialize_stellar_onboarding(config)
    if stellar_onboarding:
        self.register('stellar_onboarding', stellar_onboarding)
```

---

## Step 3: Register API Routes in main.py

### Update `main.py`:

```python
from stellar_onboarding_routes import router as stellar_onboarding_router

# Add after existing router registrations
app.include_router(stellar_onboarding_router)

logger.info("✓ Stellar onboarding routes registered")
```

---

## Step 4: Update Registration Portal Frontend

### Update `register_portal/steward-en.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Existing head content -->
    
    <!-- Add Stellar wallet creator styles -->
    <link rel="stylesheet" href="styles/stellar-wallet-creator.css">
</head>
<body>
    <!-- Existing header and navigation -->
    
    <div class="container">
        <div class="registration-container">
            <h1>🌱 Steward Registration</h1>
            
            <!-- EXISTING FORM FIELDS (name, email, organization, role) -->
            
            <!-- NEW: Stellar Wallet Section -->
            <div class="form-section">
                <h3>Stellar Wallet Setup</h3>
                
                <!-- Option 1: Let user enter existing wallet -->
                <div class="form-group">
                    <label for="stellarWallet">
                        Stellar Wallet Address
                        <span class="optional">(Optional - we can create one for you)</span>
                    </label>
                    <input 
                        type="text" 
                        id="stellarWallet" 
                        name="stellar_address" 
                        placeholder="G..." 
                        pattern="^G[A-Z2-7]{55}$"
                    >
                    <div class="hint">Your UBECrc tokens will be sent here</div>
                </div>
                
                <!-- Option 2: Link to wallet creator -->
                <div class="wallet-creation-link">
                    <p>Don't have a Stellar wallet?</p>
                    <button 
                        type="button" 
                        class="btn btn-secondary" 
                        onclick="showWalletCreator()"
                    >
                        Create Wallet for Me →
                    </button>
                </div>
            </div>
            
            <!-- Wallet Creator Container (hidden initially) -->
            <div id="wallet-creator-container" style="display: none;"></div>
            
            <!-- Rest of form (sensory capacities, etc.) -->
            
        </div>
    </div>
    
    <!-- Scripts -->
    <script src="scripts/config.js"></script>
    <script src="scripts/utils/debug.js"></script>
    <script src="scripts/services/api.service.js"></script>
    <script src="scripts/components/stellar-wallet-creator.component.js"></script>
    <script src="scripts/components/steward-form.component.js"></script>
    
    <script>
        // Initialize services
        const debugService = new DebugService();
        const apiService = new APIService(CONFIG.API_BASE, debugService);
        
        // Initialize wallet creator (but don't show yet)
        const walletCreator = new StellarWalletCreator(
            'wallet-creator-container',
            apiService,
            debugService
        );
        walletCreator.init();
        
        // Function to show wallet creator
        function showWalletCreator() {
            const container = document.getElementById('wallet-creator-container');
            container.style.display = 'block';
            container.scrollIntoView({ behavior: 'smooth' });
        }
        
        // Initialize steward form
        const stewardForm = new StewardFormComponent(
            'steward-registration-form',
            apiService,
            debugService
        );
        stewardForm.init();
    </script>
</body>
</html>
```

---

## Step 5: Database Updates (Optional)

If you want to track wallet creation in the database:

```sql
-- Add to phenomenological schema

-- Track wallet creation events
CREATE TABLE IF NOT EXISTS wallet_creations (
    id SERIAL PRIMARY KEY,
    observer_id INTEGER REFERENCES observers(id),
    public_key TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    xlm_funded NUMERIC(10, 2),
    trustline_created BOOLEAN DEFAULT FALSE,
    network TEXT DEFAULT 'public'
);

-- Index for quick lookups
CREATE INDEX idx_wallet_creations_observer ON wallet_creations(observer_id);
CREATE INDEX idx_wallet_creations_public_key ON wallet_creations(public_key);
```

---

## Step 6: Testing the Integration

### 6.1 Backend Testing

```bash
# Start the application
python main.py

# Test funding account status
curl http://localhost:8000/api/v2/stellar/funding-status

# Test wallet creation (replace with real email/name)
curl -X POST http://localhost:8000/api/v2/stellar/create-wallet \
  -H "Content-Type: application/json" \
  -d '{
    "steward_email": "test@school.edu",
    "steward_name": "Test Steward"
  }'
```

### 6.2 Frontend Testing

1. Navigate to `http://localhost:8000/steward`
2. Fill in name and email fields
3. Click "Create Wallet for Me"
4. Verify wallet creation flow:
   - ✓ Shows creating animation
   - ✓ Displays public and secret keys
   - ✓ Shows security warnings
   - ✓ Download credentials works
   - ✓ Public key fills into form

### 6.3 Integration Testing

```python
# tests/test_stellar_onboarding.py
import pytest
from stellar_onboarding_service import StellarOnboardingService

@pytest.mark.asyncio
async def test_wallet_creation():
    config = {
        'stellar_horizon_url': 'https://horizon-testnet.stellar.org',
        'stellar_network': 'testnet',
        'funding_source_public': 'YOUR_TESTNET_PUBLIC',
        'funding_source_secret': 'YOUR_TESTNET_SECRET',
        'ubecrc_asset_code': 'UBECrc',
        'ubecrc_issuer': 'TESTNET_ISSUER'
    }
    
    service = StellarOnboardingService(config)
    
    result = await service.create_and_fund_account(
        steward_email='test@example.com',
        steward_name='Test User'
    )
    
    assert result is not None
    assert result['success'] is True
    assert result['public_key'].startswith('G')
    assert result['secret_key'].startswith('S')
    assert result['funded'] is True
    assert float(result['xlm_balance']) >= 5.0
```

---

## Step 7: Security Considerations

### 7.1 Secret Key Handling

**CRITICAL**: The secret key is shown ONCE to the user. Follow these rules:

- ✅ **Never log secret keys** in application logs
- ✅ **Never store secret keys** in the database
- ✅ **Always use HTTPS** in production
- ✅ **Educate users** about secret key security
- ✅ **Implement download option** so users can save credentials

### 7.2 Rate Limiting

```python
# Add to stellar_onboarding_routes.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/create-wallet")
@limiter.limit("5/hour")  # Max 5 wallet creations per hour per IP
async def create_wallet(...):
    # ... existing code ...
```

### 7.3 Monitoring

```python
# Add monitoring for funding account
import asyncio

async def monitor_funding_account():
    """Background task to monitor funding account balance"""
    while True:
        service = ServiceRegistry().get('stellar_onboarding')
        if service:
            status = await service.check_funding_account_balance()
            
            if status.get('warning'):
                logger.warning(f"⚠️ {status['warning']}")
                # Send alert to admin (email, Slack, etc.)
            
            if status.get('accounts_possible', 0) < 5:
                logger.error("❌ CRITICAL: Funding account almost depleted!")
                # Send urgent alert
        
        await asyncio.sleep(3600)  # Check every hour

# Add to main.py startup
@app.on_event("startup")
async def startup():
    asyncio.create_task(monitor_funding_account())
```

---

## Step 8: Production Deployment

### 8.1 Environment Setup

```bash
# Production .env
STELLAR_NETWORK=public
STELLAR_FUNDING_PUBLIC=<production_funding_account>
STELLAR_FUNDING_SECRET=<production_funding_secret>
STELLAR_ONBOARDING_ENABLED=true
```

### 8.2 Funding Account Preparation

1. Create dedicated funding account on Stellar mainnet
2. Fund with sufficient XLM (100+ XLM recommended)
3. Add UBECrc trustline to funding account (if needed)
4. Test with small amount first

### 8.3 Monitoring Dashboard

Create admin endpoint to monitor onboarding:

```python
@router.get("/admin/onboarding-stats")
async def get_onboarding_stats(service: StellarOnboardingService = Depends(...)):
    """Admin endpoint for onboarding statistics"""
    status = await service.check_funding_account_balance()
    
    return {
        "funding_account": {
            "balance": status.get('xlm_balance'),
            "accounts_possible": status.get('accounts_possible'),
            "warning": status.get('warning')
        },
        "wallets_created_today": await get_wallets_created_today(),
        "total_wallets_created": await get_total_wallets_created()
    }
```

---

## Troubleshooting

### Issue: Wallet creation fails

**Solution**:
1. Check funding account has sufficient XLM
2. Verify network configuration (testnet vs mainnet)
3. Check Horizon server connectivity
4. Review logs for specific error messages

### Issue: Trustline creation fails

**Solution**:
1. Account was funded but trustline failed - user can add later
2. Check UBECrc issuer public key is correct
3. Verify account has minimum XLM for trustline reserve

### Issue: Frontend not showing wallet creator

**Solution**:
1. Verify CSS file is loaded
2. Check JavaScript console for errors
3. Ensure API endpoints are accessible
4. Verify CORS settings in main.py

---

## API Endpoints Reference

### POST /api/v2/stellar/create-wallet
Creates new wallet, funds it, adds trustline

**Request**:
```json
{
  "steward_email": "user@example.com",
  "steward_name": "John Doe"
}
```

**Response**:
```json
{
  "success": true,
  "public_key": "GABC...XYZ",
  "secret_key": "SABC...XYZ",
  "xlm_balance": 5.5,
  "trustline_created": true,
  "network": "public"
}
```

### POST /api/v2/stellar/add-trustline
Adds UBECrc trustline to existing account

**Request**:
```json
{
  "public_key": "GABC...XYZ",
  "secret_key": "SABC...XYZ"
}
```

### GET /api/v2/stellar/funding-status
Check funding account status

**Response**:
```json
{
  "configured": true,
  "xlm_balance": 150.5,
  "accounts_possible": 27,
  "warning": null
}
```

### GET /api/v2/stellar/check-account/{public_key}
Verify if account exists on network

---

## Success Criteria

✅ New stewards can create wallets in <30 seconds  
✅ Accounts are funded with 5+ XLM automatically  
✅ UBECrc trustline is added automatically  
✅ Users receive clear security instructions  
✅ Credentials can be downloaded securely  
✅ Public key is auto-filled in registration form  
✅ Funding account is monitored for depletion  
✅ All operations follow async patterns  
✅ Service is registered in service registry  
✅ No duplicate code across modules  

---

## Next Steps

1. **User Education**: Create tutorial videos on Stellar wallet security
2. **Recovery Process**: Implement account recovery documentation
3. **Multi-language**: Translate wallet creator to German
4. **Mobile Support**: Optimize wallet creator for mobile devices
5. **Advanced Features**: Add hardware wallet support for advanced users

---

**Attribution**: This integration guide was created with the assistance of Claude and Anthropic PBC.
