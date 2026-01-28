"""
Crop Recommendation API Routes
Endpoints for crop prediction based on soil and environmental conditions
"""

from fastapi import APIRouter, HTTPException, status
from ..schemas.crop import (
    CropPredictionRequest,
    CropPredictionResponse,
    CropBatchPredictionRequest,
    CropBatchPredictionResponse
)
from ..core.models import model_manager
from ..core.exceptions import PredictionError, InvalidInputError
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/crop",
    tags=["Crop Recommendation"],
    responses={
        400: {"description": "Invalid input"},
        500: {"description": "Internal server error"}
    }
)


@router.post(
    "/predict",
    response_model=CropPredictionResponse,
    summary="Predict recommended crop",
    description="Get crop recommendation based on soil nutrients and environmental conditions"
)
async def predict_crop(request: CropPredictionRequest) -> CropPredictionResponse:
    """
    Predict the best crop based on input parameters
    
    - **nitrogen**: Soil nitrogen level (N) in mg/kg
    - **phosphorus**: Soil phosphorus level (P) in mg/kg
    - **potassium**: Soil potassium level (K) in mg/kg
    - **temperature**: Temperature in Celsius
    - **humidity**: Humidity percentage (0-100)
    - **ph**: Soil pH level (0-14)
    - **rainfall**: Rainfall in mm
    
    Returns the recommended crop with confidence score
    """
    try:
        # Prepare features in the correct order
        features = [
            request.nitrogen,
            request.phosphorus,
            request.potassium,
            request.temperature,
            request.humidity,
            request.ph,
            request.rainfall
        ]
        
        # Get prediction
        result = model_manager.predict_crop(features)
        
        logger.info(f"Crop prediction: {result['crop']} (confidence: {result['confidence']}%)")
        
        return CropPredictionResponse(**result)
        
    except PredictionError as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e.detail)
        )
    except Exception as e:
        logger.error(f"Unexpected error in crop prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to make crop prediction"
        )


@router.post(
    "/batch-predict",
    response_model=CropBatchPredictionResponse,
    summary="Batch predict crops",
    description="Get recommendations for multiple crop requests"
)
async def batch_predict_crops(request: CropBatchPredictionRequest) -> CropBatchPredictionResponse:
    """
    Predict crops for multiple requests in batch
    
    Accepts up to 100 prediction requests at once.
    Returns a list of predictions with confidence scores.
    """
    try:
        results = []
        
        for crop_request in request.predictions:
            features = [
                crop_request.nitrogen,
                crop_request.phosphorus,
                crop_request.potassium,
                crop_request.temperature,
                crop_request.humidity,
                crop_request.ph,
                crop_request.rainfall
            ]
            
            result = model_manager.predict_crop(features)
            results.append(CropPredictionResponse(**result))
        
        logger.info(f"Batch crop predictions completed: {len(results)} crops")
        
        return CropBatchPredictionResponse(
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
    "/supported-crops",
    summary="Get supported crops",
    description="List all crops that the model can predict"
)
async def get_supported_crops() -> dict:
    """
    Get list of all supported crops
    
    Returns the crop categories the model can recommend
    """
    try:
        crops = list(model_manager.crop_encoder.classes_)
        return {
            "crops": crops,
            "total": len(crops)
        }
    except Exception as e:
        logger.error(f"Error fetching supported crops: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch supported crops"
        )
