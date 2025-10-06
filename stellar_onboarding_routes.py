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
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from stellar_onboarding_service import StellarOnboardingService

logger = logging.getLogger(__name__)

# Create router
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


# Dependency: Get onboarding service from registry
async def get_onboarding_service() -> StellarOnboardingService:
    """
    Retrieve onboarding service from service registry
    Following Principle #3: Service registry for dependencies
    """
    from service_registry import ServiceRegistry
    
    registry = ServiceRegistry()
    service = registry.get('stellar_onboarding')
    
    if not service:
        logger.error("Stellar onboarding service not registered")
        raise HTTPException(
            status_code=503,
            detail="Stellar onboarding service unavailable"
        )
    
    return service


# API Routes

@router.post("/create-wallet", response_model=WalletCreationResponse)
async def create_wallet(
    request: WalletCreationRequest,
    service: StellarOnboardingService = Depends(get_onboarding_service)
):
    """
    Create a new Stellar wallet for a steward
    - Generates keypair
    - Funds account with 5+ XLM
    - Adds UBECrc trustline
    
    **IMPORTANT**: Secret key is returned ONCE. Store it securely!
    """
    logger.info(f"Creating wallet for {request.steward_name} ({request.steward_email})")
    
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
    
    return WalletCreationResponse(
        success=True,
        public_key=result['public_key'],
        secret_key=result['secret_key'],
        xlm_balance=float(result['xlm_balance']),
        trustline_created=result['trustline_created'],
        network=result['network'],
        warning=warning
    )


@router.post("/add-trustline")
async def add_trustline(
    request: TrustlineRequest,
    service: StellarOnboardingService = Depends(get_onboarding_service)
):
    """
    Add UBECrc trustline to an existing Stellar account
    
    Use this if a steward already has a wallet but needs the UBECrc trustline.
    """
    logger.info(f"Adding trustline for {request.public_key[:8]}...")
    
    success = await service.add_trustline_to_existing_account(
        public_key=request.public_key,
        secret_key=request.secret_key
    )
    
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to add trustline. Verify account exists and credentials are correct."
        )
    
    return {
        "success": True,
        "public_key": request.public_key,
        "trustline_created": True,
        "message": "UBECrc trustline added successfully"
    }


@router.get("/funding-status", response_model=FundingStatusResponse)
async def get_funding_status(
    service: StellarOnboardingService = Depends(get_onboarding_service)
):
    """
    Check funding account balance and capacity
    
    Returns how many new accounts can be created with current funding balance.
    Useful for monitoring and alerting.
    """
    status = await service.check_funding_account_balance()
    
    return FundingStatusResponse(
        configured=status.get('configured', False),
        xlm_balance=status.get('xlm_balance'),
        accounts_possible=status.get('accounts_possible'),
        warning=status.get('warning'),
        error=status.get('error')
    )


@router.get("/check-account/{public_key}")
async def check_account_exists(
    public_key: str,
    service: StellarOnboardingService = Depends(get_onboarding_service)
):
    """
    Check if a Stellar public key has an active account
    
    Useful for validating user input before attempting operations.
    """
    if not public_key.startswith('G') or len(public_key) != 56:
        raise HTTPException(
            status_code=400,
            detail="Invalid Stellar public key format"
        )
    
    exists = await service.has_stellar_account(public_key)
    
    return {
        "public_key": public_key,
        "exists": exists
    }
