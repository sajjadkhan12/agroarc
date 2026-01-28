"""
Core Pydantic schemas for AgroArc Backend
Simple, lightweight data models for request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal


# ============================================================================
# CROP RECOMMENDATION SCHEMAS
# ============================================================================

class CropRequest(BaseModel):
    """
    Crop Prediction Request Schema
    
    Validates soil nutrient levels and environmental conditions
    to predict the most suitable crop.
    
    Validation:
    - Nitrogen (N): Non-negative, typically 0-100+ mg/kg
    - Phosphorus (P): Non-negative, typically 0-100+ mg/kg
    - Potassium (K): Non-negative, typically 0-100+ mg/kg
    - Temperature: -50 to 60°C (realistic for agriculture)
    - Humidity: 0-100% (percentage)
    - pH: 0-14 (standard soil pH scale)
    - Rainfall: Non-negative, in mm/month
    """
    
    # Soil nutrients (in mg/kg)
    N: float = Field(
        ...,
        ge=0,
        title="Nitrogen",
        description="Soil nitrogen level in mg/kg"
    )
    P: float = Field(
        ...,
        ge=0,
        title="Phosphorus",
        description="Soil phosphorus level in mg/kg"
    )
    K: float = Field(
        ...,
        ge=0,
        title="Potassium",
        description="Soil potassium level in mg/kg"
    )
    
    # Environmental factors
    temperature: float = Field(
        ...,
        ge=-50,
        le=60,
        title="Temperature",
        description="Temperature in Celsius"
    )
    humidity: float = Field(
        ...,
        ge=0,
        le=100,
        title="Humidity",
        description="Relative humidity as percentage (0-100)"
    )
    ph: float = Field(
        ...,
        ge=0,
        le=14,
        title="Soil pH",
        description="Soil pH value (0-14 scale)"
    )
    rainfall: float = Field(
        ...,
        ge=0,
        title="Rainfall",
        description="Monthly rainfall in mm"
    )
    
    class Config:
        # Example data for API documentation
        json_schema_extra = {
            "example": {
                "N": 50,
                "P": 40,
                "K": 30,
                "temperature": 25.5,
                "humidity": 65.0,
                "ph": 6.8,
                "rainfall": 200.0
            }
        }


class CropResponse(BaseModel):
    """
    Crop Prediction Response Schema
    
    Returns the model's prediction for the best crop
    along with confidence score.
    
    Fields:
    - recommended_crop: The predicted crop name
    - confidence: Prediction confidence (0-100%)
    """
    
    recommended_crop: str = Field(
        ...,
        title="Recommended Crop",
        description="The crop recommended by the model"
    )
    confidence: float = Field(
        ...,
        ge=0,
        le=100,
        title="Confidence Score",
        description="Confidence percentage of the prediction (0-100)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "recommended_crop": "Rice",
                "confidence": 98.5
            }
        }


# ============================================================================
# FERTILIZER RECOMMENDATION SCHEMAS
# ============================================================================

class FertilizerRequest(BaseModel):
    """
    Fertilizer Prediction Request Schema
    
    Validates soil conditions, crop type, and environmental factors
    to predict the best fertilizer for the farmer.
    
    Validation:
    - Temperature: -50 to 60°C
    - Humidity: 0-100% (percentage)
    - Moisture: 0-100% (soil moisture percentage)
    - Soil_Type: Must be one of (Sandy, Loamy, Clayey)
    - Crop_Type: Must be one of (Rice, Maize, Sugarcane, Cotton, Wheat)
    - Nitrogen: Non-negative (mg/kg)
    - Phosphorus: Non-negative (mg/kg)
    - Potassium: Non-negative (mg/kg)
    """
    
    # Environmental conditions
    Temperature: float = Field(
        ...,
        ge=-50,
        le=60,
        title="Temperature",
        description="Air temperature in Celsius"
    )
    Humidity: float = Field(
        ...,
        ge=0,
        le=100,
        title="Humidity",
        description="Relative humidity as percentage (0-100)"
    )
    Moisture: float = Field(
        ...,
        ge=0,
        le=100,
        title="Soil Moisture",
        description="Soil moisture content as percentage (0-100)"
    )
    
    # Categorical variables (must match training data)
    Soil_Type: Literal["Sandy", "Loamy", "Clayey"] = Field(
        ...,
        title="Soil Type",
        description="Type of soil: Sandy, Loamy, or Clayey"
    )
    Crop_Type: Literal["Rice", "Maize", "Sugarcane", "Cotton", "Wheat"] = Field(
        ...,
        title="Crop Type",
        description="Type of crop being grown"
    )
    
    # Soil nutrients (in mg/kg)
    Nitrogen: float = Field(
        ...,
        ge=0,
        title="Nitrogen",
        description="Soil nitrogen level in mg/kg"
    )
    Phosphorous: float = Field(
        ...,
        ge=0,
        title="Phosphorus",
        description="Soil phosphorus level in mg/kg"
    )
    Potassium: float = Field(
        ...,
        ge=0,
        title="Potassium",
        description="Soil potassium level in mg/kg"
    )
    
    class Config:
        # Example data for API documentation
        json_schema_extra = {
            "example": {
                "Temperature": 28.0,
                "Humidity": 70.0,
                "Moisture": 45.0,
                "Soil_Type": "Loamy",
                "Crop_Type": "Rice",
                "Nitrogen": 35.0,
                "Phosphorous": 15.0,
                "Potassium": 10.0
            }
        }


class FertilizerResponse(BaseModel):
    """
    Fertilizer Prediction Response Schema
    
    Returns the model's prediction for the best fertilizer
    to apply based on the given conditions.
    
    Fields:
    - recommended_fertilizer: The predicted fertilizer name
    - confidence: Prediction confidence (0-100%)
    """
    
    recommended_fertilizer: str = Field(
        ...,
        title="Recommended Fertilizer",
        description="The fertilizer recommended by the model"
    )
    confidence: float = Field(
        ...,
        ge=0,
        le=100,
        title="Confidence Score",
        description="Confidence percentage of the prediction (0-100)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "recommended_fertilizer": "17-17-17",
                "confidence": 99.8
            }
        }
