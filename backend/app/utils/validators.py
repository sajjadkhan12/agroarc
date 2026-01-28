"""
Input validation helpers for AgroArc Backend
"""

from typing import List, Tuple
from ..core.exceptions import InvalidInputError


def validate_crop_features(features: List[float]) -> bool:
    """
    Validate crop prediction features
    
    Args:
        features: List of feature values [N, P, K, temp, humidity, pH, rainfall]
    
    Returns:
        True if valid, raises InvalidInputError otherwise
    """
    if len(features) != 7:
        raise InvalidInputError(f"Expected 7 features, got {len(features)}")
    
    # N, P, K
    if features[0] < 0 or features[1] < 0 or features[2] < 0:
        raise InvalidInputError("N, P, K values must be non-negative")
    
    # Temperature
    if features[3] < -50 or features[3] > 60:
        raise InvalidInputError("Temperature must be between -50 and 60 Celsius")
    
    # Humidity
    if features[4] < 0 or features[4] > 100:
        raise InvalidInputError("Humidity must be between 0 and 100")
    
    # pH
    if features[5] < 0 or features[5] > 14:
        raise InvalidInputError("pH must be between 0 and 14")
    
    # Rainfall
    if features[6] < 0:
        raise InvalidInputError("Rainfall must be non-negative")
    
    return True


def validate_fertilizer_features(features: List[float], encoders_dict: dict) -> bool:
    """
    Validate fertilizer prediction features
    
    Args:
        features: List of feature values
        encoders_dict: Dictionary of encoders
    
    Returns:
        True if valid, raises InvalidInputError otherwise
    """
    if len(features) != 8:
        raise InvalidInputError(f"Expected 8 features, got {len(features)}")
    
    # Temperature
    if features[0] < -50 or features[0] > 60:
        raise InvalidInputError("Temperature must be between -50 and 60 Celsius")
    
    # Humidity
    if features[1] < 0 or features[1] > 100:
        raise InvalidInputError("Humidity must be between 0 and 100")
    
    # Moisture
    if features[2] < 0 or features[2] > 100:
        raise InvalidInputError("Moisture must be between 0 and 100")
    
    # N, P, K
    if features[5] < 0 or features[6] < 0 or features[7] < 0:
        raise InvalidInputError("N, P, K values must be non-negative")
    
    return True


def normalize_temperature(temp: float, from_unit: str = "celsius") -> float:
    """
    Normalize temperature to Celsius
    
    Args:
        temp: Temperature value
        from_unit: Unit of temperature (celsius, fahrenheit, kelvin)
    
    Returns:
        Temperature in Celsius
    """
    if from_unit.lower() == "fahrenheit":
        return (temp - 32) * 5/9
    elif from_unit.lower() == "kelvin":
        return temp - 273.15
    elif from_unit.lower() == "celsius":
        return temp
    else:
        raise InvalidInputError(f"Unknown temperature unit: {from_unit}")


def validate_categorical_value(value: str, allowed_values: List[str]) -> bool:
    """
    Validate categorical value against allowed values
    
    Args:
        value: Value to validate
        allowed_values: List of allowed values
    
    Returns:
        True if valid, raises InvalidInputError otherwise
    """
    if value not in allowed_values:
        raise InvalidInputError(
            f"Invalid value '{value}'. Allowed values: {', '.join(allowed_values)}"
        )
    return True
