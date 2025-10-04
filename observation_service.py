#!/usr/bin/env python3
"""
Observation Service - Environmental Data Recording
Handles IPFS storage, Stellar muxed payments, and database recording

Design Principles Applied:
- Principle #2: Service pattern - no standalone execution
- Principle #5: Strict async operations
- Principle #10: Clear separation of concerns
- Automatic muxed address lookup for Stellar payments

Attribution: This project uses the services of Claude and Anthropic PBC.
"""

import logging
import uuid
import json
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from decimal import Decimal
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class ObservationResult:
    """Result of complete observation processing"""
    observation_id: str
    ipfs_cid: Optional[str]
    stellar_tx_hash: Optional[str]
    tokens_distributed: Decimal
    blockchain_verified: bool
    timestamp: str
    muxed_address: Optional[str] = None  # The muxed address used for payment
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "observation_id": self.observation_id,
            "ipfs_cid": self.ipfs_cid,
            "stellar_tx_hash": self.stellar_tx_hash,
            "tokens_distributed": str(self.tokens_distributed),
            "blockchain_verified": self.blockchain_verified,
            "timestamp": self.timestamp,
            "muxed_address": self.muxed_address
        }


class ObservationService:
    """
    Service for processing environmental observations
    Coordinates IPFS storage, Stellar payments, and database recording
    
    Payment Flow:
    1. Device sends observation with device_id
    2. System looks up device's muxed address from database
    3. Payment sent to muxed address (automatically routes to base address)
    4. Stellar network tracks which device via mux ID
    """
    
    # Token values for reciprocal economy
    BASE_OBSERVATION_VALUE = Decimal("7.44")  # Base value per observation
    SENSOR_BONUS = Decimal("0.50")  # Additional for sensor data
    
    def __init__(
        self,
        ipfs_service: Optional[Any] = None,
        stellar_service: Optional[Any] = None,
        database: Optional[Any] = None,
        phenomenological_db: Optional[Any] = None
    ):
        """
        Initialize observation service
        
        Args:
            ipfs_service: IPFS/Pinata service instance
            stellar_service: Stellar network service instance
            database: Database connection
            phenomenological_db: Phenomenological database (can be same as database)
        """
        self.ipfs = ipfs_service
        self.stellar = stellar_service
        self.db = database or phenomenological_db
        self.pheno_db = phenomenological_db or database
        
        # Service availability flags
        self.ipfs_available = ipfs_service is not None
        self.stellar_available = stellar_service is not None and getattr(stellar_service, 'can_send_payments', False)
        self.db_available = database is not None or phenomenological_db is not None
        
        # Cache for observer and phenomenon IDs
        self._observer_cache = {}
        self._default_phenomenon_id = None
        
        mode = "Reciprocal Economy Mode" if self.stellar_available else "Observation Mode"
        logger.info(f"Observation Service initialized ({mode})")
        logger.info(f"  IPFS: {'✓' if self.ipfs_available else '✗'}")
        logger.info(f"  Stellar: {'✓' if self.stellar_available else '✗'}")
        logger.info(f"  Database: {'✓' if self.db_available else '✗'}")
    
    async def _get_device_muxed_address(self, device_id: str) -> Optional[str]:
        """
        Look up the muxed Stellar address for a device
        
        Args:
            device_id: Device identifier
            
        Returns:
            Muxed address (M...) if found, None otherwise
        """
        if not self.db_available:
            return None
        
        try:
            async with self.db.pool.acquire() as conn:
                # Look up device's muxed address from observers table
                result = await conn.fetchrow("""
                    SELECT 
                        essence->>'device_muxed_wallet' as muxed_wallet,
                        essence->>'owner_stellar' as owner_stellar
                    FROM phenomenological.observers
                    WHERE external_identity->>'device_id' = $1
                    LIMIT 1
                """, device_id)
                
                if result:
                    muxed_wallet = result['muxed_wallet']
                    owner_stellar = result['owner_stellar']
                    
                    if muxed_wallet:
                        logger.info(f"Found muxed address for device {device_id}: {muxed_wallet[:15]}...")
                        return muxed_wallet
                    elif owner_stellar:
                        logger.info(f"Found base address for device {device_id}: {owner_stellar[:10]}...")
                        return owner_stellar
                    else:
                        logger.warning(f"Device {device_id} has no payment address configured")
                else:
                    logger.warning(f"Device {device_id} not found in database")
                    
        except Exception as e:
            logger.error(f"Error looking up device address: {e}")
        
        return None
    
    async def _get_or_create_observer(self, device_id: str) -> Optional[str]:
        """Get or create an observer record for the device"""
        if not self.db_available:
            return None
        
        # Check cache first
        if device_id in self._observer_cache:
            return self._observer_cache[device_id]
        
        schema = "phenomenological"
        
        try:
            if hasattr(self.db, 'pool'):
                async with self.db.pool.acquire() as conn:
                    # First try to find existing observer by device_id in external_identity
                    existing = await conn.fetchrow(f"""
                        SELECT id FROM {schema}.observers 
                        WHERE external_identity->>'device_id' = $1
                        LIMIT 1
                    """, device_id)
                    
                    if existing:
                        observer_id = str(existing['id'])
                        self._observer_cache[device_id] = observer_id
                        return observer_id
                    
                    # Create new observer
                    new_observer = await conn.fetchrow(f"""
                        INSERT INTO {schema}.observers (
                            observer_type,
                            external_identity,
                            essence,
                            sensory_capacities
                        ) VALUES (
                            'device',
                            $1::jsonb,
                            $2::jsonb,
                            $3::jsonb
                        )
                        RETURNING id
                    """, 
                    json.dumps({"device_id": device_id, "type": "sensor"}),
                    json.dumps({"capabilities": ["environmental_monitoring"]}),
                    json.dumps({"sensors": ["temperature", "humidity"]})
                    )
                    
                    observer_id = str(new_observer['id'])
                    self._observer_cache[device_id] = observer_id
                    logger.info(f"Created new observer for device {device_id}")
                    return observer_id
                    
        except Exception as e:
            logger.error(f"Failed to get/create observer: {e}")
            return None
    
    async def _get_or_create_phenomenon(self) -> Optional[str]:
        """Get or create a default environmental phenomenon"""
        if self._default_phenomenon_id:
            return self._default_phenomenon_id
        
        if not self.db_available:
            return None
        
        schema = "phenomenological"
        
        try:
            if hasattr(self.db, 'pool'):
                async with self.db.pool.acquire() as conn:
                    # Try to find existing environmental phenomenon
                    existing = await conn.fetchrow(f"""
                        SELECT id FROM {schema}.phenomena 
                        WHERE gesture->>'type' = 'environmental_observation'
                        LIMIT 1
                    """)
                    
                    if existing:
                        self._default_phenomenon_id = str(existing['id'])
                        return self._default_phenomenon_id
                    
                    # Create new phenomenon
                    new_phenom = await conn.fetchrow(f"""
                        INSERT INTO {schema}.phenomena (
                            moment,
                            gesture,
                            mood,
                            intensity
                        ) VALUES (
                            $1,
                            $2::jsonb,
                            'neutral',
                            0.7
                        )
                        RETURNING id
                    """,
                    datetime.now(timezone.utc),
                    json.dumps({"type": "environmental_observation", "category": "sensor_data"})
                    )
                    
                    self._default_phenomenon_id = str(new_phenom['id'])
                    return self._default_phenomenon_id
                    
        except Exception as e:
            logger.error(f"Failed to get/create phenomenon: {e}")
            return None
    
    async def process_observation(
        self,
        device_id: str,
        readings: Dict[str, float],
        location: Dict[str, float],
        student_wallet: Optional[str] = None,  # Kept for backward compatibility but not used
        metadata: Optional[Dict[str, Any]] = None
    ) -> ObservationResult:
        """
        Process a complete environmental observation
        
        Args:
            device_id: Sensor or observer identifier
            readings: Environmental measurements
            location: Geographic coordinates
            student_wallet: DEPRECATED - system now auto-looks up muxed addresses
            metadata: Additional observation metadata
            
        Returns:
            ObservationResult with processing details
        """
        observation_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Initialize result
        result = ObservationResult(
            observation_id=observation_id,
            ipfs_cid=None,
            stellar_tx_hash=None,
            tokens_distributed=Decimal("0"),
            blockchain_verified=False,
            timestamp=timestamp,
            muxed_address=None
        )
        
        # Prepare observation data
        observation_data = {
            "observation_id": observation_id,
            "device_id": device_id,
            "timestamp": timestamp,
            "readings": readings,
            "location": location,
            "metadata": metadata or {},
            "reciprocal_economy": {
                "value_created": str(self.BASE_OBSERVATION_VALUE),
            }
        }
        
        # Step 1: Store on IPFS (permanent storage)
        if self.ipfs_available:
            try:
                from ipfs_service import ObservationData
                
                ipfs_obs = ObservationData(
                    device_id=device_id,
                    timestamp=timestamp,
                    readings=readings,
                    location=location,
                    metadata=observation_data["metadata"]
                )
                
                result.ipfs_cid = await self.ipfs.store_observation(ipfs_obs)
                if result.ipfs_cid:
                    logger.info(f"Observation stored on IPFS: {result.ipfs_cid}")
                    observation_data["ipfs_cid"] = result.ipfs_cid
                    result.blockchain_verified = True
            except Exception as e:
                logger.error(f"IPFS storage failed: {e}")
        
        # Step 2: Look up muxed address and send reciprocal tokens
        if self.stellar_available:
            try:
                # Look up the device's muxed address from database
                muxed_address = await self._get_device_muxed_address(device_id)
                
                if muxed_address:
                    result.muxed_address = muxed_address
                    
                    # Calculate token amount
                    token_amount = self.BASE_OBSERVATION_VALUE
                    if "sensor" in device_id.lower() or "sb" in device_id.lower():
                        token_amount += self.SENSOR_BONUS
                    
                    # Send UBECrc tokens to muxed address
                    logger.info(f"Sending {token_amount} UBECrc to muxed address {muxed_address[:15]}...")
                    
                    tx_result = await self.stellar.send_ubecrc_payment(
                        destination=muxed_address,
                        amount=str(token_amount),
                        memo=f"obs:{observation_id[:8]}"
                    )
                    
                    if tx_result and tx_result.get("success"):
                        result.stellar_tx_hash = tx_result.get("transaction_hash")
                        result.tokens_distributed = token_amount
                        result.blockchain_verified = True
                        logger.info(f"✓ Distributed {token_amount} UBECrc to {muxed_address[:15]}...")
                        logger.info(f"  TX: {result.stellar_tx_hash[:16]}...")
                        
                        observation_data["stellar_tx_hash"] = result.stellar_tx_hash
                        observation_data["tokens_distributed"] = str(token_amount)
                        observation_data["muxed_address"] = muxed_address
                    else:
                        logger.warning(f"Payment failed: {tx_result}")
                else:
                    logger.info(f"No muxed address found for device {device_id} - skipping payment")
                    logger.info(f"  Register the device via /api/v2/observers/register to enable payments")
                    
            except Exception as e:
                logger.error(f"Token distribution failed: {e}", exc_info=True)
        
        # Step 3: Record in database (for queries and analysis)
        if self.db_available:
            try:
                await self.record_observation(observation_data)
                logger.info(f"Observation recorded in database: {observation_id}")
            except Exception as e:
                logger.error(f"Database recording failed: {e}")
        
        return result
    
    async def record_observation(self, observation_data: dict) -> None:
        """
        Record observation in the phenomenological database
        
        Args:
            observation_data: Complete observation data
        """
        if not self.db_available:
            return
        
        try:
            schema = "phenomenological"
            
            # Get or create observer
            device_id = observation_data.get("device_id")
            observer_id = await self._get_or_create_observer(device_id)
            
            if not observer_id:
                logger.warning("Could not create observer - skipping database record")
                return
            
            # Get or create phenomenon
            phenomenon_id = await self._get_or_create_phenomenon()
            
            if not phenomenon_id:
                logger.warning("Could not create phenomenon - skipping database record")
                return
            
            # Create observation record
            if hasattr(self.db, 'pool'):
                async with self.db.pool.acquire() as conn:
                    await conn.execute(f"""
                        INSERT INTO {schema}.observations (
                            observer_id,
                            phenomenon_id,
                            perception,
                            attention_quality,
                            clarity
                        ) VALUES (
                            $1::uuid,
                            $2::uuid,
                            $3::jsonb,
                            0.8,
                            0.7
                        )
                    """,
                    uuid.UUID(observer_id),
                    uuid.UUID(phenomenon_id),
                    json.dumps(observation_data)
                    )
                    
        except Exception as e:
            logger.error(f"Failed to record observation in database: {e}")
    
    async def close(self):
        """Cleanup resources"""
        logger.info("Observation service closing")


"""
Attribution: This project uses the services of Claude and Anthropic PBC
to inform our decisions and recommendations. This project was made
possible with the assistance of Claude and Anthropic PBC.
"""
