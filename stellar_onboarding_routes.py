#!/usr/bin/env python3
"""
Stellar Onboarding API Routes
Handles wallet creation and funding requests from registration portal

Design Principles Applied:
- Principle #2: Service pattern - router only, no standalone execution
- Principle #3: Service registry for dependencies
- Principle #5: Strict async operations
- Principle #10: Clear separation of concerns

Attribution: This project uses the services of Claude and Anthropic PBC to inform our 
decisions and recommendations. This project was made possible with the assistance of 
Claude and Anthropic PBC.
"""

import logging
from typing import Dict, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, EmailStr, Field

logger = logging.getLogger(__name__)

# Create router with prefix
router = APIRouter(prefix="/api/v2/stellar", tags=["stellar-onboarding"])


# Request/Response Models
class WalletCreationRequest(BaseModel):
    """Request to create a new Stellar wallet"""
    steward_email: EmailStr
    steward_name: str = Field(..., min_length=2, max_length=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "steward_email": "steward@school.edu",
                "steward_name": "Maria Schmidt"
            }
        }


class WalletCreationResponse(BaseModel):
    """Response with new wallet credentials"""
    success: bool
    public_key: str
    secret_key: str  # CRITICAL: Only send over HTTPS!
    xlm_balance: float
    trustline_created: bool
    network: str
    warning: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "public_key": "GABC...XYZ",
                "secret_key": "SABC...XYZ",
                "xlm_balance": 5.5,
                "trustline_created": True,
                "network": "public",
                "warning": None
            }
        }


class TrustlineRequest(BaseModel):
    """Request to add UBECrc trustline to existing wallet"""
    public_key: str = Field(..., min_length=56, max_length=56, pattern="^G[A-Z2-7]{55}$")
    secret_key: str = Field(..., min_length=56, max_length=56, pattern="^S[A-Z2-7]{55}$")


class FundingStatusResponse(BaseModel):
    """Response with funding account status"""
    configured: bool
    xlm_balance: Optional[float] = None
    accounts_possible: Optional[int] = None
    warning: Optional[str] = None
    error: Optional[str] = None


# Dependency: Get onboarding service from app state
async def get_onboarding_service(request: Request):
    """
    Retrieve onboarding service from app state
    Following Principle #3: Service registry for dependencies
    """
    if not hasattr(request.app.state, 'stellar_onboarding'):
        logger.error("Stellar onboarding service not initialized in app.state")
        raise HTTPException(
            status_code=503,
            detail="Stellar onboarding service unavailable. Please check server configuration."
        )
    
    service = request.app.state.stellar_onboarding
    if service is None:
        logger.error("Stellar onboarding service is None")
        raise HTTPException(
            status_code=503,
            detail="Stellar onboarding service not configured. Please contact administrator."
        )
    
    return service


# API Routes

@router.post("/create-wallet", response_model=WalletCreationResponse)
async def create_wallet(
    request: WalletCreationRequest,
    service = Depends(get_onboarding_service)
):
    """
    Create a new Stellar wallet for a steward
    - Generates keypair
    - Funds account with 5+ XLM
    - Adds UBECrc trustline
    
    **IMPORTANT**: Secret key is returned ONCE. Store it securely!
    """
    logger.info(f"Creating wallet for {request.steward_name} ({request.steward_email})")
    
    try:
        result = await service.create_and_fund_account(
            steward_email=request.steward_email,
            steward_name=request.steward_name
        )
        
        if not result or not result.get('success'):
            raise HTTPException(
                status_code=500,
                detail="Failed to create and fund wallet. Please try again or contact support."
            )
        
        # Add warning if trustline creation failed
        warning = None
        if not result.get('trustline_created'):
            warning = "Account funded but UBECrc trustline failed. You can add it later."
            logger.warning(f"Trustline creation failed for {request.steward_email}")
        
        logger.info(f"✓ Wallet created successfully for {request.steward_email}")
        logger.info(f"  Public key: {result['public_key']}")
        logger.info(f"  XLM balance: {result['xlm_balance']}")
        logger.info(f"  Trustline: {result['trustline_created']}")
        
        return WalletCreationResponse(
            success=True,
            public_key=result['public_key'],
            secret_key=result['secret_key'],
            xlm_balance=result['xlm_balance'],
            trustline_created=result['trustline_created'],
            network=result.get('network', 'public'),
            warning=warning
        )
        
    except Exception as e:
        logger.error(f"Error creating wallet: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Wallet creation failed: {str(e)}"
        )


@router.post("/onboarding/create", response_model=WalletCreationResponse)
async def create_wallet_alt(
    request: WalletCreationRequest,
    service = Depends(get_onboarding_service)
):
    """
    Alternative endpoint path for wallet creation (for compatibility)
    Redirects to main create-wallet endpoint
    """
    return await create_wallet(request, service)


@router.post("/add-trustline")
async def add_trustline(
    request: TrustlineRequest,
    service = Depends(get_onboarding_service)
):
    """
    Add UBECrc trustline to existing Stellar wallet
    
    Use this if:
    - You already have a Stellar account
    - Trustline creation failed during wallet creation
    - You want to receive UBECrc tokens
    """
    logger.info(f"Adding trustline for account: {request.public_key[:8]}...")
    
    try:
        success = await service.add_trustline_to_existing_account(
            public_key=request.public_key,
            secret_key=request.secret_key
        )
        
        if success:
            logger.info(f"✓ Trustline added successfully for {request.public_key[:8]}...")
            return {
                "success": True,
                "message": "UBECrc trustline added successfully",
                "public_key": request.public_key
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to add trustline. Account may not exist or may already have the trustline."
            )
            
    except Exception as e:
        logger.error(f"Error adding trustline: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Trustline creation failed: {str(e)}"
        )


@router.get("/funding-status", response_model=FundingStatusResponse)
async def get_funding_status(service = Depends(get_onboarding_service)):
    """
    Check the funding account status
    
    Returns:
    - Current XLM balance
    - Number of accounts that can be created
    - Warnings if balance is low
    """
    try:
        status = await service.check_funding_capacity()
        
        return FundingStatusResponse(
            configured=True,
            xlm_balance=status.get('xlm_balance'),
            accounts_possible=status.get('wallets_can_create'),
            warning=status.get('warning'),
            error=None
        )
        
    except Exception as e:
        logger.error(f"Error checking funding status: {e}", exc_info=True)
        return FundingStatusResponse(
            configured=False,
            xlm_balance=None,
            accounts_possible=None,
            warning=None,
            error=str(e)
        )


@router.get("/check-account/{public_key}")
async def check_account_exists(
    public_key: str,
    service = Depends(get_onboarding_service)
):
    """
    Check if a Stellar account exists
    
    Useful for:
    - Verifying wallet creation success
    - Checking if account is already funded
    - Validating public keys
    """
    try:
        exists = await service.has_stellar_account(public_key)
        
        return {
            "public_key": public_key,
            "exists": exists,
            "message": "Account found" if exists else "Account not found"
        }
        
    except Exception as e:
        logger.error(f"Error checking account: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check account: {str(e)}"
        )


"""
Attribution: This project uses the services of Claude and Anthropic PBC
to inform our decisions and recommendations. This project was made
possible with the assistance of Claude and Anthropic PBC.
"""
