# Stellar Onboarding - Quick Migration Checklist

## Files to Move to Production

Copy these NEW files to your production environment:

```bash
# Core service and API
cp /home/claude/stellar_onboarding_service.py /path/to/production/
cp /home/claude/stellar_onboarding_routes.py /path/to/production/

# Frontend components
cp /home/claude/register_portal/scripts/components/stellar-wallet-creator.component.js /path/to/production/register_portal/scripts/components/
cp /home/claude/register_portal/styles/stellar-wallet-creator.css /path/to/production/register_portal/styles/

# Documentation
cp /home/claude/STELLAR_ONBOARDING_INTEGRATION.md /path/to/production/docs/
```

---

## Files to MODIFY

### 1. `.env` - Add Configuration

```bash
# Add at end of file:

# ==================================================
# Stellar Onboarding Configuration
# ==================================================
STELLAR_FUNDING_PUBLIC=YOUR_FUNDING_ACCOUNT_PUBLIC_KEY
STELLAR_FUNDING_SECRET=YOUR_FUNDING_ACCOUNT_SECRET_KEY
STELLAR_ONBOARDING_ENABLED=true
STELLAR_MIN_FUNDING_AMOUNT=5.0
```

### 2. `config.py` - Add Configuration Class

**Location**: After existing Stellar configuration

```python
class StellarOnboardingConfig:
    """Configuration for Stellar account creation and funding"""
    
    enabled: bool = os.getenv('STELLAR_ONBOARDING_ENABLED', 'false').lower() == 'true'
    funding_public: str = os.getenv('STELLAR_FUNDING_PUBLIC', '')
    funding_secret: str = os.getenv('STELLAR_FUNDING_SECRET', '')
    min_funding_amount: Decimal = Decimal(os.getenv('STELLAR_MIN_FUNDING_AMOUNT', '5.0'))
    
    @property
    def is_configured(self) -> bool:
        return bool(self.enabled and self.funding_public and self.funding_secret)

# In main Config class:
stellar_onboarding = StellarOnboardingConfig()
```

### 3. `service_registry.py` - Register Service

**Location**: Add new initialization function

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
    logger.info("Stellar onboarding service initialized")
    return service
```

**Location**: In `ServiceRegistry.__init__` or startup method

```python
# Add after existing service registrations:
stellar_onboarding = await initialize_stellar_onboarding(config)
if stellar_onboarding:
    self.register('stellar_onboarding', stellar_onboarding)
```

### 4. `main.py` - Register Router

**Location**: After existing router imports

```python
from stellar_onboarding_routes import router as stellar_onboarding_router
```

**Location**: After existing router registrations

```python
app.include_router(stellar_onboarding_router)
logger.info("✓ Stellar onboarding routes registered")
```

### 5. `register_portal/steward-en.html` - Update Frontend

**Location**: In `<head>` section

```html
<!-- Add Stellar wallet creator styles -->
<link rel="stylesheet" href="styles/stellar-wallet-creator.css">
```

**Location**: Before closing `</body>` tag, in scripts section

```html
<script src="scripts/components/stellar-wallet-creator.component.js"></script>

<script>
    // Add to existing initialization code:
    const walletCreator = new StellarWalletCreator(
        'wallet-creator-container',
        apiService,
        debugService
    );
    walletCreator.init();
    
    function showWalletCreator() {
        const container = document.getElementById('wallet-creator-container');
        container.style.display = 'block';
        container.scrollIntoView({ behavior: 'smooth' });
    }
</script>
```

**Location**: In the Stellar wallet section of the form

```html
<div class="form-section">
    <h3>Stellar Wallet Setup</h3>
    
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

<!-- Wallet Creator Container -->
<div id="wallet-creator-container" style="display: none;"></div>
```

---

## Pre-Deployment Testing

### 1. Test Configuration
```bash
# Verify environment variables
cat .env | grep STELLAR_FUNDING

# Should show:
# STELLAR_FUNDING_PUBLIC=G...
# STELLAR_FUNDING_SECRET=S...
```

### 2. Test Service Initialization
```bash
# Start application
python main.py

# Look for log messages:
# "Stellar onboarding service initialized"
# "✓ Stellar onboarding routes registered"
```

### 3. Test API Endpoints
```bash
# Test funding status
curl http://localhost:8000/api/v2/stellar/funding-status

# Should return:
# {
#   "configured": true,
#   "xlm_balance": ...,
#   "accounts_possible": ...,
# }
```

### 4. Test Frontend
1. Navigate to http://localhost:8000/steward
2. Fill in name and email
3. Click "Create Wallet for Me"
4. Verify wallet creation flow works

---

## Production Deployment Steps

### Step 1: Prepare Funding Account
```bash
# Create new Stellar account for funding
# OR use existing distributor account
# Fund with at least 100 XLM

# Add UBECrc trustline (if needed)
# Get public and secret keys
```

### Step 2: Update Production Config
```bash
# Update .env with production values
STELLAR_NETWORK=public
STELLAR_FUNDING_PUBLIC=<mainnet_funding_public>
STELLAR_FUNDING_SECRET=<mainnet_funding_secret>
```

### Step 3: Deploy Code
```bash
# Stop application
systemctl stop ubec-api

# Copy new files
# Modify existing files as per checklist above

# Restart application
systemctl start ubec-api

# Check logs
journalctl -u ubec-api -f
```

### Step 4: Verify Deployment
```bash
# Test API
curl https://your-domain.com/api/v2/stellar/funding-status

# Test frontend
# Visit https://your-domain.com/steward
# Try wallet creation
```

---

## Monitoring After Deployment

### Daily Checks
- [ ] Check funding account balance
- [ ] Review wallet creation logs
- [ ] Monitor error rates

### Weekly Tasks
- [ ] Refill funding account if below threshold
- [ ] Review user feedback on wallet creation
- [ ] Update documentation based on issues

### Commands for Monitoring
```bash
# Check funding account balance
curl https://your-domain.com/api/v2/stellar/funding-status | jq

# View recent wallet creations (if logging implemented)
grep "Wallet created" /var/log/ubec/app.log | tail -n 10

# Check for errors
grep "ERROR" /var/log/ubec/app.log | grep "stellar_onboarding"
```

---

## Rollback Plan

If issues arise:

### Quick Rollback
```bash
# 1. Disable feature via config
STELLAR_ONBOARDING_ENABLED=false

# 2. Restart application
systemctl restart ubec-api

# 3. Old registration form still works
# Users can manually enter existing wallets
```

### Full Rollback
```bash
# 1. Remove new files
rm stellar_onboarding_service.py
rm stellar_onboarding_routes.py
rm register_portal/scripts/components/stellar-wallet-creator.component.js
rm register_portal/styles/stellar-wallet-creator.css

# 2. Revert modified files from git
git checkout config.py service_registry.py main.py
git checkout register_portal/steward-en.html

# 3. Restart
systemctl restart ubec-api
```

---

## Success Metrics

Track these metrics post-deployment:

- **Wallet Creation Rate**: How many users choose auto-creation vs manual entry
- **Success Rate**: Percentage of successful wallet creations
- **Time to Create**: Average time from click to completion
- **Funding Account Usage**: XLM depletion rate
- **User Satisfaction**: Feedback on ease of use

---

## Support & Troubleshooting

### Common Issues

**Issue**: "Funding account not configured"
- **Fix**: Verify STELLAR_FUNDING_PUBLIC and SECRET are set in .env

**Issue**: "Failed to fund account"
- **Fix**: Check funding account has sufficient XLM (>5 per account)

**Issue**: "Trustline creation failed"
- **Fix**: Account is funded, trustline can be added later via separate endpoint

**Issue**: Frontend shows error
- **Fix**: Check browser console, verify API is accessible

---

## Checklist Complete? ✅

- [ ] All new files copied to production
- [ ] .env updated with funding credentials
- [ ] config.py modified with onboarding class
- [ ] service_registry.py registers service
- [ ] main.py includes router
- [ ] steward-en.html updated with component
- [ ] Tested on staging/local environment
- [ ] Funding account prepared and funded
- [ ] Monitoring in place
- [ ] Rollback plan documented
- [ ] Team trained on new feature

**Ready to deploy!** 🚀

---

**Attribution**: This migration checklist was created with the assistance of Claude and Anthropic PBC.
