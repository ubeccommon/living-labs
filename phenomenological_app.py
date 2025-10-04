#!/usr/bin/env python3
"""
Phenomenological Observation System - FIXED v1.3.0
Enhanced with robust payload handling and Stellar payment integration

FIXES:
- Supports BOTH "readings" and "data" payload formats
- Better error messages for debugging
- Robust validation with clear failure points
- Handles flat sensor fields as fallback

Attribution: This project uses the services of Claude and Anthropic PBC.
"""

import asyncio
import uvicorn
from fastapi import FastAPI, Request as FastAPIRequest, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import os
import json

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("phenomenological_app")

# ============================================================
# SENSOR FIELD DEFINITIONS
# ============================================================

# Known sensor field names that can appear as flat top-level keys
SENSOR_FIELDS = {
    'air_temperature', 'temperature', 'temp',
    'humidity', 'hum',
    'pressure',
    'soil_moisture', 'soil_m',
    'soil_temperature', 'soil_temp', 'soil_t',
    'light_intensity', 'lux', 'illuminance',
    'uv_intensity', 'uv',
    'co2_ppm', 'co2',
    'voc_ppb', 'voc',
    'pm25', 'pm10', 'pm1', 'pm4',
    'dew_point', 'vpd'
}

# ============================================================
# APPLICATION LIFECYCLE
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the phenomenological system lifecycle"""
    logger.info("â•"â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—")
    logger.info("   Awakening Phenomenological Observer System v1.3.0")
    logger.info("â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•")
    
    try:
        # Initialize phenomenological database
        from phenomenological_db import PhenomenologicalDB
        
        # Get database URL from environment or use default
        db_url = os.getenv(
            'DATABASE_URL',
            'postgresql://postgres@localhost/ubec_sensors'
        )
        
        # Try alternative connection strings if first fails
        connection_strings = [
            db_url,
            'postgresql://postgres@localhost/ubec_sensors',
            'postgresql://kelpit@localhost/ubec_sensors',
        ]
        
        connected = False
        for conn_str in connection_strings:
            try:
                app.state.pheno_db = PhenomenologicalDB(conn_str)
                await app.state.pheno_db.connect()
                logger.info(f"âœ" Phenomenological database connected")
                connected = True
                break
            except Exception as e:
                logger.debug(f"Failed to connect with {conn_str}: {e}")
                continue
        
        if not connected:
            raise Exception("Could not connect to database")
        
        # Initialize pattern recognition engine
        app.state.pattern_engine = PatternRecognitionEngine(app.state.pheno_db)
        logger.info("âœ" Pattern recognition engine initialized")
        
        # Initialize gift economy
        app.state.gift_economy = GiftEconomy(app.state.pheno_db)
        logger.info("âœ" Gift economy activated")
        
        # Initialize learning journey tracker
        app.state.journey_tracker = LearningJourneyTracker(app.state.pheno_db)
        logger.info("âœ" Learning journey tracker ready")
        
        # Optional: Stellar blockchain for UBEC tokens
        try:
            from stellar_integration import StellarGiftNetwork
            app.state.stellar = StellarGiftNetwork()
            connected = await app.state.stellar.connect()
            if connected:
                logger.info("âœ" Stellar gift network connected")
                if app.state.stellar.can_send_payments:
                    logger.info("âœ" Stellar payments ENABLED")
                else:
                    logger.warning("âš  Stellar connected but payments DISABLED")
            else:
                logger.warning("âš¬ Stellar network connection failed")
                app.state.stellar = None
        except Exception as e:
            logger.info(f"âš¬ Stellar network optional - running without blockchain")
            app.state.stellar = None
        
        logger.info("â•"â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—")
        logger.info("   System Ready for Observations")
        logger.info("â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•")
        
    except Exception as e:
        logger.error(f"Failed to awaken system: {e}")
        raise
    
    yield  # Application runs here
    
    # Graceful shutdown
    logger.info("Entering rest state...")
    await app.state.pheno_db.close()
    if app.state.stellar:
        await app.state.stellar.close()
    logger.info("System at rest")

# ============================================================
# APPLICATION CREATION
# ============================================================

app = FastAPI(
    title="Phenomenological Observation System",
    description="""
    A living system for environmental observations where:
    - Sensors are conscious observers
    - Data points are phenomena
    - Measurements are observations
    - Patterns emerge naturally
    - Contributions are gifts
    - Gifts trigger UBEC token rewards
    """,
    version="1.3.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# ============================================================
# CORE SERVICES
# ============================================================

class PatternRecognitionEngine:
    """Discovers emerging patterns in observations"""
    
    def __init__(self, db):
        self.db = db
        self.patterns = {}
        
    async def analyze_observations(self, observer_id, phenomenon_id):
        """Look for patterns in recent observations"""
        await self.db.check_for_patterns(observer_id, phenomenon_id)
        
    async def get_emerging_patterns(self):
        """Return currently emerging patterns"""
        pass


class GiftEconomy:
    """Manages reciprocal gift exchanges"""
    
    def __init__(self, db):
        self.db = db
        
    async def offer_gift(self, giver_id, gift_type, value=0):
        """Record a gift offering"""
        return await self.db.create_gift(
            giver_id=giver_id,
            gift_type=gift_type,
            ubec_amount=value
        )
        
    async def track_reciprocity(self, observer_id):
        """Track reciprocal relationships"""
        pass


class LearningJourneyTracker:
    """Tracks observer learning and development"""
    
    def __init__(self, db):
        self.db = db
        
    async def record_insight(self, observer_id, insight):
        """Record a learning moment"""
        pass
        
    async def track_development(self, observer_id):
        """Monitor capacity development"""
        pass

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def safe_json_parse(value):
    """Safely parse a value that might be JSON string or already parsed dict"""
    if value is None:
        return None
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, ValueError):
            logger.debug(f"Failed to parse JSON string: {value[:100]}")
            return None
    return None

def safe_get(obj, *keys, default=None):
    """Safely get nested values from dict/record"""
    current = obj
    for key in keys:
        if current is None:
            return default
        
        if hasattr(current, 'get'):
            current = current.get(key)
        elif isinstance(current, dict):
            current = current.get(key)
        else:
            return default
    
    return current if current is not None else default

# ============================================================
# PAYMENT HELPER FUNCTIONS
# ============================================================

async def send_stellar_payment(app, gift_id, observer_id, observation_id, amount=7.14):
    """
    Send Stellar payment for a gift
    
    Returns:
        Dict with payment status and transaction hash if successful
    """
    result = {
        "payment_sent": False,
        "status": "not_attempted",
        "transaction_hash": None,
        "stellar_address": None,
        "error": None
    }
    
    # Check if Stellar is available
    if not app.state.stellar:
        result["status"] = "stellar_not_configured"
        logger.debug("Stellar not configured - gift created without payment")
        return result
    
    # Check if payments are enabled
    if not app.state.stellar.can_send_payments:
        result["status"] = "no_distributor_keys"
        logger.warning("Stellar connected but cannot send payments")
        return result
    
    try:
        # Get observer's Stellar address from database
        stellar_address = None
        
        async with app.state.pheno_db.pool.acquire() as conn:
            observer_query = """
                SELECT 
                    id,
                    external_identity,
                    essence
                FROM observers 
                WHERE id = $1
            """
            observer_row = await conn.fetchrow(observer_query, observer_id)
            
            if not observer_row:
                result["status"] = "observer_not_found"
                result["error"] = f"Observer {observer_id} not found"
                logger.warning(f"Observer {observer_id} not found")
                return result
            
            observer = dict(observer_row)
            
            # Extract Stellar address from JSONB fields
            ext_id = safe_json_parse(observer.get('external_identity'))
            essence = safe_json_parse(observer.get('essence'))
            
            if ext_id and isinstance(ext_id, dict):
                stellar_address = (
                    ext_id.get('stellar_address') or 
                    ext_id.get('wallet') or
                    ext_id.get('muxed_address')
                )
            
            if not stellar_address and essence and isinstance(essence, dict):
                stellar_address = (
                    essence.get('stellar_address') or 
                    essence.get('owner_stellar') or
                    essence.get('device_muxed_wallet') or
                    essence.get('muxed_address')
                )
        
        if not stellar_address:
            result["status"] = "no_stellar_address"
            result["error"] = f"No Stellar address found for observer {observer_id}"
            logger.warning(f"No Stellar address for observer {observer_id}")
            return result
        
        result["stellar_address"] = stellar_address
        logger.info(f"Sending {amount} UBEC to {stellar_address[:20]}...")
        
        # Send the payment
        tx_hash = await app.state.stellar.distributor.distribute_ubecrc(
            recipient=stellar_address,
            amount=Decimal(str(amount)),
            device_id=str(gift_id)[:8],
            memo=f"Obs_{str(observation_id)[:8]}" if observation_id else f"Gift_{str(gift_id)[:8]}"
        )
        
        if tx_hash:
            # Update gift with transaction hash
            async with app.state.pheno_db.pool.acquire() as conn:
                await conn.execute(
                    "UPDATE gifts SET stellar_transaction_hash = $1, received_at = NOW() WHERE id = $2",
                    tx_hash, gift_id
                )
            
            result["payment_sent"] = True
            result["status"] = "success"
            result["transaction_hash"] = tx_hash
            logger.info(f"âœ" Payment sent: {amount} UBEC, TX: {tx_hash}")
        else:
            result["status"] = "payment_failed"
            result["error"] = "Transaction submission failed"
            logger.warning(f"Payment failed for gift {gift_id}")
            
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        logger.error(f"Error processing payment: {e}", exc_info=True)
    
    return result

# ============================================================
# API ROUTES
# ============================================================

from phenomenological_api import pheno_router

# Mount phenomenological routes
app.include_router(pheno_router)

@app.get("/")
async def root():
    """System consciousness check"""
    return {
        "state": "aware",
        "mode": "phenomenological",
        "version": "1.3.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "philosophy": "Technology and nature as complementary expressions",
        "stellar_payments": "enabled" if (app.state.stellar and app.state.stellar.can_send_payments) else "disabled"
    }

@app.get("/health")
async def health_check():
    """System health check"""
    try:
        async with app.state.pheno_db.pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        
        return {
            "status": "healthy",
            "version": "1.3.0",
            "database": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

@app.get("/status")
async def system_status():
    """Detailed system status"""
    stellar_status = "not_configured"
    can_send_payments = False
    
    if app.state.stellar:
        stellar_status = "connected"
        can_send_payments = app.state.stellar.can_send_payments
    
    return {
        "system": "phenomenological_observer",
        "version": "1.3.0",
        "database": "connected",
        "stellar": {
            "status": stellar_status,
            "can_send_payments": can_send_payments
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.post("/observe")
async def create_observation_endpoint(request: FastAPIRequest):
    """
    UNIVERSAL OBSERVATION ENDPOINT - v1.3.0 FIXED
    
    Accepts multiple payload formats:
    1. Nested readings: {"device_id": "...", "readings": {...}}
    2. Nested data: {"device_id": "...", "data": {...}}
    3. Flat sensor fields: {"device_id": "...", "temperature": 22.5, ...}
    
    Required fields:
    - device_id: String identifier for the device
    - At least one sensor reading
    
    Optional fields:
    - observer_id: UUID (auto-created if not provided)
    - location: {"lat": float, "lon": float}
    - mood, intensity, quality: Phenomenological metadata
    - timestamp: Unix timestamp or ISO format
    
    Returns observation details and UBEC reward information
    
    Attribution: This fix uses Claude and Anthropic PBC assistance.
    """
    try:
        # ===== STEP 1: PARSE JSON BODY =====
        try:
            request_data = await request.json()
        except Exception as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid JSON payload: {str(e)}"
            )
        
        logger.info(f"Received observation request: {list(request_data.keys())}")
        
        # ===== STEP 2: VALIDATE device_id (REQUIRED) =====
        device_id = request_data.get('device_id')
        if not device_id:
            logger.error("Missing device_id in request")
            raise HTTPException(
                status_code=400,
                detail="Missing required field 'device_id'. Please include device_id in your payload."
            )
        
        logger.info(f"Processing observation from device: {device_id}")
        
        # ===== STEP 3: EXTRACT READINGS (REQUIRED) =====
        # Try multiple extraction strategies
        readings = None
        extraction_method = None
        
        # Strategy 1: Check for 'readings' key
        if 'readings' in request_data and isinstance(request_data['readings'], dict):
            readings = request_data['readings']
            extraction_method = "readings_key"
            logger.info(f"Extracted readings from 'readings' key: {list(readings.keys())}")
        
        # Strategy 2: Check for 'data' key
        if not readings and 'data' in request_data:
            data = request_data['data']
            if isinstance(data, dict):
                readings = {
                    key: value 
                    for key, value in data.items()
                    if isinstance(value, (int, float)) or value is None
                }
                extraction_method = "data_key"
                logger.info(f"Extracted readings from 'data' key: {list(readings.keys())}")
        
        # Strategy 3: Extract flat sensor fields
        if not readings:
            readings = {}
            for key, value in request_data.items():
                if key in SENSOR_FIELDS:
                    if isinstance(value, (int, float)):
                        readings[key] = value
                    elif value is None:
                        readings[key] = None
            
            if readings:
                extraction_method = "flat_fields"
                logger.info(f"Extracted readings from flat fields: {list(readings.keys())}")
        
        # Validate we got some readings
        if not readings:
            logger.error("No readings found in request")
            logger.error(f"Request keys: {list(request_data.keys())}")
            raise HTTPException(
                status_code=400,
                detail="No sensor readings found. Include either 'readings' object, 'data' object, or flat sensor fields (temperature, humidity, etc.)"
            )
        
        logger.info(f"âœ" Extracted {len(readings)} sensor readings via {extraction_method}")
        
        # ===== STEP 4: EXTRACT OPTIONAL FIELDS =====
        location = request_data.get('location', {})
        
        metadata = {}
        for field in ['timestamp', 'timezone', 'tz_offset_seconds', 'ip', 'mood', 'intensity', 'quality']:
            if field in request_data:
                metadata[field] = request_data[field]
        
        # ===== STEP 5: FIND OR CREATE OBSERVER =====
        observer_id = request_data.get('observer_id')
        
        if not observer_id:
            # Auto-create observer for this device
            observer_id = await app.state.pheno_db.create_observer(
                observer_type='device',
                external_identity={
                    'device_id': device_id,
                    'first_seen': datetime.now(timezone.utc).isoformat()
                },
                essence={
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'auto_created': True,
                    'extraction_method': extraction_method
                }
            )
            logger.info(f"âœ" Auto-created observer {observer_id} for device {device_id}")
        
        # ===== STEP 6: CREATE PHENOMENON =====
        phenomenon_gesture = {
            "type": "environmental_reading",
            "sensor_types": list(readings.keys()),
            "device_id": device_id,
            "readings": readings,
            "location": location,
            "extraction_method": extraction_method
        }
        
        phenomenon_id = await app.state.pheno_db.create_phenomenon(
            moment=datetime.now(timezone.utc),
            gesture=phenomenon_gesture,
            mood=request_data.get('mood', 'observing'),
            intensity=request_data.get('intensity', 0.8)
        )
        
        # ===== STEP 7: CREATE OBSERVATION =====
        perception_data = {
            "readings": readings,
            "location": location,
            "metadata": metadata,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "extraction_method": extraction_method
        }
        
        # Calculate quality metrics
        attention_quality = float(request_data.get('quality', 0.85))
        clarity = min(1.0, len(readings) / 5.0)
        
        observation_id = await app.state.pheno_db.create_observation(
            observer_id=observer_id,
            phenomenon_id=phenomenon_id,
            perception=perception_data,
            attention_quality=attention_quality,
            clarity=clarity
        )
        
        logger.info(f"âœ" Created observation {observation_id}")
        
        # ===== STEP 8: CHECK FOR PATTERNS =====
        try:
            await app.state.pattern_engine.analyze_observations(observer_id, phenomenon_id)
        except Exception as e:
            logger.warning(f"Pattern analysis failed: {e}")
        
        # ===== STEP 9: CREATE GIFT & CALCULATE REWARD =====
        base_reward = 7.14
        sensor_bonus = len(readings) * 0.5
        quality_bonus = attention_quality * 0.5
        total_reward = base_reward + sensor_bonus + quality_bonus
        
        gift_id = await app.state.gift_economy.offer_gift(
            observer_id, 
            'observation',
            total_reward
        )
        
        logger.info(f"âœ" Created gift {gift_id} worth {total_reward} UBEC")
        
        # ===== STEP 10: SEND STELLAR PAYMENT =====
        payment_result = await send_stellar_payment(
            app=app,
            gift_id=gift_id,
            observer_id=observer_id,
            observation_id=observation_id,
            amount=total_reward
        )
        
        # ===== STEP 11: RETURN SUCCESS =====
        response = {
            "success": True,
            "observation_id": str(observation_id),
            "phenomenon_id": str(phenomenon_id),
            "observer_id": str(observer_id),
            "device_id": device_id,
            "readings_count": len(readings),
            "extraction_method": extraction_method,
            "gift_id": str(gift_id),
            "ubec_reward": float(total_reward),
            "payment": {
                "sent": payment_result["payment_sent"],
                "status": payment_result["status"],
                "transaction_hash": payment_result["transaction_hash"],
                "stellar_address": payment_result["stellar_address"]
            },
            "message": f"âœ" Observation received - {len(readings)} sensor readings recorded",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"âœ" Observation pipeline complete for device {device_id}")
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions with proper status codes
        raise
        
    except Exception as e:
        logger.error(f"âœ— Error in observation endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal error processing observation: {str(e)}"
        )

@app.get("/gifts/pending")
async def get_pending_gifts():
    """Get gifts that haven't been paid yet"""
    try:
        async with app.state.pheno_db.pool.acquire() as conn:
            pending = await conn.fetch("""
                SELECT 
                    g.id,
                    g.giver_id,
                    g.gift_type,
                    g.ubec_expression as amount,
                    g.offered_at,
                    o.external_identity,
                    o.essence
                FROM gifts g
                JOIN observers o ON g.giver_id = o.id
                WHERE g.stellar_transaction_hash IS NULL
                AND g.ubec_expression > 0
                ORDER BY g.offered_at DESC
                LIMIT 100
            """)
            
            pending_list = []
            for row in pending:
                gift_dict = dict(row)
                
                # Extract stellar address
                ext_id = safe_json_parse(gift_dict.get('external_identity'))
                essence = safe_json_parse(gift_dict.get('essence'))
                
                stellar_address = None
                if ext_id:
                    stellar_address = ext_id.get('stellar_address') or ext_id.get('wallet')
                if not stellar_address and essence:
                    stellar_address = (
                        essence.get('device_muxed_wallet') or 
                        essence.get('owner_stellar') or
                        essence.get('stellar_address')
                    )
                
                gift_dict['stellar_address'] = stellar_address
                pending_list.append(gift_dict)
            
            return {
                "pending_gifts": pending_list,
                "count": len(pending_list)
            }
    except Exception as e:
        logger.error(f"Error getting pending gifts: {e}", exc_info=True)
        return {"error": str(e)}

# ============================================================
# STARTUP SCRIPT
# ============================================================

def main():
    """Main entry point"""
    
    print("""
    â•"â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
    â•'                                                          â•'
    â•'       PHENOMENOLOGICAL OBSERVATION SYSTEM v1.3.0        â•'
    â•'                 with UBEC Gift Economy                   â•'
    â•'                         FIXED                            â•'
    â•'                                                          â•'
    â•'     "From Seeds to Blockchain: Growing the Future"      â•'
    â•'                                                          â•'
    â•'      Freie Waldorfschule Frankfurt (Oder)               â•'
    â•'           Living Science Initiative                      â•'
    â•'                                                          â•'
    â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    
    Starting phenomenological observer with Stellar payments...
    """)
    
    config = {
        "app": "phenomenological_app:app",
        "host": "0.0.0.0",
        "port": 8000,
        "reload": True,
        "log_level": "info",
        "access_log": True
    }
    
    uvicorn.run(**config)


if __name__ == "__main__":
    main()
