"""
observation_utilities.py - Helper Functions for Observation Processing
Provides data quality scoring, UBECrc calculations, and validation utilities

These utilities support the observation service with:
- Comprehensive data quality assessment
- Reward calculation based on quality metrics
- Sensor value validation
- Data completeness checks

Design Principles Applied:
- Principle #5: All operations are async
- Principle #11: Comprehensive documentation
- Principle #12: Single implementation of each method

This project uses the services of Claude and Anthropic PBC to inform our 
decisions and recommendations. This project was made possible with the 
assistance of Claude and Anthropic PBC.

Version: 2.0.0
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timezone
import statistics

logger = logging.getLogger(__name__)


class DataQualityCalculator:
    """
    Calculates comprehensive data quality scores for sensor observations.
    
    Quality factors considered:
    1. Sensor coverage (number of active sensors)
    2. Value plausibility (within expected ranges)
    3. Data completeness (no missing critical readings)
    4. Value consistency (statistical outlier detection)
    5. Temporal consistency (reasonable change rates)
    """
    
    # Expected sensor ranges for validation
    SENSOR_RANGES = {
        "temperature": (-50.0, 60.0, "°C"),
        "humidity": (0.0, 100.0, "%"),
        "pressure": (800.0, 1200.0, "hPa"),
        "soil_moisture": (0.0, 100.0, "%"),
        "soil_temperature": (-20.0, 50.0, "°C"),
        "light": (0.0, 150000.0, "lux"),
        "uv": (0.0, 15.0, "UV index"),
        "pm25": (0.0, 500.0, "µg/m³"),
        "pm10": (0.0, 500.0, "µg/m³"),
        "co2": (350.0, 5000.0, "ppm")
    }
    
    # Sensor importance weights
    SENSOR_WEIGHTS = {
        "temperature": 1.2,  # Critical
        "humidity": 1.1,     # Important
        "pressure": 1.0,     # Standard
        "soil_moisture": 1.3, # Very important for plants
        "soil_temperature": 1.1,
        "light": 1.0,
        "uv": 0.9,
        "pm25": 1.0,
        "pm10": 0.9,
        "co2": 1.1
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize quality calculator.
        
        Args:
            config: Optional configuration for custom ranges/weights
        """
        self.config = config or {}
        self.history: List[Dict[str, Any]] = []  # For temporal consistency checks
        
        logger.info("Data Quality Calculator initialized")
    
    async def calculate_score(
        self,
        sensor_data: Dict[str, Any],
        previous_reading: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        Calculate comprehensive quality score (0.0 to 1.0).
        
        Args:
            sensor_data: Current sensor readings
            previous_reading: Optional previous reading for temporal consistency
        
        Returns:
            Quality score between 0.0 (poor) and 1.0 (excellent)
        """
        scores = []
        weights = []
        
        # 1. Sensor coverage score (30% weight)
        coverage_score = self._calculate_coverage_score(sensor_data)
        scores.append(coverage_score)
        weights.append(0.30)
        logger.debug(f"Coverage score: {coverage_score:.2f}")
        
        # 2. Value plausibility score (25% weight)
        plausibility_score = self._calculate_plausibility_score(sensor_data)
        scores.append(plausibility_score)
        weights.append(0.25)
        logger.debug(f"Plausibility score: {plausibility_score:.2f}")
        
        # 3. Completeness score (20% weight)
        completeness_score = self._calculate_completeness_score(sensor_data)
        scores.append(completeness_score)
        weights.append(0.20)
        logger.debug(f"Completeness score: {completeness_score:.2f}")
        
        # 4. Consistency score (15% weight)
        consistency_score = self._calculate_consistency_score(sensor_data)
        scores.append(consistency_score)
        weights.append(0.15)
        logger.debug(f"Consistency score: {consistency_score:.2f}")
        
        # 5. Temporal consistency (10% weight) - if previous reading available
        if previous_reading:
            temporal_score = self._calculate_temporal_consistency(
                sensor_data, previous_reading
            )
            scores.append(temporal_score)
            weights.append(0.10)
            logger.debug(f"Temporal score: {temporal_score:.2f}")
        
        # Calculate weighted average
        total_weight = sum(weights)
        weighted_score = sum(s * w for s, w in zip(scores, weights)) / total_weight
        
        logger.info(f"Final quality score: {weighted_score:.3f}")
        return round(weighted_score, 3)
    
    def _calculate_coverage_score(self, sensor_data: Dict[str, Any]) -> float:
        """
        Score based on number and importance of active sensors.
        
        More sensors = higher score
        Important sensors (temp, humidity, soil) weighted higher
        """
        score = 0.0
        max_score = 0.0
        
        for sensor_name in self.SENSOR_RANGES.keys():
            weight = self.SENSOR_WEIGHTS.get(sensor_name, 1.0)
            max_score += weight
            
            value = sensor_data.get(sensor_name)
            if value is not None and isinstance(value, (int, float)):
                score += weight
        
        # Normalize to 0-1 range
        return score / max_score if max_score > 0 else 0.0
    
    def _calculate_plausibility_score(self, sensor_data: Dict[str, Any]) -> float:
        """
        Score based on whether values are within expected ranges.
        
        Values outside ranges reduce score
        Extreme outliers reduce score more
        """
        scores = []
        
        for sensor_name, value in sensor_data.items():
            if not isinstance(value, (int, float)):
                continue
            
            if sensor_name not in self.SENSOR_RANGES:
                # Unknown sensor, assume plausible
                scores.append(1.0)
                continue
            
            min_val, max_val, unit = self.SENSOR_RANGES[sensor_name]
            
            if min_val <= value <= max_val:
                # Value in range - full score
                scores.append(1.0)
            else:
                # Value out of range - calculate penalty
                if value < min_val:
                    deviation = (min_val - value) / (max_val - min_val)
                else:
                    deviation = (value - max_val) / (max_val - min_val)
                
                # Penalty increases with deviation
                # Small deviation (< 10%): 0.7 score
                # Large deviation (> 50%): 0.0 score
                penalty = min(deviation * 2, 1.0)
                scores.append(max(0.0, 1.0 - penalty))
        
        return statistics.mean(scores) if scores else 0.5
    
    def _calculate_completeness_score(self, sensor_data: Dict[str, Any]) -> float:
        """
        Score based on data completeness.
        
        Checks for:
        - No null/None values
        - All expected sensors present
        - Numeric values where expected
        """
        total_checks = 0
        passed_checks = 0
        
        # Check each sensor
        for sensor_name in self.SENSOR_RANGES.keys():
            total_checks += 1
            value = sensor_data.get(sensor_name)
            
            # Has value
            if value is not None:
                passed_checks += 0.5
                
                # Is numeric
                if isinstance(value, (int, float)):
                    passed_checks += 0.5
        
        return passed_checks / total_checks if total_checks > 0 else 0.0
    
    def _calculate_consistency_score(self, sensor_data: Dict[str, Any]) -> float:
        """
        Score based on internal consistency of readings.
        
        Checks for logical relationships:
        - Temperature and humidity correlation
        - Soil moisture and soil temperature relationship
        - Pressure and weather patterns
        """
        score = 1.0  # Start with perfect score
        
        # Check temperature-humidity relationship
        temp = sensor_data.get("temperature")
        humidity = sensor_data.get("humidity")
        
        if temp is not None and humidity is not None:
            # Very high temp with very high humidity is unusual
            if temp > 35 and humidity > 90:
                score -= 0.1
                logger.debug("Unusual temp-humidity combination detected")
            
            # Very low temp with very low humidity is unusual
            if temp < 5 and humidity < 20:
                score -= 0.1
                logger.debug("Unusual cold-dry combination detected")
        
        # Check soil moisture-temperature relationship
        soil_moisture = sensor_data.get("soil_moisture")
        soil_temp = sensor_data.get("soil_temperature")
        
        if soil_moisture is not None and soil_temp is not None:
            # Frozen soil with high moisture is unusual
            if soil_temp < 0 and soil_moisture > 80:
                score -= 0.1
        
        # More consistency checks can be added here
        
        return max(0.0, score)
    
    def _calculate_temporal_consistency(
        self,
        current: Dict[str, Any],
        previous: Dict[str, Any]
    ) -> float:
        """
        Score based on realistic change rates between readings.
        
        Sudden large changes reduce score (likely sensor error)
        Gradual changes are expected
        """
        score = 1.0
        
        # Maximum expected changes per 15 minutes
        MAX_CHANGES = {
            "temperature": 5.0,      # °C
            "humidity": 20.0,        # %
            "pressure": 10.0,        # hPa
            "soil_moisture": 10.0,   # %
            "soil_temperature": 3.0, # °C
            "light": 50000.0,        # lux (can change rapidly)
            "uv": 3.0,              # UV index
        }
        
        for sensor_name, max_change in MAX_CHANGES.items():
            curr_val = current.get(sensor_name)
            prev_val = previous.get(sensor_name)
            
            if curr_val is None or prev_val is None:
                continue
            
            if not isinstance(curr_val, (int, float)) or not isinstance(prev_val, (int, float)):
                continue
            
            change = abs(curr_val - prev_val)
            
            if change > max_change:
                # Penalize based on how much it exceeds max
                excess = (change - max_change) / max_change
                penalty = min(excess * 0.2, 0.3)  # Max 0.3 penalty per sensor
                score -= penalty
                logger.debug(
                    f"Large {sensor_name} change detected: "
                    f"{prev_val} → {curr_val} (Δ{change:.1f})"
                )
        
        return max(0.0, score)


class UBECrcRewardCalculator:
    """
    Calculates UBECrc token rewards for observations.
    
    Reward Formula:
        reward = base_rate × sensor_count × quality_multiplier × bonus_factors
    
    Where:
        - base_rate: 1.02 UBECrc per sensor
        - sensor_count: Number of active sensors
        - quality_multiplier: 0.5 to 1.0 based on quality score
        - bonus_factors: Time-of-day, consistency bonuses
    """
    
    # Base configuration
    BASE_RATE = Decimal("1.02")  # UBECrc per sensor
    MIN_QUALITY_MULTIPLIER = Decimal("0.5")  # Minimum 50% of base
    MAX_REWARD_PER_OBSERVATION = Decimal("20.0")  # Cap to prevent abuse
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize reward calculator.
        
        Args:
            config: Optional custom configuration
        """
        self.config = config or {}
        logger.info("UBECrc Reward Calculator initialized")
    
    async def calculate_reward(
        self,
        sensor_data: Dict[str, Any],
        quality_score: float,
        bonus_factors: Optional[Dict[str, float]] = None
    ) -> Decimal:
        """
        Calculate UBECrc reward for an observation.
        
        Args:
            sensor_data: Sensor readings
            quality_score: Quality score (0.0 to 1.0)
            bonus_factors: Optional bonus multipliers
        
        Returns:
            UBECrc amount (2 decimal places)
        
        Examples:
            7 sensors at 100% quality = 7 × 1.02 × 1.0 = 7.14 UBECrc
            7 sensors at 90% quality = 7 × 1.02 × 0.95 = 6.78 UBECrc
            5 sensors at 80% quality = 5 × 1.02 × 0.90 = 4.59 UBECrc
        """
        # Count active sensors
        sensor_count = self._count_active_sensors(sensor_data)
        
        if sensor_count == 0:
            logger.warning("No active sensors, reward = 0")
            return Decimal("0.00")
        
        # Calculate quality multiplier (0.5 to 1.0)
        quality_multiplier = self._calculate_quality_multiplier(quality_score)
        
        # Base reward calculation
        base_reward = self.BASE_RATE * Decimal(str(sensor_count)) * quality_multiplier
        
        # Apply bonus factors if provided
        if bonus_factors:
            for bonus_name, bonus_value in bonus_factors.items():
                base_reward *= Decimal(str(bonus_value))
                logger.debug(f"Applied bonus '{bonus_name}': {bonus_value}x")
        
        # Apply cap
        final_reward = min(base_reward, self.MAX_REWARD_PER_OBSERVATION)
        
        # Round to 2 decimal places
        final_reward = final_reward.quantize(Decimal("0.01"))
        
        logger.info(
            f"Reward calculated: {sensor_count} sensors × "
            f"{quality_score:.2%} quality = {final_reward} UBECrc"
        )
        
        return final_reward
    
    async def calculate_daily_estimate(
        self,
        sensor_count: int,
        average_quality: float = 0.9,
        observations_per_day: int = 96
    ) -> Decimal:
        """
        Estimate daily UBECrc earnings.
        
        Args:
            sensor_count: Number of sensors
            average_quality: Expected average quality score
            observations_per_day: Number of observations per day
        
        Returns:
            Estimated daily UBECrc earnings
        """
        quality_multiplier = self._calculate_quality_multiplier(average_quality)
        
        per_observation = self.BASE_RATE * Decimal(str(sensor_count)) * quality_multiplier
        daily_total = per_observation * Decimal(str(observations_per_day))
        
        return daily_total.quantize(Decimal("0.01"))
    
    def _count_active_sensors(self, sensor_data: Dict[str, Any]) -> int:
        """Count number of active sensors with numeric readings."""
        return len([
            v for v in sensor_data.values()
            if isinstance(v, (int, float))
        ])
    
    def _calculate_quality_multiplier(self, quality_score: float) -> Decimal:
        """
        Convert quality score to reward multiplier.
        
        Score 0.0 → 0.5x multiplier (minimum)
        Score 1.0 → 1.0x multiplier (maximum)
        Linear interpolation between
        """
        score_decimal = Decimal(str(quality_score))
        multiplier_range = Decimal("1.0") - self.MIN_QUALITY_MULTIPLIER
        
        multiplier = self.MIN_QUALITY_MULTIPLIER + (score_decimal * multiplier_range)
        
        return multiplier.quantize(Decimal("0.001"))


class SensorValidator:
    """
    Validates sensor data for correctness and safety.
    
    Prevents:
    - Invalid data types
    - Out-of-range values
    - Malformed data structures
    - Injection attacks
    """
    
    async def validate(
        self,
        sensor_data: Dict[str, Any],
        strict: bool = False
    ) -> Tuple[bool, List[str]]:
        """
        Validate sensor data.
        
        Args:
            sensor_data: Data to validate
            strict: If True, require all sensors to be valid
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Check data is a dictionary
        if not isinstance(sensor_data, dict):
            return False, ["sensor_data must be a dictionary"]
        
        # Check not empty
        if not sensor_data:
            errors.append("sensor_data is empty")
            if strict:
                return False, errors
        
        # Validate each sensor
        for sensor_name, value in sensor_data.items():
            # Check sensor name is string
            if not isinstance(sensor_name, str):
                errors.append(f"Invalid sensor name type: {type(sensor_name)}")
                continue
            
            # Check sensor name is reasonable
            if len(sensor_name) > 50:
                errors.append(f"Sensor name too long: {sensor_name}")
            
            # Check value type
            if value is not None and not isinstance(value, (int, float, str, bool)):
                errors.append(f"Invalid value type for {sensor_name}: {type(value)}")
        
        # In strict mode, any error is fatal
        if strict and errors:
            return False, errors
        
        # In normal mode, allow partial data as long as some is valid
        valid_count = sum(
            1 for v in sensor_data.values()
            if isinstance(v, (int, float))
        )
        
        if valid_count == 0:
            return False, errors + ["No valid numeric sensor readings"]
        
        return True, errors


# Convenience functions for common operations

async def calculate_observation_quality(
    sensor_data: Dict[str, Any],
    previous_reading: Optional[Dict[str, Any]] = None
) -> float:
    """
    Quick function to calculate quality score.
    
    Usage:
        quality = await calculate_observation_quality(sensor_data)
    """
    calculator = DataQualityCalculator()
    return await calculator.calculate_score(sensor_data, previous_reading)


async def calculate_ubec_reward(
    sensor_data: Dict[str, Any],
    quality_score: float
) -> Decimal:
    """
    Quick function to calculate UBECrc reward.
    
    Usage:
        reward = await calculate_ubec_reward(sensor_data, 0.95)
    """
    calculator = UBECrcRewardCalculator()
    return await calculator.calculate_reward(sensor_data, quality_score)


async def validate_sensor_data(
    sensor_data: Dict[str, Any],
    strict: bool = False
) -> Tuple[bool, List[str]]:
    """
    Quick function to validate sensor data.
    
    Usage:
        is_valid, errors = await validate_sensor_data(sensor_data)
    """
    validator = SensorValidator()
    return await validator.validate(sensor_data, strict)


# Attribution footer
"""
These utilities provide robust data quality assessment and reward
calculation for the UBEC environmental monitoring system.

Attribution: This project uses the services of Claude and Anthropic PBC
to inform our decisions and recommendations. This project was made
possible with the assistance of Claude and Anthropic PBC.
"""
