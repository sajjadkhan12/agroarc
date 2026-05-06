"""
Crop Recommendation API Routes
Endpoints for crop prediction based on soil nutrients and environmental conditions
"""

from fastapi import APIRouter, HTTPException, status
import pandas as pd
import logging

# Import schemas from core
from ..core.schemas import CropRequest, CropResponse

# Import model loader
from ..core.model_loader import load_crop_assets

# Configure logging
logger = logging.getLogger(__name__)

# Create router with prefix and tags
router = APIRouter(
    prefix="/api/v1/crop",
    tags=["Crop Recommendation"]
)

# Load crop model, encoder, and scaler once at startup (module-level import)
# This ensures models are loaded only once when the application starts
try:
    crop_model, crop_label_encoder, crop_feature_scaler = load_crop_assets()
    logger.info("✓ Crop assets loaded successfully at startup")
except Exception as e:
    logger.error(f"❌ Failed to load crop assets: {str(e)}")
    crop_model = None
    crop_label_encoder = None
    crop_feature_scaler = None


@router.post(
    "/predict-crop",
    response_model=CropResponse,
    summary="Predict recommended crop",
    description="Get crop recommendation based on soil nutrients and environmental conditions"
)
async def predict_crop(request: CropRequest) -> CropResponse:
    """
    Predict the best crop based on soil and environmental conditions
    
    Endpoint: POST /api/v1/crop/predict-crop
    
    Input (CropRequest):
    - N: Soil nitrogen level (mg/kg)
    - P: Soil phosphorus level (mg/kg)
    - K: Soil potassium level (mg/kg)
    - temperature: Temperature in Celsius
    - humidity: Relative humidity percentage (0-100)
    - ph: Soil pH value (0-14)
    - rainfall: Monthly rainfall in mm
    
    Output (CropResponse):
    - recommended_crop: Predicted crop name
    - confidence: Prediction confidence percentage (0-100)
    
    Process:
    1. Validate input using CropRequest schema
    2. Create pandas DataFrame with exact feature order
    3. Predict using pre-trained RandomForest model
    4. Get prediction probability for confidence score
    5. Decode predicted class to crop name using LabelEncoder
    6. Return response with crop name and confidence
    """
    
    # Check if models are loaded
    if crop_model is None or crop_label_encoder is None:
        logger.error("Crop model or encoder not loaded")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Crop prediction model not available. Service initialization failed."
        )
    
    try:
        # Step 1: Extract features from request in exact order required by model
        # The model was trained with features in this specific order
        features_dict = {
            'N': request.N,
            'P': request.P,
            'K': request.K,
            'temperature': request.temperature,
            'humidity': request.humidity,
            'ph': request.ph,
            'rainfall': request.rainfall
        }
        
        # Step 2: Create pandas DataFrame with exact feature names and order
        # This matches the training data structure
        df = pd.DataFrame([features_dict])

        logger.debug(f"Input features: {features_dict}")
        logger.debug(f"DataFrame columns: {df.columns.tolist()}")

        # Step 2b: Apply the exact StandardScaler that was fit during training.
        # The model was trained on scaled inputs; feeding raw values causes
        # the model to collapse to a single class for every request.
        if crop_feature_scaler is not None:
            model_input = crop_feature_scaler.transform(df)
        else:
            logger.warning("Crop scaler not loaded; predicting on raw features.")
            model_input = df

        # Step 3: Make prediction using the pre-trained model
        # Returns array of predicted class (encoded integer)
        prediction_encoded = crop_model.predict(model_input)[0]

        # Step 4: Get prediction probabilities for confidence score
        # predict_proba returns probabilities for all classes
        prediction_proba = crop_model.predict_proba(model_input)[0]
        
        # Get the highest probability (confidence) and convert to percentage
        confidence = float(max(prediction_proba)) * 100
        
        # Step 5: Decode the predicted class integer back to crop name
        # inverse_transform converts encoded integer to original crop name
        recommended_crop = crop_label_encoder.inverse_transform([prediction_encoded])[0]
        
        # Step 6: Log the prediction
        logger.info(f"Prediction: {recommended_crop} (confidence: {confidence:.2f}%)")
        
        # Step 7: Return response with crop name and confidence
        return CropResponse(
            recommended_crop=recommended_crop,
            confidence=round(confidence, 2)
        )
        
    except ValueError as ve:
        # Handle validation errors from the model
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid input values: {str(ve)}"
        )
    
    except Exception as e:
        # Handle any unexpected errors during prediction
        logger.error(f"❌ Prediction failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Crop prediction failed: {str(e)}"
        )


@router.get(
    "/supported-crops",
    summary="Get supported crops",
    description="List all crops that the model can predict"
)
async def get_supported_crops() -> dict:
    """
    Get list of all supported crop types
    
    Endpoint: GET /api/v1/crop/supported-crops
    
    Returns:
    - crops: List of all crop names the model can predict
    - total: Total number of supported crops
    
    This helps users understand which crops are available
    for prediction in the system
    """
    
    # Check if encoder is loaded
    if crop_label_encoder is None:
        logger.error("Crop encoder not loaded")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Crop encoder not available"
        )
    
    try:
        # Get all crop classes from the label encoder
        # encoder.classes_ returns the unique classes it was trained on
        crops = list(crop_label_encoder.classes_)
        
        logger.info(f"Retrieved {len(crops)} supported crops")
        
        return {
            "crops": crops,
            "total": len(crops)
        }
    
    except Exception as e:
        logger.error(f"Failed to fetch supported crops: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch supported crops"
        )


# Health check endpoint for crop service
@router.get(
    "/health",
    summary="Health check",
    description="Check if crop prediction service is operational"
)
async def crop_health() -> dict:
    """
    Health check for crop prediction service
    
    Endpoint: GET /api/v1/crop/health
    
    Returns:
    - status: 'healthy' if models are loaded, 'unhealthy' otherwise
    - models_loaded: Boolean indicating if crop model and encoder are ready
    """
    
    # Check if model, encoder, and scaler are loaded
    models_loaded = crop_model is not None and crop_label_encoder is not None
    scaler_loaded = crop_feature_scaler is not None

    status_msg = "healthy" if models_loaded else "unhealthy"

    return {
        "status": status_msg,
        "models_loaded": models_loaded,
        "scaler_loaded": scaler_loaded,
        "service": "crop_recommendation"
    }

