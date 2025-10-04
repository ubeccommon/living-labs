# phenomenological_models.py
"""
Phenomenological Data Models - Reciprocal Economy Edition
Represents living observations with reciprocal value exchange

This module defines data models for the phenomenological observation system
with integrated reciprocal economy and blockchain verification.

Attribution: This project uses the services of Claude and Anthropic PBC.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from enum import Enum


# ============================================================
# OBSERVER MODELS
# ============================================================

class ObserverType(str, Enum):
    """Types of observers in the system"""
    DEVICE = "device"
    HUMAN = "human"
    COMMUNITY = "community"
    COLLECTIVE = "collective"


class SensoryCapacities(BaseModel):
    """What an observer can perceive"""
    sight: bool = False
    touch: bool = False
    smell: bool = False
    hearing: bool = False
    taste: bool = False
    intuition: bool = False
    technological: bool = False
    
    # Extended capacities for devices
    temperature: Optional[bool] = None
    humidity: Optional[bool] = None
    pressure: Optional[bool] = None
    light: Optional[bool] = None
    soil: Optional[bool] = None
    uv: Optional[bool] = None
    air_quality: Optional[bool] = None


class ObserverEntity(BaseModel):
    """An observer in the phenomenological system"""
    id: Optional[UUID] = None
    type: ObserverType
    external_identity: Dict[str, Any]
    essence: Dict[str, Any]
    sensory_capacities: SensoryCapacities
    presence_began: datetime
    presence_continues: bool = True
    relationships: Optional[Dict] = Field(default_factory=dict)
    rhythms: Optional[Dict] = Field(default_factory=dict)
    reciprocity_score: Optional[float] = Field(default=0.5, ge=0.0, le=1.0)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "device",
                "external_identity": {
                    "device_id": "SENS_001",
                    "serial_number": "SN12345",
                    "name": "Garden Monitor"
                },
                "essence": {
                    "location": {"lat": 52.3928, "lon": 14.5317},
                    "sensors": ["temperature", "humidity", "soil_moisture"],
                    "timezone": "Europe/Berlin"
                },
                "sensory_capacities": {
                    "technological": True,
                    "temperature": True,
                    "humidity": True,
                    "soil": True
                },
                "presence_began": "2024-01-20T10:00:00Z",
                "presence_continues": True,
                "reciprocity_score": 0.85
            }
        }
    }


# ============================================================
# PHENOMENON MODELS
# ============================================================

class PhenomenonMood(str, Enum):
    """Atmospheric qualities of phenomena"""
    VIBRANT = "vibrant"
    QUIET = "quiet"
    MYSTERIOUS = "mysterious"
    PLEASANT = "pleasant"
    OPPRESSIVE = "oppressive"
    ARID = "arid"
    CRISP = "crisp"
    NEUTRAL = "neutral"
    TURBULENT = "turbulent"
    SERENE = "serene"


class PhenomenonGesture(BaseModel):
    """Movement qualities of a phenomenon"""
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    soil_moisture: Optional[float] = None
    soil_temperature: Optional[float] = None
    light_intensity: Optional[float] = None
    uv_index: Optional[float] = None
    
    # Qualitative gestures
    movement: Optional[str] = None  # "expanding", "contracting", "spiraling"
    quality: Optional[str] = None   # "warm", "cool", "moist", "dry"
    
    @field_validator('temperature', 'humidity', 'pressure', 'soil_moisture', 'light_intensity', 'uv_index')
    @classmethod
    def validate_ranges(cls, v: Optional[float], info) -> Optional[float]:
        if v is not None:
            if info.field_name == 'humidity' and not 0 <= v <= 100:
                raise ValueError(f"Humidity must be between 0 and 100, got {v}")
            if info.field_name == 'temperature' and not -50 <= v <= 60:
                raise ValueError(f"Temperature must be reasonable, got {v}")
        return v


class PhenomenonEvent(BaseModel):
    """An observable event in the living world"""
    id: Optional[UUID] = None
    moment: datetime
    duration: Optional[str] = None  # ISO 8601 duration
    location: Optional[tuple[float, float]] = None  # (lon, lat)
    gesture: PhenomenonGesture
    mood: Optional[PhenomenonMood] = PhenomenonMood.NEUTRAL
    intensity: float = Field(default=0.5, ge=0.0, le=1.0)
    context_web: Optional[Dict] = Field(default_factory=dict)
    influenced_by: Optional[List[UUID]] = Field(default_factory=list)
    influences: Optional[List[UUID]] = Field(default_factory=list)
    resonances: Optional[List[str]] = Field(default_factory=list)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "moment": "2024-01-20T10:00:00Z",
                "location": [14.5317, 52.3928],
                "gesture": {
                    "temperature": 22.5,
                    "humidity": 65.0,
                    "movement": "expanding",
                    "quality": "warm"
                },
                "mood": "pleasant",
                "intensity": 0.3,
                "resonances": ["growth", "morning", "awakening"]
            }
        }
    }


# ============================================================
# OBSERVATION MODELS
# ============================================================

class ObservationPerception(BaseModel):
    """Raw sensory data from observation"""
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    soil_moisture: Optional[float] = None
    soil_temperature: Optional[float] = None
    light: Optional[float] = None
    uv: Optional[float] = None
    
    # Human perceptions
    visual: Optional[str] = None
    auditory: Optional[str] = None
    tactile: Optional[str] = None
    olfactory: Optional[str] = None
    
    # Extended device perceptions
    air_quality: Optional[float] = None
    co2_level: Optional[float] = None
    noise_level: Optional[float] = None


class ObservationImagination(BaseModel):
    """Patterns and forms perceived in observation"""
    form: Optional[str] = None  # "warming_trend", "cooling_pattern"
    pattern: Optional[str] = None  # "morning_rise", "evening_decline"
    time_pattern: Optional[str] = None
    weather_pattern: Optional[str] = None
    metaphor: Optional[str] = None  # "like a breath", "dance of light"
    ecological_pattern: Optional[str] = None  # "growth phase", "dormancy"


class ObservationExperience(BaseModel):
    """The meeting of observer and phenomenon"""
    id: Optional[UUID] = None
    observer_id: UUID
    phenomenon_id: UUID
    observed_at: datetime
    perception: ObservationPerception
    imagination: Optional[ObservationImagination] = None
    inspiration: Optional[Dict] = None  # Insights discovered
    intuition: Optional[Dict] = None  # Direct knowing
    attention_quality: float = Field(default=0.5, ge=0.0, le=1.0)
    clarity: float = Field(default=0.5, ge=0.0, le=1.0)
    iteration_number: int = 1
    builds_on: Optional[UUID] = None
    changed_observer: Optional[Dict] = None
    changed_phenomenon: Optional[Dict] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "observer_id": "550e8400-e29b-41d4-a716-446655440000",
                "phenomenon_id": "550e8400-e29b-41d4-a716-446655440001",
                "observed_at": "2024-01-20T10:00:00Z",
                "perception": {
                    "temperature": 22.5,
                    "humidity": 65.0,
                    "soil_moisture": 45.0
                },
                "imagination": {
                    "form": "warming_trend",
                    "pattern": "morning_rise",
                    "time_pattern": "morning_awakening"
                },
                "attention_quality": 0.85,
                "clarity": 0.90
            }
        }
    }


# ============================================================
# PATTERN MODELS
# ============================================================

class PatternArchetype(str, Enum):
    """Types of patterns that can emerge"""
    DAILY_RHYTHM = "daily_rhythm"
    SEASONAL_CYCLE = "seasonal_cycle"
    WARMING_TREND = "warming_trend"
    COOLING_TREND = "cooling_trend"
    STABLE_TEMPERATURE = "stable_temperature"
    TEMPERATURE_OSCILLATION = "temperature_oscillation"
    HIGH_HUMIDITY_PERIOD = "high_humidity_period"
    LOW_HUMIDITY_PERIOD = "low_humidity_period"
    OSCILLATION = "oscillation"
    SPIRAL = "spiral"
    BRANCHING = "branching"
    PULSATION = "pulsation"
    EMERGENCE = "emergence"
    DISSOLUTION = "dissolution"


class PatternEmergence(BaseModel):
    """A recognized pattern in observations"""
    id: Optional[UUID] = None
    archetype: PatternArchetype
    scale: Optional[str] = None  # "micro", "human", "landscape", "cosmic"
    instances: List[UUID] = Field(default_factory=list)
    recognition_count: int = 1
    strength: float = Field(default=0.5, ge=0.0, le=1.0)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    first_recognized: datetime
    last_seen: datetime
    is_emerging: bool = True
    is_dissolving: bool = False
    seasonal_affinity: Optional[Dict] = None
    lunar_affinity: Optional[Dict] = None
    diurnal_affinity: Optional[Dict] = None


# ============================================================
# RECIPROCAL ECONOMY MODELS (Replaces Gift Economy)
# ============================================================

class ExchangeType(str, Enum):
    """Types of reciprocal exchanges in the system"""
    DATA_CONTRIBUTION = "data_contribution"
    ANALYSIS_CONTRIBUTION = "analysis_contribution"
    PATTERN_RECOGNITION = "pattern_recognition"
    INFRASTRUCTURE_MAINTENANCE = "infrastructure_maintenance"
    INQUIRY_CONTRIBUTION = "inquiry_contribution"
    NETWORK_CONTRIBUTION = "network_contribution"
    OBSERVATION = "observation"  # Legacy support
    INSIGHT = "insight"  # Legacy support


class ReciprocalExchange(BaseModel):
    """A reciprocal value exchange in the system"""
    id: Optional[UUID] = None
    contributor_id: UUID  # Was giver_id
    exchange_type: ExchangeType  # Was gift_type
    reciprocity_score: float = Field(default=0.8, ge=0.0, le=1.0)  # Was generosity
    relevance: float = Field(default=0.8, ge=0.0, le=1.0)
    beauty: float = Field(default=0.6, ge=0.0, le=1.0)
    
    # Reciprocal value tracking
    ubec_reciprocity_value: Decimal = Field(default=Decimal("0"))  # Was ubec_expression
    value_provided: Dict[str, Any] = Field(default_factory=dict)
    value_received: Dict[str, Any] = Field(default_factory=dict)
    reciprocal_balance: Decimal = Field(default=Decimal("0"))
    
    # Blockchain verification
    ipfs_hash: Optional[str] = None
    stellar_transaction_hash: Optional[str] = None
    blockchain_verified: bool = False
    ipfs_metadata: Optional[Dict] = Field(default_factory=dict)
    
    # Recipients and timing
    received_by: Optional[List[UUID]] = Field(default_factory=list)
    reciprocated_by: Optional[List[UUID]] = Field(default_factory=list)
    offered_at: datetime
    received_at: Optional[datetime] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "contributor_id": "550e8400-e29b-41d4-a716-446655440000",
                "exchange_type": "data_contribution",
                "reciprocity_score": 0.85,
                "ubec_reciprocity_value": "7.14",
                "value_provided": {
                    "observation_id": "550e8400-e29b-41d4-a716-446655440001",
                    "data_points": 7,
                    "quality_score": 0.95
                },
                "value_received": {
                    "ubecrc_tokens": 7.14,
                    "type": "utility_token"
                },
                "ipfs_hash": "QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco",
                "offered_at": "2024-01-20T10:00:00Z"
            }
        }
    }


# ============================================================
# LEARNING JOURNEY MODELS
# ============================================================

class LearningJourney(BaseModel):
    """Educational pathway through phenomena"""
    id: Optional[UUID] = None
    traveler_id: UUID  # Observer on the journey
    guide_id: Optional[UUID] = None  # Mentor/teacher
    stages: List[Dict] = Field(default_factory=list)
    current_stage: int = 0
    wonder_moments: List[Dict] = Field(default_factory=list)
    confusion_moments: List[Dict] = Field(default_factory=list)
    clarity_moments: List[Dict] = Field(default_factory=list)
    pace: Optional[str] = "moderate"  # "contemplative", "moderate", "eager"
    depth_tendency: float = Field(default=0.5, ge=0.0, le=1.0)
    breadth_tendency: float = Field(default=0.5, ge=0.0, le=1.0)
    initial_understanding: Optional[Dict] = None
    current_understanding: Optional[Dict] = None
    capacities_developed: List[str] = Field(default_factory=list)
    reciprocal_contributions: int = 0  # Number of value exchanges


# ============================================================
# API RESPONSE MODELS
# ============================================================

class ObservationResponse(BaseModel):
    """Response after creating an observation"""
    success: bool
    observation_id: UUID
    phenomenon_id: UUID
    patterns_detected: Optional[List[str]] = None
    reciprocal_exchange_id: Optional[UUID] = None  # Was gift_created
    ipfs_hash: Optional[str] = None
    blockchain_verified: bool = False
    message: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "observation_id": "550e8400-e29b-41d4-a716-446655440002",
                "phenomenon_id": "550e8400-e29b-41d4-a716-446655440001",
                "patterns_detected": ["morning_warming", "daily_rhythm"],
                "reciprocal_exchange_id": "550e8400-e29b-41d4-a716-446655440003",
                "ipfs_hash": "QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco",
                "blockchain_verified": False,
                "message": "Observation recorded and reciprocal exchange created"
            }
        }
    }


class PatternDiscoveryResponse(BaseModel):
    """Response when patterns are discovered"""
    patterns_found: List[PatternEmergence]
    total_count: int
    emerging_count: int
    dissolving_count: int
    reciprocal_reward: Optional[Decimal] = None  # Bonus for pattern discovery
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "patterns_found": [
                    {
                        "archetype": "daily_rhythm",
                        "scale": "landscape",
                        "recognition_count": 15,
                        "strength": 0.85,
                        "is_emerging": True
                    }
                ],
                "total_count": 5,
                "emerging_count": 3,
                "dissolving_count": 1,
                "reciprocal_reward": "10.0"
            }
        }
    }


class ReciprocalBalanceResponse(BaseModel):
    """Response showing reciprocal balance for a contributor"""
    contributor_id: UUID
    value_provided_total: Dict[str, Any]
    value_received_total: Dict[str, Any]
    blockchain_status: Dict[str, Any]
    balance: Decimal
    reciprocity_score: float
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "contributor_id": "550e8400-e29b-41d4-a716-446655440000",
                "value_provided_total": {
                    "total_contributions": 100,
                    "data_points": 700,
                    "ipfs_stored": 95
                },
                "value_received_total": {
                    "total_tokens": 714.0,
                    "paid_tokens": 700.0
                },
                "blockchain_status": {
                    "verified_count": 90,
                    "ipfs_count": 95,
                    "stellar_count": 98
                },
                "balance": "714.0",
                "reciprocity_score": 0.85
            }
        }
    }


class ExchangeStatisticsResponse(BaseModel):
    """Response with reciprocal exchange statistics"""
    total_exchanges: int
    unique_contributors: int
    ipfs_stored: int
    stellar_paid: int
    fully_verified: int
    total_tokens: Decimal
    avg_reciprocity_score: float
    avg_balance: Decimal
    verification_rate: float
    period_days: int
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "total_exchanges": 1000,
                "unique_contributors": 25,
                "ipfs_stored": 950,
                "stellar_paid": 980,
                "fully_verified": 940,
                "total_tokens": "7140.0",
                "avg_reciprocity_score": 0.82,
                "avg_balance": "285.6",
                "verification_rate": 94.0,
                "period_days": 7
            }
        }
    }


# ============================================================
# BLOCKCHAIN VERIFICATION MODELS
# ============================================================

class BlockchainVerificationRequest(BaseModel):
    """Request to verify blockchain integrity"""
    exchange_id: UUID
    ipfs_hash: Optional[str] = None
    stellar_transaction_hash: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "exchange_id": "550e8400-e29b-41d4-a716-446655440003",
                "ipfs_hash": "QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco",
                "stellar_transaction_hash": "stellar_tx_hash_example"
            }
        }
    }


class BlockchainVerificationResponse(BaseModel):
    """Response after blockchain verification"""
    exchange_id: UUID
    ipfs_verified: bool
    stellar_verified: bool
    fully_verified: bool
    ipfs_gateway_url: Optional[str] = None
    stellar_explorer_url: Optional[str] = None
    verification_timestamp: datetime
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "exchange_id": "550e8400-e29b-41d4-a716-446655440003",
                "ipfs_verified": True,
                "stellar_verified": True,
                "fully_verified": True,
                "ipfs_gateway_url": "https://gateway.pinata.cloud/ipfs/QmXoy...",
                "stellar_explorer_url": "https://stellar.expert/explorer/public/tx/...",
                "verification_timestamp": "2024-01-20T10:00:00Z"
            }
        }
    }


# ============================================================
# BACKWARD COMPATIBILITY ALIASES (Remove after full migration)
# ============================================================

# These aliases maintain backward compatibility during transition
GiftType = ExchangeType  # Deprecated
GiftOffering = ReciprocalExchange  # Deprecated


# ============================================================
# VALIDATION HELPERS
# ============================================================

def validate_stellar_address(address: str) -> bool:
    """Validate Stellar address format"""
    if not address:
        return False
    # Stellar addresses start with 'G' and are 56 characters
    return len(address) == 56 and address.startswith('G')


def validate_ipfs_hash(hash_str: str) -> bool:
    """Validate IPFS hash format"""
    if not hash_str:
        return False
    # IPFS hashes typically start with 'Qm' and are 46 characters
    return len(hash_str) == 46 and hash_str.startswith('Qm')
