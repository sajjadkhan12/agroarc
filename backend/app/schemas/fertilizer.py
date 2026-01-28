"""
Fertilizer Recommendation Request/Response Schemas
Pydantic models for request validation and response serialization
"""

from pydantic import BaseModel, Field
from typing import Literal


class FertilizerPredictionRequest(BaseModel):
    """
    Request schema for fertilizer recommendation
    
    Attributes:
        temperature: Temperature in Celsius
        humidity: Humidity percentage (0-100)
        moisture: Soil moisture percentage
        soil_type: Type of soil
        crop_type: Type of crop
        nitrogen: Soil nitrogen level (N) in mg/kg
        phosphorus: Soil phosphorus level (P) in mg/kg
        potassium: Soil potassium level (K) in mg/kg
    """
    
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
    moisture: float = Field(
        ..., 
        ge=0, 
        le=100, 
        description="Soil moisture percentage"
    )
    soil_type: Literal["Sandy", "Loamy", "Clayey"] = Field(
        ..., 
        description="Type of soil"
    )
    crop_type: Literal["Rice", "Maize", "Sugarcane", "Cotton", "Wheat"] = Field(
        ..., 
        description="Type of crop"
    )
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
    
    class Config:
        json_schema_extra = {
            "example": {
                "temperature": 28.0,
                "humidity": 70.0,
                "moisture": 45.0,
                "soil_type": "Loamy",
                "crop_type": "Rice",
                "nitrogen": 35.0,
                "phosphorus": 15.0,
                "potassium": 10.0
            }
        }


class FertilizerPredictionResponse(BaseModel):
    """
    Response schema for fertilizer recommendation
    
    Attributes:
        fertilizer: Recommended fertilizer name
        confidence: Prediction confidence percentage
        encoded_value: Internal encoded value (for reference)
    """
    
    fertilizer: str = Field(..., description="Recommended fertilizer name")
    confidence: float = Field(..., ge=0, le=100, description="Confidence percentage")
    encoded_value: int = Field(..., description="Encoded fertilizer value")
    
    class Config:
        json_schema_extra = {
            "example": {
                "fertilizer": "17-17-17",
                "confidence": 99.8,
                "encoded_value": 3
            }
        }


class FertilizerBatchPredictionRequest(BaseModel):
    """Request schema for batch fertilizer predictions"""
    
    predictions: list[FertilizerPredictionRequest] = Field(
        ..., 
        min_items=1,
        max_items=100,
        description="List of fertilizer prediction requests"
    )


class FertilizerBatchPredictionResponse(BaseModel):
    """Response schema for batch fertilizer predictions"""
    
    results: list[FertilizerPredictionResponse] = Field(
        ..., 
        description="List of predictions"
    )
    total: int = Field(..., description="Total number of predictions")
