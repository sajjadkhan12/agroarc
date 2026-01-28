"""
Crop Recommendation Request/Response Schemas
Pydantic models for request validation and response serialization
"""

from pydantic import BaseModel, Field
from typing import Optional


class CropPredictionRequest(BaseModel):
    """
    Request schema for crop recommendation
    
    Attributes:
        nitrogen: Soil nitrogen level (N) in mg/kg
        phosphorus: Soil phosphorus level (P) in mg/kg
        potassium: Soil potassium level (K) in mg/kg
        temperature: Temperature in Celsius
        humidity: Humidity percentage (0-100)
        ph: Soil pH level (0-14)
        rainfall: Rainfall in mm
    """
    
    nitrogen: float = Field(
        ..., 
        ge=0, 
        description="Nitrogen level (N) in mg/kg"
    )
    phosphorus: float = Field(
        ..., 
        ge=0, 
        description="Phosphorus level (P) in mg/kg"
    )
    potassium: float = Field(
        ..., 
        ge=0, 
        description="Potassium level (K) in mg/kg"
    )
    temperature: float = Field(
        ..., 
        ge=-50, 
        le=60, 
        description="Temperature in Celsius"
    )
    humidity: float = Field(
        ..., 
        ge=0, 
        le=100, 
        description="Humidity percentage"
    )
    ph: float = Field(
        ..., 
        ge=0, 
        le=14, 
        description="Soil pH level"
    )
    rainfall: float = Field(
        ..., 
        ge=0, 
        description="Rainfall in mm"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "nitrogen": 50,
                "phosphorus": 40,
                "potassium": 30,
                "temperature": 25.5,
                "humidity": 65.0,
                "ph": 6.8,
                "rainfall": 200.0
            }
        }


class CropPredictionResponse(BaseModel):
    """
    Response schema for crop recommendation
    
    Attributes:
        crop: Recommended crop name
        confidence: Prediction confidence percentage
        encoded_value: Internal encoded value (for reference)
    """
    
    crop: str = Field(..., description="Recommended crop name")
    confidence: float = Field(..., ge=0, le=100, description="Confidence percentage")
    encoded_value: int = Field(..., description="Encoded crop value")
    
    class Config:
        json_schema_extra = {
            "example": {
                "crop": "Rice",
                "confidence": 98.5,
                "encoded_value": 5
            }
        }


class CropBatchPredictionRequest(BaseModel):
    """Request schema for batch crop predictions"""
    
    predictions: list[CropPredictionRequest] = Field(
        ..., 
        min_items=1,
        max_items=100,
        description="List of crop prediction requests"
    )


class CropBatchPredictionResponse(BaseModel):
    """Response schema for batch crop predictions"""
    
    results: list[CropPredictionResponse] = Field(
        ..., 
        description="List of predictions"
    )
    total: int = Field(..., description="Total number of predictions")
