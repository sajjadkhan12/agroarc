"""
Fertilizer Recommendation API Routes
Endpoints for fertilizer prediction based on soil nutrients and conditions
"""

from fastapi import APIRouter, HTTPException, status
from ..schemas.fertilizer import (
    FertilizerPredictionRequest,
    FertilizerPredictionResponse,
    FertilizerBatchPredictionRequest,
    FertilizerBatchPredictionResponse
)
from ..core.models import model_manager
from ..core.exceptions import PredictionError, InvalidInputError, EncoderError
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/fertilizer",
    tags=["Fertilizer Recommendation"],
    responses={
        400: {"description": "Invalid input"},
        500: {"description": "Internal server error"}
    }
)


@router.post(
    "/predict",
    response_model=FertilizerPredictionResponse,
    summary="Predict recommended fertilizer",
    description="Get fertilizer recommendation based on soil nutrients and conditions"
)
async def predict_fertilizer(request: FertilizerPredictionRequest) -> FertilizerPredictionResponse:
    """
    Predict the best fertilizer based on input parameters
    
    - **temperature**: Temperature in Celsius
    - **humidity**: Humidity percentage (0-100)
    - **moisture**: Soil moisture percentage
    - **soil_type**: Type of soil (Sandy, Loamy, Clayey)
    - **crop_type**: Type of crop (Rice, Maize, Sugarcane, Cotton, Wheat)
    - **nitrogen**: Soil nitrogen level (N) in mg/kg
    - **phosphorus**: Soil phosphorus level (P) in mg/kg
    - **potassium**: Soil potassium level (K) in mg/kg
    
    Returns the recommended fertilizer with confidence score
    """
    try:
        # Encode categorical variables
        soil_encoded = model_manager.encode_categorical("soil", request.soil_type)
        crop_encoded = model_manager.encode_categorical("crop", request.crop_type)
        
        # Prepare features in correct order
        features = [
            request.temperature,
            request.humidity,
            request.moisture,
            soil_encoded,
            crop_encoded,
            request.nitrogen,
            request.phosphorus,
            request.potassium
        ]
        
        # Get prediction
        result = model_manager.predict_fertilizer(features)
        
        logger.info(f"Fertilizer prediction: {result['fertilizer']} (confidence: {result['confidence']}%)")
        
        return FertilizerPredictionResponse(**result)
        
    except EncoderError as e:
        logger.error(f"Encoding error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e.detail)
        )
    except PredictionError as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e.detail)
        )
    except Exception as e:
        logger.error(f"Unexpected error in fertilizer prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to make fertilizer prediction"
        )


@router.post(
    "/batch-predict",
    response_model=FertilizerBatchPredictionResponse,
    summary="Batch predict fertilizers",
    description="Get recommendations for multiple fertilizer requests"
)
async def batch_predict_fertilizers(request: FertilizerBatchPredictionRequest) -> FertilizerBatchPredictionResponse:
    """
    Predict fertilizers for multiple requests in batch
    
    Accepts up to 100 prediction requests at once.
    Returns a list of predictions with confidence scores.
    """
    try:
        results = []
        
        for fert_request in request.predictions:
            soil_encoded = model_manager.encode_categorical("soil", fert_request.soil_type)
            crop_encoded = model_manager.encode_categorical("crop", fert_request.crop_type)
            
            features = [
                fert_request.temperature,
                fert_request.humidity,
                fert_request.moisture,
                soil_encoded,
                crop_encoded,
                fert_request.nitrogen,
                fert_request.phosphorus,
                fert_request.potassium
            ]
            
            result = model_manager.predict_fertilizer(features)
            results.append(FertilizerPredictionResponse(**result))
        
        logger.info(f"Batch fertilizer predictions completed: {len(results)} fertilizers")
        
        return FertilizerBatchPredictionResponse(
            results=results,
            total=len(results)
        )
        
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Batch prediction failed"
        )


@router.get(
    "/supported-fertilizers",
    summary="Get supported fertilizers",
    description="List all fertilizers that the model can recommend"
)
async def get_supported_fertilizers() -> dict:
    """
    Get list of all supported fertilizers
    
    Returns the fertilizer types the model can recommend
    """
    try:
        fertilizers = list(model_manager.fertilizer_encoder.classes_)
        return {
            "fertilizers": fertilizers,
            "total": len(fertilizers)
        }
    except Exception as e:
        logger.error(f"Error fetching supported fertilizers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch supported fertilizers"
        )


@router.get(
    "/supported-soil-types",
    summary="Get supported soil types",
    description="List all soil types accepted by the model"
)
async def get_supported_soil_types() -> dict:
    """Get list of supported soil types"""
    return {
        "soil_types": ["Sandy", "Loamy", "Clayey"],
        "total": 3
    }


@router.get(
    "/supported-crop-types",
    summary="Get supported crop types",
    description="List all crop types accepted by the fertilizer model"
)
async def get_supported_crop_types() -> dict:
    """Get list of supported crop types for fertilizer model"""
    return {
        "crop_types": ["Rice", "Maize", "Sugarcane", "Cotton", "Wheat"],
        "total": 5
    }
