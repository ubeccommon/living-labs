#!/usr/bin/env python3
"""
Stellar Onboarding API Routes - WITH SECURITY
Integrates wallet security system to prevent abuse

New Features:
- Rate limiting by IP and email
- CAPTCHA validation
- Suspicious pattern detection
- Manual approval queue for high-risk requests
- Comprehensive logging

Design Principles Applied:
- Principle #2: Service pattern with centralized execution
- Principle #3: Service registry for dependencies
- Principle #5: Strict async operations
- Principle #10: Clear separation of concerns

Attribution: This project uses the services of Claude and Anthropic PBC.
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v2/stellar", tags=["stellar", "onboarding"])


# ==================================================
# REQUEST MODELS
# ==================================================

class CreateWalletRequest(BaseModel):
    """Request to create new Stellar wallet"""
    steward_email: EmailStr = Field(..., description="Steward email address")
    steward_name: str = Field(..., min_length=2, max_length=255, description="Steward name")
    organization: Optional[str] = Field(None, max_length=255, description="Organization/School name")
    captcha_token: Optional[str] = Field(None, description="CAPTCHA token from frontend")


class AddTrustlineRequest(BaseModel):
    """Request to add UBECrc trustline to existing account"""
    public_key: str = Field(..., min_length=56, max_length=56, pattern="^G[A-Z2-7]{55}$")
    secret_key: str = Field(..., min_length=56, max_length=56, pattern="^S[A-Z2-7]{55}$")


# ==================================================
# RESPONSE MODELS
# ==================================================

class WalletCreationResponse(BaseModel):
    """Response from wallet creation"""
    success: bool
    public_key: Optional[str] = None
    secret_key: Optional[str] = None
    xlm_balance: Optional[float] = None
    trustline_created: Optional[bool] = None
    network: Optional[str] = None
    creation_transaction: Optional[str] = None  # NEW: metadata support
    immutable_memo: Optional[str] = None  # NEW: metadata support
    metadata_added: Optional[bool] = None  # NEW: metadata support
    message: Optional[str] = None
    error: Optional[str] = None
    requires_approval: Optional[bool] = False  # NEW: security
    risk_score: Optional[int] = None  # NEW: security


class SecurityStatusResponse(BaseModel):
    """Security check status"""
    allowed: bool
    reason: str
    risk_score: int
    requires_approval: bool = False


# ==================================================
# DEPENDENCY INJECTION
# ==================================================

async def get_onboarding_service(request: Request):
    """Get onboarding service from request state"""
    if not hasattr(request.app.state, 'stellar_onboarding_service'):
        raise HTTPException(
            status_code=503,
            detail="Stellar onboarding service not available"
        )
    return request.app.state.stellar_onboarding_service


async def get_security_service(request: Request):
    """Get security service from request state"""
    if not hasattr(request.app.state, 'wallet_security_service'):
        raise HTTPException(
            status_code=503,
            detail="Security service not available"
        )
    return request.app.state.wallet_security_service


async def get_client_ip(request: Request) -> str:
    """
    Get client IP address, handling proxies correctly
    
    Checks headers in order:
    1. X-Forwarded-For (behind proxy)
    2. X-Real-IP (nginx)
    3. request.client.host (direct)
    """
    # Check if behind proxy
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        # X-Forwarded-For can contain multiple IPs, take the first (client)
        return forwarded.split(',')[0].strip()
    
    # Check X-Real-IP (nginx)
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip
    
    # Direct connection
    return request.client.host if request.client else 'unknown'


# ==================================================
# ROUTES
# ==================================================

@router.post("/create-wallet", response_model=WalletCreationResponse)
async def create_wallet(
    wallet_request: CreateWalletRequest,
    request: Request,
    onboarding_service = Depends(get_onboarding_service),
    security_service = Depends(get_security_service)
):
    """
    Create new Stellar wallet with funding and trustline
    
    **Security Features:**
    - Rate limiting by IP and email
    - CAPTCHA validation (optional but recommended)
    - Suspicious pattern detection
    - Manual approval for high-risk requests
    
    **Process:**
    1. Security validation
    2. Generate keypair
    3. Fund account (5+ XLM)
    4. Add metadata (attribution)
    5. Add UBECrc trustline
    6. Return credentials
    
    **Rate Limits:**
    - 1 wallet per email (ever)
    - 1 wallet per IP per hour
    - 3 wallets per IP per day
    """
    try:
        # Get client IP
        client_ip = await get_client_ip(request)
        
        logger.info(f"Wallet creation request from {client_ip}: {wallet_request.steward_email}")
        
        # ==================================================
        # SECURITY VALIDATION (NEW!)
        # ==================================================
        
        security_check = await security_service.validate_wallet_request(
            email=wallet_request.steward_email,
            name=wallet_request.steward_name,
            ip_address=client_ip,
            captcha_token=wallet_request.captcha_token,
            organization=wallet_request.organization
        )
        
        # Handle high-risk requests
        if not security_check.allowed:
            # Record failed attempt
            await security_service.record_failed_attempt(
                email=wallet_request.steward_email,
                ip_address=client_ip,
                reason=security_check.reason,
                risk_score=security_check.risk_score
            )
            
            # Return appropriate response
            if security_check.requires_manual_approval:
                logger.warning(
                    f"Wallet request requires approval: {wallet_request.steward_email} "
                    f"(risk: {security_check.risk_score})"
                )
                return WalletCreationResponse(
                    success=False,
                    message="Your request requires manual review. You'll be notified via email.",
                    requires_approval=True,
                    risk_score=security_check.risk_score
                )
            else:
                logger.warning(
                    f"Wallet request rejected: {wallet_request.steward_email} - "
                    f"{security_check.reason}"
                )
                return WalletCreationResponse(
                    success=False,
                    error=security_check.reason,
                    risk_score=security_check.risk_score
                )
        
        # ==================================================
        # CREATE WALLET (Security passed!)
        # ==================================================
        
        logger.info(
            f"Creating wallet for {wallet_request.steward_email} "
            f"(risk: {security_check.risk_score})"
        )
        
        result = await onboarding_service.create_and_fund_account(
            steward_email=wallet_request.steward_email,
            steward_name=wallet_request.steward_name
        )
        
        if result and result.get('success'):
            # Record successful creation
            await security_service.record_wallet_creation(
                email=wallet_request.steward_email,
                ip_address=client_ip,
                public_key=result['public_key'],
                risk_score=security_check.risk_score
            )
            
            logger.info(
                f"✓ Wallet created successfully: {result['public_key'][:8]}... "
                f"for {wallet_request.steward_email}"
            )
            
            return WalletCreationResponse(
                success=True,
                public_key=result['public_key'],
                secret_key=result['secret_key'],
                xlm_balance=result.get('xlm_balance'),
                trustline_created=result.get('trustline_created'),
                network=result.get('network'),
                creation_transaction=result.get('creation_transaction'),
                immutable_memo=result.get('immutable_memo'),
                metadata_added=result.get('metadata_added'),
                message="Wallet created successfully!",
                risk_score=security_check.risk_score
            )
        else:
            # Creation failed
            error_msg = result.get('error', 'Wallet creation failed') if result else 'Wallet creation failed'
            
            await security_service.record_failed_attempt(
                email=wallet_request.steward_email,
                ip_address=client_ip,
                reason=f"Creation failed: {error_msg}",
                risk_score=security_check.risk_score
            )
            
            logger.error(f"Wallet creation failed: {error_msg}")
            
            return WalletCreationResponse(
                success=False,
                error=error_msg
            )
            
    except Exception as e:
        logger.error(f"Wallet creation error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Wallet creation failed: {str(e)}"
        )


@router.post("/add-trustline")
async def add_trustline(
    trustline_request: AddTrustlineRequest,
    request: Request,
    onboarding_service = Depends(get_onboarding_service)
):
    """
    Add UBECrc trustline to existing Stellar account
    
    **Note:** This doesn't require the same security checks as wallet creation
    since the user already has an account and is just adding a trustline.
    """
    try:
        success = await onboarding_service.add_trustline_to_existing_account(
            public_key=trustline_request.public_key,
            secret_key=trustline_request.secret_key
        )
        
        if success:
            logger.info(f"✓ Trustline added: {trustline_request.public_key[:8]}...")
            return {
                "success": True,
                "message": "UBECrc trustline added successfully"
            }
        else:
            return {
                "success": False,
                "error": "Failed to add trustline"
            }
            
    except Exception as e:
        logger.error(f"Trustline error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Trustline creation failed: {str(e)}"
        )


@router.get("/funding-status")
async def get_funding_status(
    request: Request,
    onboarding_service = Depends(get_onboarding_service)
):
    """
    Check funding account status
    
    Returns:
    - Current XLM balance
    - Number of wallets that can be created
    - Warning if balance is low
    """
    try:
        status = await onboarding_service.check_funding_capacity()
        return status
        
    except Exception as e:
        logger.error(f"Funding status error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check funding status: {str(e)}"
        )


@router.get("/check-account/{public_key}")
async def check_account_exists(
    public_key: str,
    request: Request,
    onboarding_service = Depends(get_onboarding_service)
):
    """
    Check if a Stellar account exists on the network
    
    Args:
        public_key: Stellar public key (G...)
    
    Returns:
        exists: boolean indicating if account exists
    """
    try:
        # Validate public key format
        if not public_key.startswith('G') or len(public_key) != 56:
            raise HTTPException(
                status_code=400,
                detail="Invalid Stellar public key format"
            )
        
        exists = await onboarding_service.has_stellar_account(public_key)
        
        return {
            "exists": exists,
            "public_key": public_key
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Account check error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check account: {str(e)}"
        )


@router.get("/security-check")
async def security_status_check(
    request: Request,
    email: str,
    security_service = Depends(get_security_service)
):
    """
    Check security status for an email/IP without creating wallet
    
    **Admin use only** - helps debug security issues
    
    Args:
        email: Email to check
    
    Returns:
        Security check result with risk score and reasons
    """
    try:
        client_ip = await get_client_ip(request)
        
        security_check = await security_service.validate_wallet_request(
            email=email,
            name="Security Check",
            ip_address=client_ip,
            captcha_token=None
        )
        
        return SecurityStatusResponse(
            allowed=security_check.allowed,
            reason=security_check.reason,
            risk_score=security_check.risk_score,
            requires_approval=security_check.requires_manual_approval
        )
        
    except Exception as e:
        logger.error(f"Security check error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Security check failed: {str(e)}"
        )


"""
Attribution: This project uses the services of Claude and Anthropic PBC
to inform our decisions and recommendations. This project was made
possible with the assistance of Claude and Anthropic PBC.
"""
