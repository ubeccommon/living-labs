# phenomenological_db.py
"""
Phenomenological Database Interface - Reciprocal Economy Edition
Transforms mechanical data collection into living observations with reciprocal value exchange

This module bridges sensor devices with the phenomenological database,
treating each data point as an observation experience and tracking
the reciprocal exchange of value between contributors and the system.

Attribution: This project uses the services of Claude and Anthropic PBC.
"""

import asyncio
import asyncpg
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone, timedelta
from uuid import UUID, uuid4
from decimal import Decimal
import json
import logging

logger = logging.getLogger(__name__)


class PhenomenologicalDB:
    """Database interface for phenomenological observations with reciprocal economy"""
    
    def __init__(self, database_url: str, schema: str = 'phenomenological', 
                 search_path: str = 'phenomenological,ubec_sensors,public'):
        """
        Initialize database connection.
        
        Args:
            database_url: PostgreSQL connection URL
            schema: Primary schema name (default: 'phenomenological')
            search_path: Comma-separated schema search path
        """
        self.database_url = database_url
        self.schema = schema
        self.search_path = search_path
        self.pool = None
    
    @staticmethod
    def _safe_json_parse(value):
        """
        Safely parse a value that might be JSON string or already parsed dict
        
        Args:
            value: Could be dict, str (JSON), or None
            
        Returns:
            dict or None
        """
        if value is None:
            return None
        if isinstance(value, dict):
            return value
        if isinstance(value, str):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, ValueError):
                return None
        return None
    
    async def connect(self):
        """
        Establish connection pool to database with schema configuration.
        """
        self.pool = await asyncpg.create_pool(
            self.database_url,
            min_size=5,
            max_size=20,
            command_timeout=60,
            server_settings={
                'search_path': self.search_path
            }
        )
        logger.info(f"Database connected with search_path: {self.search_path}")
    
    async def close(self):
        """Close database connections"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection closed")
    
    # ============================================================
    # OBSERVER MANAGEMENT
    # ============================================================
    
    async def create_observer(self, 
                              observer_type: str,
                              external_identity: Dict,
                              essence: Dict,
                              sensory_capacities: Optional[Dict] = None) -> UUID:
        """
        Create a new observer entity (device or human)
        
        Args:
            observer_type: 'device' or 'human'
            external_identity: External identifiers (device_id, email, etc.)
            essence: Core qualities and characteristics
            sensory_capacities: What the observer can perceive
        
        Returns:
            UUID of created observer
        """
        if sensory_capacities is None:
            sensory_capacities = self._default_capacities(observer_type)
        
        external_identity['type'] = observer_type
        
        async with self.pool.acquire() as conn:
            observer_id = await conn.fetchval("""
                INSERT INTO observers (
                    observer_type,
                    external_identity,
                    essence,
                    sensory_capacities,
                    presence_began,
                    presence_continues
                ) VALUES ($1, $2, $3, $4, NOW(), true)
                RETURNING id
            """,
                observer_type,
                json.dumps(external_identity),
                json.dumps(essence),
                json.dumps(sensory_capacities)
            )
            logger.info(f"Created {observer_type} observer: {observer_id}")
            return observer_id
    
    async def get_observer_by_device_id(self, device_id: str) -> Optional[Dict]:
        """Get observer by legacy device ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM observers
                WHERE external_identity->>'device_id' = $1
                AND external_identity->>'type' = 'device'
            """, device_id)
            return dict(row) if row else None
    
    async def get_observer_by_email(self, email: str) -> Optional[Dict]:
        """Get human observer by email"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM observers
                WHERE external_identity->>'email' = $1
                AND external_identity->>'type' = 'human'
            """, email)
            return dict(row) if row else None
    
    async def get_observer(self, observer_id: UUID) -> Optional[Dict]:
        """Get observer by ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM observers WHERE id = $1
            """, observer_id)
            return dict(row) if row else None
    
    # ============================================================
    # PHENOMENON CREATION
    # ============================================================
    
    async def create_phenomenon(self,
                                moment: datetime,
                                location: Optional[tuple] = None,
                                gesture: Dict = None,
                                mood: Optional[str] = None,
                                intensity: float = 0.5,
                                context_web: Optional[Dict] = None) -> UUID:
        """
        Create a phenomenon (an observable event in the world)
        
        Args:
            moment: When the phenomenon occurred
            location: Spatial coordinates (lon, lat)
            gesture: Qualitative expression of the phenomenon
            mood: Atmospheric quality
            intensity: Strength of presence (0-1)
            context_web: Surrounding conditions
        
        Returns:
            UUID of created phenomenon
        """
        point = None
        if location:
            point = f"POINT({location[0]} {location[1]})"
        
        async with self.pool.acquire() as conn:
            phenomenon_id = await conn.fetchval("""
                INSERT INTO phenomena (
                    moment,
                    location,
                    gesture,
                    mood,
                    intensity,
                    context_web
                ) VALUES ($1, $2::geometry, $3, $4, $5, $6)
                RETURNING id
            """,
                moment,
                point,
                json.dumps(gesture or {}),
                mood,
                intensity,
                json.dumps(context_web or {})
            )
            logger.debug(f"Created phenomenon: {phenomenon_id}")
            return phenomenon_id
    
    # ============================================================
    # OBSERVATION RECORDING
    # ============================================================
    
    async def create_observation(self,
                                observer_id: UUID,
                                phenomenon_id: UUID,
                                perception: Dict,
                                imagination: Optional[Dict] = None,
                                attention_quality: float = 0.5,
                                clarity: float = 0.5,
                                conditions: Optional[Dict] = None) -> UUID:
        """
        Record an observation (meeting of observer and phenomenon)
        
        Args:
            observer_id: The observer making the observation
            phenomenon_id: The phenomenon being observed
            perception: Raw sensory data
            imagination: Patterns or forms perceived
            attention_quality: Quality of attention (0-1)
            clarity: Clarity of observation (0-1)
            conditions: Environmental conditions during observation
        
        Returns:
            UUID of created observation
        """
        async with self.pool.acquire() as conn:
            observation_id = await conn.fetchval("""
                INSERT INTO observations (
                    observer_id,
                    phenomenon_id,
                    perceived_at,
                    perception,
                    imagination,
                    attention_quality,
                    clarity,
                    conditions
                ) VALUES ($1, $2, NOW(), $3, $4, $5, $6, $7)
                RETURNING id
            """,
                observer_id,
                phenomenon_id,
                json.dumps(perception),
                json.dumps(imagination) if imagination else None,
                attention_quality,
                clarity,
                json.dumps(conditions or {})
            )
            logger.debug(f"Created observation: {observation_id}")
            return observation_id
    
    # ============================================================
    # PATTERN RECOGNITION
    # ============================================================
    
    async def check_for_patterns(self, observer_id: UUID, phenomenon_id: UUID):
        """Check if this observation reveals any patterns"""
        async with self.pool.acquire() as conn:
            # Get recent observations by this observer
            recent = await conn.fetch("""
                SELECT o.*, p.gesture, p.mood
                FROM observations o
                JOIN phenomena p ON o.phenomenon_id = p.id
                WHERE o.observer_id = $1
                AND o.perceived_at > NOW() - INTERVAL '7 days'
                ORDER BY o.perceived_at DESC
                LIMIT 20
            """, observer_id)
            
            # Analyze for patterns
            if len(recent) >= 3:
                patterns = self._analyze_patterns(recent)
                for pattern_type, strength in patterns.items():
                    if strength > 0.6:  # Pattern threshold
                        await self._record_pattern(
                            pattern_type, 
                            observer_id,
                            phenomenon_id, 
                            strength
                        )
    
    # ============================================================
    # RECIPROCAL ECONOMY (Replaces Gift Economy)
    # ============================================================
    
    async def create_reciprocal_exchange(self,
                                        contributor_id: UUID,
                                        exchange_type: str,
                                        ubec_reciprocity_value: Decimal,
                                        ipfs_hash: Optional[str] = None,
                                        value_provided: Optional[Dict] = None,
                                        value_received: Optional[Dict] = None,
                                        recipients: Optional[List[UUID]] = None) -> UUID:
        """
        Record a reciprocal value exchange in the system
        
        Args:
            contributor_id: Observer contributing value
            exchange_type: Type of exchange (data_contribution, pattern_recognition, etc.)
            ubec_reciprocity_value: UBECrc tokens for the exchange
            ipfs_hash: IPFS hash for blockchain verification
            value_provided: What the contributor provides
            value_received: What the contributor receives
            recipients: Who benefits from the exchange
        
        Returns:
            UUID of created reciprocal exchange
        """
        # Prepare value structures
        if value_provided is None:
            value_provided = {
                'type': exchange_type,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        
        if value_received is None:
            value_received = {
                'ubecrc_tokens': float(ubec_reciprocity_value),
                'type': 'utility_token'
            }
        
        async with self.pool.acquire() as conn:
            exchange_id = await conn.fetchval("""
                INSERT INTO reciprocal_exchanges (
                    contributor_id,
                    exchange_type,
                    ubec_reciprocity_value,
                    ipfs_hash,
                    value_provided,
                    value_received,
                    received_by,
                    offered_at,
                    reciprocity_score,
                    relevance,
                    beauty,
                    reciprocal_balance
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW(), $8, $9, $10, $11)
                RETURNING id
            """,
                contributor_id,
                exchange_type,
                ubec_reciprocity_value,
                ipfs_hash,
                json.dumps(value_provided),
                json.dumps(value_received),
                recipients or [],
                0.8,  # Default reciprocity score
                0.8,  # Default relevance
                0.6,  # Default beauty
                ubec_reciprocity_value  # Initial balance equals tokens
            )
            
            logger.info(f"Created reciprocal exchange {exchange_id}: "
                       f"{exchange_type} for {ubec_reciprocity_value} UBECrc")
            return exchange_id
    
    async def verify_blockchain_integrity(self,
                                         exchange_id: UUID,
                                         ipfs_hash: Optional[str] = None,
                                         stellar_tx: Optional[str] = None) -> bool:
        """
        Verify and update blockchain integrity for a reciprocal exchange
        
        Args:
            exchange_id: The exchange to verify
            ipfs_hash: IPFS content identifier
            stellar_tx: Stellar transaction hash
        
        Returns:
            True if fully verified (both IPFS and Stellar present)
        """
        async with self.pool.acquire() as conn:
            # Use the function created by migration
            verified = await conn.fetchval("""
                SELECT phenomenological.verify_blockchain_integrity($1, $2, $3)
            """, exchange_id, ipfs_hash, stellar_tx)
            
            if verified:
                logger.info(f"Exchange {exchange_id} fully blockchain verified")
            else:
                logger.debug(f"Exchange {exchange_id} partially verified")
            
            return verified
    
    async def get_pending_exchanges(self, limit: int = 100) -> List[Dict]:
        """Get reciprocal exchanges pending Stellar payment"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM reciprocal_exchanges
                WHERE stellar_transaction_hash IS NULL
                ORDER BY offered_at DESC
                LIMIT $1
            """, limit)
            return [dict(row) for row in rows]
    
    async def get_verified_exchanges(self, 
                                    contributor_id: Optional[UUID] = None,
                                    limit: int = 100) -> List[Dict]:
        """Get fully blockchain verified exchanges"""
        async with self.pool.acquire() as conn:
            if contributor_id:
                rows = await conn.fetch("""
                    SELECT * FROM reciprocal_exchanges
                    WHERE blockchain_verified = TRUE
                    AND contributor_id = $1
                    ORDER BY offered_at DESC
                    LIMIT $2
                """, contributor_id, limit)
            else:
                rows = await conn.fetch("""
                    SELECT * FROM reciprocal_exchanges
                    WHERE blockchain_verified = TRUE
                    ORDER BY offered_at DESC
                    LIMIT $1
                """, limit)
            return [dict(row) for row in rows]
    
    async def get_reciprocal_balance(self, contributor_id: UUID) -> Dict:
        """
        Get comprehensive reciprocal balance for a contributor
        
        Returns dict with:
            - value_provided_total: Total value contributed
            - value_received_total: Total value received
            - blockchain_status: Verification statistics
            - balance: Net reciprocal balance
        """
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow("""
                SELECT * FROM phenomenological.get_reciprocal_balance($1)
            """, contributor_id)
            
            if result:
                return {
                    'value_provided_total': self._safe_json_parse(result['value_provided_total']),
                    'value_received_total': self._safe_json_parse(result['value_received_total']),
                    'blockchain_status': self._safe_json_parse(result['blockchain_status']),
                    'balance': float(result['balance']) if result['balance'] else 0
                }
            return {
                'value_provided_total': {},
                'value_received_total': {},
                'blockchain_status': {},
                'balance': 0
            }
    
    async def calculate_reciprocity_score(self, contributor_id: UUID) -> float:
        """Calculate average reciprocity score for contributor over last 30 days"""
        async with self.pool.acquire() as conn:
            score = await conn.fetchval("""
                SELECT phenomenological.calculate_reciprocity_score($1)
            """, contributor_id)
            return float(score) if score else 0.5
    
    # ============================================================
    # BACKWARDS COMPATIBILITY (Temporary - Remove after code update)
    # ============================================================
    
    async def create_gift(self, giver_id: UUID, gift_type: str, 
                         ubec_amount: float = 0, recipients: Optional[List[UUID]] = None) -> UUID:
        """
        DEPRECATED: Use create_reciprocal_exchange instead
        Backward compatibility wrapper for gift economy calls
        """
        logger.warning("create_gift is deprecated - use create_reciprocal_exchange")
        
        # Map old gift types to new exchange types
        exchange_type_map = {
            'observation': 'data_contribution',
            'insight': 'analysis_contribution',
            'pattern': 'pattern_recognition',
            'care': 'infrastructure_maintenance',
            'question': 'inquiry_contribution',
            'connection': 'network_contribution'
        }
        
        exchange_type = exchange_type_map.get(gift_type, gift_type)
        
        return await self.create_reciprocal_exchange(
            contributor_id=giver_id,
            exchange_type=exchange_type,
            ubec_reciprocity_value=Decimal(str(ubec_amount)),
            recipients=recipients
        )
    
    # ============================================================
    # STATISTICS AND ANALYTICS
    # ============================================================
    
    async def get_exchange_statistics(self, days: int = 7) -> Dict:
        """Get reciprocal exchange statistics for the specified period"""
        async with self.pool.acquire() as conn:
            stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_exchanges,
                    COUNT(DISTINCT contributor_id) as unique_contributors,
                    COUNT(ipfs_hash) as ipfs_stored,
                    COUNT(stellar_transaction_hash) as stellar_paid,
                    COUNT(CASE WHEN blockchain_verified THEN 1 END) as fully_verified,
                    SUM(ubec_reciprocity_value) as total_tokens,
                    AVG(reciprocity_score) as avg_reciprocity_score,
                    AVG(reciprocal_balance) as avg_balance
                FROM reciprocal_exchanges
                WHERE offered_at > NOW() - INTERVAL '%s days'
            """ % days)
            
            return {
                'total_exchanges': stats['total_exchanges'],
                'unique_contributors': stats['unique_contributors'],
                'ipfs_stored': stats['ipfs_stored'],
                'stellar_paid': stats['stellar_paid'],
                'fully_verified': stats['fully_verified'],
                'total_tokens': float(stats['total_tokens']) if stats['total_tokens'] else 0,
                'avg_reciprocity_score': float(stats['avg_reciprocity_score']) if stats['avg_reciprocity_score'] else 0,
                'avg_balance': float(stats['avg_balance']) if stats['avg_balance'] else 0,
                'verification_rate': (stats['fully_verified'] / stats['total_exchanges'] * 100) if stats['total_exchanges'] > 0 else 0
            }
    
    # ============================================================
    # HELPER METHODS
    # ============================================================
    
    def _default_capacities(self, observer_type: str) -> Dict:
        """Get default sensory capacities for observer type"""
        if observer_type == 'device':
            return {
                'sight': False,
                'touch': False,
                'smell': False,
                'hearing': False,
                'taste': False,
                'intuition': False,
                'technological': True,
                'temperature': True,
                'humidity': True,
                'pressure': True
            }
        else:  # human
            return {
                'sight': True,
                'touch': True,
                'smell': True,
                'hearing': True,
                'taste': True,
                'intuition': True,
                'technological': False
            }
    
    def _determine_mood(self, gesture: Dict) -> str:
        """Determine atmospheric mood from sensor data"""
        temp = gesture.get('temperature', 20)
        humidity = gesture.get('humidity', 50)
        
        if temp > 30 and humidity > 70:
            return 'oppressive'
        elif temp > 25 and humidity < 40:
            return 'arid'
        elif temp < 10:
            return 'crisp'
        elif 18 <= temp <= 24 and 40 <= humidity <= 60:
            return 'pleasant'
        else:
            return 'neutral'
    
    def _calculate_intensity(self, gesture: Dict) -> float:
        """Calculate phenomenon intensity from data"""
        intensities = []
        
        if 'temperature' in gesture:
            temp_intensity = abs(gesture['temperature'] - 20) / 30
            intensities.append(min(1.0, temp_intensity))
        
        if 'humidity' in gesture:
            hum_intensity = abs(gesture['humidity'] - 50) / 50
            intensities.append(min(1.0, hum_intensity))
        
        if 'pressure' in gesture:
            pressure_intensity = abs(gesture['pressure'] - 1013) / 100
            intensities.append(min(1.0, pressure_intensity))
        
        if intensities:
            return sum(intensities) / len(intensities)
        return 0.5
    
    def _detect_patterns(self, gesture: Dict, timestamp: datetime) -> Optional[Dict]:
        """Detect patterns in sensor data"""
        patterns = {}
        
        # Time-based patterns
        hour = timestamp.hour
        if 5 <= hour <= 8:
            patterns['time_pattern'] = 'morning_awakening'
        elif 11 <= hour <= 14:
            patterns['time_pattern'] = 'midday_peak'
        elif 17 <= hour <= 20:
            patterns['time_pattern'] = 'evening_decline'
        elif 22 <= hour or hour <= 4:
            patterns['time_pattern'] = 'night_rest'
        
        # Environmental patterns
        if 'temperature' in gesture and 'humidity' in gesture:
            temp = gesture['temperature']
            humidity = gesture['humidity']
            
            if temp > 25 and humidity > 60:
                patterns['weather_pattern'] = 'tropical_condition'
            elif temp < 10 and humidity < 30:
                patterns['weather_pattern'] = 'winter_dry'
            elif 15 <= temp <= 25 and 40 <= humidity <= 60:
                patterns['weather_pattern'] = 'temperate_ideal'
        
        return patterns if patterns else None
    
    async def _record_pattern(self, pattern_type: str, observer_id: UUID,
                              phenomenon_id: UUID, strength: float):
        """Record a recognized pattern"""
        async with self.pool.acquire() as conn:
            # Check if pattern exists
            existing = await conn.fetchval("""
                SELECT id FROM patterns 
                WHERE pattern_type = $1 AND observer_id = $2
                ORDER BY created_at DESC LIMIT 1
            """, pattern_type, observer_id)
            
            if existing:
                # Update existing pattern
                await conn.execute("""
                    UPDATE patterns 
                    SET strength = $1,
                        last_seen_at = NOW(),
                        phenomenon_ids = array_append(
                            COALESCE(phenomenon_ids, ARRAY[]::uuid[]), 
                            $2
                        ),
                        updated_at = NOW()
                    WHERE id = $3
                """, strength, phenomenon_id, existing)
                logger.debug(f"Updated pattern {existing}: {pattern_type}")
            else:
                # Create new pattern
                await conn.execute("""
                    INSERT INTO patterns (
                        pattern_type,
                        observer_id,
                        phenomenon_ids,
                        strength,
                        confidence,
                        first_detected_at,
                        last_seen_at
                    ) VALUES ($1, $2, ARRAY[$3]::uuid[], $4, $5, NOW(), NOW())
                """, pattern_type, observer_id, phenomenon_id, strength, 0.7)
                logger.info(f"New pattern detected: {pattern_type}")
    
    def _analyze_patterns(self, observations: List[Dict]) -> Dict[str, float]:
        """
        Analyze observations for patterns
        """
        patterns = {}
        
        # Parse all gesture fields first
        parsed_observations = []
        for o in observations:
            gesture_raw = o.get('gesture')
            gesture = self._safe_json_parse(gesture_raw)
            if gesture:
                parsed_observations.append(gesture)
        
        if not parsed_observations:
            return patterns
        
        # Check for temperature trends
        temps = [g.get('temperature') for g in parsed_observations 
                if g.get('temperature') is not None]
        
        if len(temps) >= 3:
            # Rising trend
            if all(temps[i] <= temps[i+1] for i in range(len(temps)-1)):
                patterns['warming_trend'] = 0.9
            # Falling trend
            elif all(temps[i] >= temps[i+1] for i in range(len(temps)-1)):
                patterns['cooling_trend'] = 0.9
            # Stable
            elif all(abs(temps[i] - temps[0]) < 2 for i in range(len(temps))):
                patterns['stable_temperature'] = 0.8
            # Oscillation
            elif len(temps) >= 5:
                changes = [temps[i+1] - temps[i] for i in range(len(temps)-1)]
                ups = sum(1 for c in changes if c > 0)
                downs = sum(1 for c in changes if c < 0)
                if abs(ups - downs) <= 1:
                    patterns['temperature_oscillation'] = 0.7
        
        # Check humidity patterns
        humidities = [g.get('humidity') for g in parsed_observations 
                     if g.get('humidity') is not None]
        
        if len(humidities) >= 3:
            avg_humidity = sum(humidities) / len(humidities)
            if avg_humidity > 70:
                patterns['high_humidity_period'] = 0.8
            elif avg_humidity < 30:
                patterns['low_humidity_period'] = 0.8
        
        return patterns


# ============================================================
# EXAMPLE USAGE WITH RECIPROCAL ECONOMY
# ============================================================

async def example_reciprocal_usage():
    """Example of using the phenomenological database with reciprocal economy"""
    
    # Initialize database with schema configuration
    db = PhenomenologicalDB(
        "postgresql://user:pass@localhost/ubec_sensors",
        schema='phenomenological',
        search_path='phenomenological,ubec_sensors,public'
    )
    await db.connect()
    
    try:
        # Create a device observer
        observer_id = await db.create_observer(
            observer_type='device',
            external_identity={'device_id': 'SENS_001', 'serial': 'SN12345'},
            essence={'location': {'lat': 52.3, 'lon': 14.5}, 'sensors': ['temp', 'humidity', 'pressure']}
        )
        
        # Create a phenomenon
        phenomenon_id = await db.create_phenomenon(
            moment=datetime.now(timezone.utc),
            location=(14.5, 52.3),
            gesture={'temperature': 22.5, 'humidity': 65, 'pressure': 1013},
            mood='pleasant',
            intensity=0.3
        )
        
        # Record an observation
        observation_id = await db.create_observation(
            observer_id=observer_id,
            phenomenon_id=phenomenon_id,
            perception={'temperature': 22.5, 'humidity': 65, 'pressure': 1013},
            imagination={'pattern': 'morning_warming'},
            attention_quality=0.85,
            clarity=0.9
        )
        
        print(f"Created observation {observation_id}")
        
        # Check for patterns
        await db.check_for_patterns(observer_id, phenomenon_id)
        
        # Create a reciprocal exchange (replaces gift)
        exchange_id = await db.create_reciprocal_exchange(
            contributor_id=observer_id,
            exchange_type='data_contribution',
            ubec_reciprocity_value=Decimal('7.14'),
            value_provided={
                'observation_id': str(observation_id),
                'data_points': 3,
                'quality_score': 0.85
            },
            value_received={
                'ubecrc_tokens': 7.14,
                'type': 'utility_token'
            }
        )
        
        print(f"Created reciprocal exchange {exchange_id}")
        
        # Simulate IPFS storage and Stellar payment
        ipfs_hash = "QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco"
        stellar_tx = "stellar_tx_hash_example"
        
        # Verify blockchain integrity
        verified = await db.verify_blockchain_integrity(
            exchange_id,
            ipfs_hash,
            stellar_tx
        )
        
        print(f"Blockchain verified: {verified}")
        
        # Get reciprocal balance
        balance = await db.get_reciprocal_balance(observer_id)
        print(f"Reciprocal balance: {balance}")
        
        # Get exchange statistics
        stats = await db.get_exchange_statistics(days=7)
        print(f"7-day statistics: {stats}")
        
    finally:
        await db.close()


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run example
    asyncio.run(example_reciprocal_usage())
