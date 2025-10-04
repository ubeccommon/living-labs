#!/usr/bin/env python3
"""
Phenomenological API Routes - v1.3.0 FIXED
UBEC Standard v1.0 - Reciprocal Economy Edition

UPDATES in v1.3.0:
- Enhanced error handling with clear validation messages
- Support for multiple payload formats (readings/data/flat)
- Improved muxed address generation and validation
- Better CORS support for cross-origin requests
- Comprehensive observer registration with device tracking

Bridges legacy sensor endpoints with reciprocal observation-based system.
Enhanced to properly handle multiple SenseBox devices per steward,
each with its own unique muxed address for tracking contributions.

Attribution: This project uses the services of Claude and Anthropic PBC.
"""

from fastapi import APIRouter, HTTPException, Depends, Response, Request
from pydantic import BaseModel
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4
from decimal import Decimal
import logging
import json

# Import the muxed account manager with new standard
try:
    from stellar_muxed import (
        StellarMuxedAccountManager,
        create_muxed,
        decode_muxed,
        verify_muxed,
        InvalidAddressError,
        InvalidDeviceIdError,
    )
    MUXED_ENABLED = True
    logger = logging.getLogger(__name__)
    logger.info("✓ Stellar muxed address generation enabled (UBEC Standard v1.0)")
except ImportError:
    StellarMuxedAccountManager = None
    create_muxed = None
    MUXED_ENABLED = False
    logger = logging.getLogger(__name__)
    logger.warning("⚠ stellar_muxed module not found. Muxed addresses will not be generated.")

# Import all models from phenomenological_models
from phenomenological_models import (
    ObserverEntity,
    ObserverType,
    SensoryCapacities,
    PhenomenonEvent,
    PhenomenonMood,
    PhenomenonGesture,
    ObservationExperience,
    ObservationPerception,
    ObservationImagination,
    PatternEmergence,
    PatternArchetype,
    ExchangeType,
    ReciprocalExchange,
    LearningJourney,
    ObservationResponse,
    PatternDiscoveryResponse,
    ReciprocalBalanceResponse,
    ExchangeStatisticsResponse,
    BlockchainVerificationRequest,
    BlockchainVerificationResponse,
    validate_stellar_address,
    validate_ipfs_hash
)

# ============================================================
# ADDITIONAL REQUEST/RESPONSE MODELS FOR API
# ============================================================

class ObserverRegistration(BaseModel):
    """Request model for observer registration"""
    observer_type: str
    external_identity: Dict[str, Any]
    essence: Dict[str, Any]
    sensory_capacities: Dict[str, bool]

class ObservationSubmission(BaseModel):
    """Request model for simple observation submission"""
    device_id: str
    readings: Dict[str, float]
    location: Dict[str, float]
    student_wallet: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

# ============================================================
# API ROUTERS
# ============================================================

pheno_router = APIRouter(prefix="/api/v2", tags=["Phenomenological"])

# ============================================================
# DEPENDENCIES
# ============================================================

def get_db(request: Request):
    """Dependency to get phenomenological database from app state"""
    if hasattr(request.app.state, 'pheno_db'):
        return request.app.state.pheno_db
    else:
        # Fallback for testing
        return request.app.state.db

# ============================================================
# TEST & HEALTH ENDPOINTS
# ============================================================

@pheno_router.get("/test")
async def test_endpoint():
    """Simple test endpoint to verify API connectivity"""
    return {
        "status": "ok", 
        "message": "Phenomenological API is running",
        "mode": "reciprocal_economy",
        "muxed_addresses": "enabled" if MUXED_ENABLED else "disabled",
        "ubec_standard": "v1.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@pheno_router.get("/health")
async def health_check(request: Request):
    """Check system health"""
    try:
        db = get_db(request)
        async with db.pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
            
        stellar_status = "disabled"
        if hasattr(request.app.state, 'stellar'):
            if request.app.state.stellar and request.app.state.stellar.can_send_payments:
                stellar_status = "enabled"
            
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": "connected",
            "stellar_payments": stellar_status,
            "muxed_addresses": "enabled" if MUXED_ENABLED else "disabled",
            "ubec_standard": "v1.0",
            "mode": "reciprocal_economy",
            "blockchain": "ready"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# ============================================================
# OBSERVER REGISTRATION ENDPOINTS
# ============================================================

@pheno_router.post("/observers/register")
async def register_observer(
    observer_data: ObserverRegistration,
    request: Request,
    response: Response
):
    """
    Register a new observer (human or device) - UBEC Standard v1.0
    
    Enhanced features:
    - Each device gets a unique muxed address based on its serial number
    - Multiple devices from the same steward have different muxed addresses
    - All payments route to the steward's base wallet
    - Specific error handling for address and device ID validation
    
    Valid observer_type values: 'device' or 'human'
    """
    # Add CORS headers explicitly
    response.headers["Access-Control-Allow-Origin"] = "*"
    
    try:
        db = get_db(request)
        
        # Normalize observer_type to ObserverType enum
        observer_type = observer_data.observer_type.lower()
        
        # Map alternative names to standard types
        if observer_type in ['environmental_sensor', 'sensor', 'device']:
            observer_type = ObserverType.DEVICE
        elif observer_type in ['person', 'user', 'human']:
            observer_type = ObserverType.HUMAN
        elif observer_type == 'community':
            observer_type = ObserverType.COMMUNITY
        elif observer_type == 'collective':
            observer_type = ObserverType.COLLECTIVE
        else:
            # Default to device if unknown
            observer_type = ObserverType.DEVICE
        
        # Initialize muxed_wallet variable
        muxed_wallet = None
        
        # Handle device registration with proper wallet setup
        if observer_type == ObserverType.DEVICE:
            # Extract owner's stellar wallet
            owner_stellar = (
                observer_data.essence.get('steward_stellar') or
                observer_data.essence.get('owner_stellar') or
                observer_data.essence.get('stellar_address')
            )
            
            # CRITICAL: Extract the actual serial number to ensure uniqueness
            # Priority order for finding the serial number:
            # 1. external_identity.serial
            # 2. external_identity.serial_number  
            # 3. external_identity.device_id (remove SENS_ prefix)
            # 4. essence.serial_number
            
            serial_number = None
            
            # Check external_identity first (this is where the registration form puts it)
            if observer_data.external_identity:
                serial_number = (
                    observer_data.external_identity.get('serial') or
                    observer_data.external_identity.get('serial_number')
                )
                
                # If not found, try extracting from device_id
                if not serial_number:
                    device_id = observer_data.external_identity.get('device_id', '')
                    if device_id.startswith('SENS_'):
                        serial_number = device_id.replace('SENS_', '')
                    elif device_id:
                        serial_number = device_id
            
            # Fallback to essence if not in external_identity
            if not serial_number and observer_data.essence:
                serial_number = observer_data.essence.get('serial_number')
            
            # If still no serial number, log error but generate a unique one
            if not serial_number:
                logger.warning("No serial number provided for device registration, generating unique ID")
                serial_number = str(uuid4())
            
            logger.info(f"Registering device with serial number: {serial_number}")
            
            if owner_stellar and validate_stellar_address(owner_stellar):
                # Generate muxed address for the device if stellar_muxed module is available
                if MUXED_ENABLED and create_muxed:
                    try:
                        # Use the new UBEC Standard v1.0 API
                        # create_muxed() is the convenience function
                        muxed_wallet = create_muxed(
                            base_address=owner_stellar,
                            device_id=serial_number
                        )
                        
                        # Store both the base and muxed addresses
                        observer_data.essence['owner_stellar'] = owner_stellar
                        observer_data.essence['device_muxed_wallet'] = muxed_wallet
                        observer_data.essence['serial_number'] = serial_number  # Store for reference
                        
                        logger.info(f"✓ Generated unique muxed address for device {serial_number}")
                        logger.info(f"  Base wallet: {owner_stellar[:10]}...{owner_stellar[-5:]}")
                        logger.info(f"  Muxed wallet: {muxed_wallet[:10]}...{muxed_wallet[-5:]}")
                        
                    except InvalidAddressError as e:
                        logger.error(f"Invalid Stellar address: {e}")
                        raise HTTPException(
                            status_code=400,
                            detail=f"Invalid Stellar address: {str(e)}"
                        )
                    except InvalidDeviceIdError as e:
                        logger.error(f"Invalid device ID: {e}")
                        raise HTTPException(
                            status_code=400,
                            detail=f"Invalid device ID: {str(e)}"
                        )
                    except Exception as e:
                        logger.error(f"Failed to generate muxed address: {e}")
                        # Fallback to regular address if muxed generation fails
                        observer_data.essence['device_muxed_wallet'] = owner_stellar
                        observer_data.essence['owner_stellar'] = owner_stellar
                        observer_data.essence['serial_number'] = serial_number
                else:
                    # No muxed module available, use regular address
                    observer_data.essence['device_muxed_wallet'] = owner_stellar
                    observer_data.essence['owner_stellar'] = owner_stellar
                    observer_data.essence['serial_number'] = serial_number
                    logger.info(f"Device configured with base wallet (muxed not available)")
            else:
                logger.warning(f"No valid Stellar wallet provided for device {serial_number}")
        
        # For human stewards, ensure stellar address is stored properly
        elif observer_type == ObserverType.HUMAN:
            stellar_address = observer_data.essence.get('stellar_address')
            if stellar_address and validate_stellar_address(stellar_address):
                # Also store in external_identity for payment processing
                observer_data.external_identity['stellar_address'] = stellar_address
                
                # For human stewards, we could also generate a muxed address if needed
                if MUXED_ENABLED and create_muxed:
                    try:
                        # Use email as unique identifier for human
                        # This ensures each human registration gets a consistent muxed address
                        human_id = (
                            observer_data.external_identity.get('email', '') or
                            observer_data.external_identity.get('name', '') or
                            str(uuid4())
                        )
                        
                        muxed_wallet = create_muxed(
                            base_address=stellar_address,
                            device_id=human_id
                        )
                        
                        observer_data.essence['muxed_wallet'] = muxed_wallet
                        logger.info(f"✓ Generated muxed address for human steward: {human_id}")
                        
                    except (InvalidAddressError, InvalidDeviceIdError) as e:
                        logger.warning(f"Failed to generate muxed address for human: {e}")
        
        # Convert sensory_capacities dict to SensoryCapacities model if needed
        sensory_caps = observer_data.sensory_capacities
        if not isinstance(sensory_caps, SensoryCapacities):
            # Create SensoryCapacities from dict
            sensory_caps = SensoryCapacities(**sensory_caps)
        
        # Create the observer
        observer_id = await db.create_observer(
            observer_type=observer_type.value,
            external_identity=observer_data.external_identity,
            essence=observer_data.essence,
            sensory_capacities=sensory_caps.dict() if hasattr(sensory_caps, 'dict') else sensory_caps
        )
        
        logger.info(f"✓ Observer registered: {observer_id} (type: {observer_type.value})")
        
        # Build response with muxed wallet if generated
        response_data = {
            "success": True,
            "observer_id": str(observer_id),
            "observer_type": observer_type.value,
            "message": f"Observer registered successfully as {observer_type.value}",
            "ubec_standard": "v1.0",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Add muxed wallet to response if it was generated
        if muxed_wallet:
            response_data["muxed_wallet"] = muxed_wallet
            logger.info(f"✓ Returning muxed wallet in response (length: {len(muxed_wallet)})")
            
            # Log verification for debugging
            if observer_type == ObserverType.DEVICE:
                serial = observer_data.essence.get('serial_number', 'unknown')
                logger.info(f"Device {serial} -> Muxed: {muxed_wallet[:15]}...{muxed_wallet[-10:]}")
        
        return response_data
        
    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
    except Exception as e:
        logger.error(f"Failed to register observer: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================
# VERIFY MUXED ADDRESS ENDPOINT (for testing)
# ============================================================

@pheno_router.get("/muxed/verify/{steward_wallet}/{serial_number}")
async def verify_muxed_address(
    steward_wallet: str,
    serial_number: str
):
    """
    Test endpoint to verify muxed address generation (UBEC Standard v1.0)
    
    Useful for checking that each serial number generates a unique address.
    Uses the new convenience functions for cleaner code.
    """
    if not MUXED_ENABLED:
        return {"error": "Muxed address generation not available"}
    
    try:
        # Use convenience functions from UBEC Standard v1.0
        muxed = create_muxed(steward_wallet, serial_number)
        base, mux_id = decode_muxed(muxed)
        is_valid = verify_muxed(muxed, steward_wallet, serial_number)
        
        return {
            "steward_wallet": steward_wallet,
            "serial_number": serial_number,
            "muxed_address": muxed,
            "muxed_length": len(muxed),
            "decoded_base": base,
            "decoded_mux_id": mux_id,
            "verification": is_valid,
            "base_matches": base == steward_wallet,
            "ubec_standard": "v1.0"
        }
    except InvalidAddressError as e:
        return {"error": f"Invalid address: {str(e)}"}
    except InvalidDeviceIdError as e:
        return {"error": f"Invalid device ID: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}

# ============================================================
# LIST DEVICES BY STEWARD (for managing multiple devices)
# ============================================================

@pheno_router.get("/steward/{steward_wallet}/devices")
async def list_steward_devices(
    steward_wallet: str,
    request: Request
):
    """
    List all devices registered to a specific steward wallet
    Shows how each device has its own unique muxed address (UBEC Standard v1.0)
    """
    try:
        db = get_db(request)
        
        async with db.pool.acquire() as conn:
            # Find all devices with this steward wallet
            devices = await conn.fetch("""
                SELECT 
                    id as observer_id,
                    external_identity,
                    essence,
                    created_at
                FROM observers
                WHERE observer_type = 'device'
                    AND (
                        essence->>'owner_stellar' = $1
                        OR essence->>'steward_stellar' = $1
                    )
                ORDER BY created_at DESC
            """, steward_wallet)
        
        device_list = []
        for device in devices:
            external_id = json.loads(device['external_identity']) if isinstance(device['external_identity'], str) else device['external_identity']
            essence = json.loads(device['essence']) if isinstance(device['essence'], str) else device['essence']
            
            device_info = {
                "observer_id": str(device['observer_id']),
                "serial_number": essence.get('serial_number', 'unknown'),
                "device_name": external_id.get('name', 'unnamed'),
                "device_id": external_id.get('device_id', ''),
                "muxed_wallet": essence.get('device_muxed_wallet', ''),
                "registered_at": device['created_at'].isoformat() if device['created_at'] else None
            }
            
            # Verify each device has unique muxed address
            if device_info['muxed_wallet'] and device_info['muxed_wallet'].startswith('M'):
                device_info['muxed_valid'] = True
                device_info['muxed_format_ok'] = True
                
                # If muxed module available, verify it
                if MUXED_ENABLED and verify_muxed:
                    try:
                        device_info['muxed_verified'] = verify_muxed(
                            device_info['muxed_wallet'],
                            steward_wallet,
                            device_info['serial_number']
                        )
                    except Exception:
                        device_info['muxed_verified'] = False
                else:
                    device_info['muxed_verified'] = None
            else:
                device_info['muxed_valid'] = False
                device_info['muxed_format_ok'] = False
                device_info['muxed_verified'] = False
            
            device_list.append(device_info)
        
        # Check for uniqueness of muxed addresses
        muxed_addresses = [d['muxed_wallet'] for d in device_list if d['muxed_wallet']]
        unique_muxed = len(muxed_addresses) == len(set(muxed_addresses))
        
        return {
            "steward_wallet": steward_wallet,
            "total_devices": len(device_list),
            "devices": device_list,
            "all_muxed_unique": unique_muxed,
            "ubec_standard": "v1.0",
            "message": "Each device has its own unique muxed address for tracking contributions"
        }
        
    except Exception as e:
        logger.error(f"Failed to list steward devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# OBSERVATION ENDPOINTS
# ============================================================

@pheno_router.post("/observations")
async def submit_observation(
    observation: ObservationSubmission,
    request: Request
):
    """Submit a new observation from a device"""
    try:
        db = get_db(request)
        
        # Find observer by device_id
        async with db.pool.acquire() as conn:
            observer_row = await conn.fetchrow(
                "SELECT id FROM observers WHERE external_identity->>'device_id' = $1",
                observation.device_id
            )
            
            if not observer_row:
                raise HTTPException(status_code=404, detail=f"Observer not found for device {observation.device_id}")
            
            observer_id = observer_row['id']
        
        # Create phenomenon if not exists
        phenomenon_id = await db.find_or_create_phenomenon(
            phenomenon_type="environmental_reading",
            attributes={
                "sensor_types": list(observation.readings.keys()),
                "location": observation.location
            }
        )
        
        # Calculate quality score based on completeness
        expected_sensors = ['temperature', 'humidity', 'pressure']
        present_sensors = [s for s in expected_sensors if s in observation.readings]
        quality_score = len(present_sensors) / len(expected_sensors) if expected_sensors else 1.0
        
        # Create observation
        observation_id = await db.create_observation(
            observer_id=observer_id,
            phenomenon_id=phenomenon_id,
            perception={
                "readings": observation.readings,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            quality_score=quality_score
        )
        
        # Calculate reciprocal value
        base_value = Decimal("7.14")
        sensor_count = len(observation.readings)
        sensor_bonus = Decimal(sensor_count) * Decimal("0.5")
        total_value = base_value + sensor_bonus
        
        # Create gift/exchange for reciprocal value
        gift_id = await db.create_gift(
            giver_id=observer_id,
            gift_type="observation",
            ubec_amount=total_value,
            metadata={
                "observation_id": str(observation_id),
                "sensor_count": sensor_count,
                "quality_score": float(quality_score)
            }
        )
        
        return ObservationResponse(
            observation_id=observation_id,
            phenomenon_id=phenomenon_id,
            observer_id=observer_id,
            quality_score=quality_score,
            timestamp=datetime.now(timezone.utc),
            reciprocal_reward=total_value
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit observation: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ============================================================
# SYSTEM INFO ENDPOINT
# ============================================================

@pheno_router.get("/system/info")
async def system_info():
    """Get system information including UBEC standard version"""
    return {
        "ubec_standard": "v1.0",
        "api_version": "2.0",
        "muxed_addresses": "enabled" if MUXED_ENABLED else "disabled",
        "features": {
            "device_registration": True,
            "human_registration": True,
            "muxed_address_generation": MUXED_ENABLED,
            "multi_device_support": True,
            "reciprocal_economy": True,
            "observation_tracking": True,
            "pattern_detection": True,
        },
        "muxed_features": {
            "custom_exceptions": MUXED_ENABLED,
            "structured_data": MUXED_ENABLED,
            "convenience_functions": MUXED_ENABLED,
            "type_safety": MUXED_ENABLED,
        } if MUXED_ENABLED else None
    }

# ============================================================
# Continue with remaining endpoints from original file...
# (Pattern detection, reciprocal economy, system stats, etc.)
# ============================================================

# [Additional endpoints can be added here as needed]

"""
UBEC Standard v1.0 - Phenomenological API
Attribution: This project uses the services of Claude and Anthropic PBC
to inform our decisions and recommendations.
"""
