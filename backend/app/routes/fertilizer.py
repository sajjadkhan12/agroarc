"""
Fertilizer Recommendation API Routes
Endpoints for fertilizer prediction based on soil nutrients and conditions
"""

from fastapi import APIRouter, HTTPException, status
import logging
import numpy as np

# Import schemas from core
from ..core.schemas import FertilizerRequest, FertilizerResponse

# Import model loader
from ..core.model_loader import load_fertilizer_assets

# Configure logging
logger = logging.getLogger(__name__)

# Create router with prefix and tags
router = APIRouter(
    prefix="/api/v1/fertilizer",
    tags=["Fertilizer Recommendation"]
)

# Load fertilizer model and encoders once at startup (module-level import)
# This ensures models are loaded only once when the application starts
try:
    fert_model, soil_encoder, crop_encoder, fertilizer_encoder = load_fertilizer_assets()
    logger.info("✓ Fertilizer assets loaded successfully at startup")
except Exception as e:
    logger.error(f"❌ Failed to load fertilizer assets: {str(e)}")
    fert_model = None
    soil_encoder = None
    crop_encoder = None
    fertilizer_encoder = None


@router.post(
    "/recommend-fertilizer",
    response_model=FertilizerResponse,
    summary="Recommend fertilizer",
    description="Get fertilizer recommendation based on soil nutrients and conditions"
)
async def recommend_fertilizer(request: FertilizerRequest) -> FertilizerResponse:
    """
    Predict the best fertilizer based on soil and environmental conditions
    
    Endpoint: POST /api/v1/fertilizer/recommend-fertilizer
    
    Input (FertilizerRequest):
    - Temperature: Air temperature in Celsius
    - Humidity: Relative humidity percentage (0-100)
    - Moisture: Soil moisture percentage (0-100)
    - Soil_Type: Type of soil (Sandy, Loamy, Clayey)
    - Crop_Type: Type of crop (Rice, Maize, Sugarcane, Cotton, Wheat)
    - Nitrogen: Soil nitrogen level (mg/kg)
    - Phosphorous: Soil phosphorus level (mg/kg)
    - Potassium: Soil potassium level (mg/kg)
    
    Output (FertilizerResponse):
    - recommended_fertilizer: Predicted fertilizer name
    - confidence: Prediction confidence percentage (0-100)
    
    Process:
    1. Validate input using FertilizerRequest schema
    2. Encode categorical variables (Soil_Type, Crop_Type)
    3. Build feature vector in exact training order
    4. Predict using pre-trained RandomForest model
    5. Get prediction probability for confidence score
    6. Decode predicted class to fertilizer name using LabelEncoder
    7. Return response with fertilizer name and confidence
    """
    
    # Check if models are loaded
    if fert_model is None or soil_encoder is None or crop_encoder is None or fertilizer_encoder is None:
        logger.error("Fertilizer model or encoders not loaded")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Fertilizer prediction model not available. Service initialization failed."
        )
    
    try:
        # Step 1: Get valid categories from encoders
        # These are the categories the model was trained on
        valid_soil_types = list(soil_encoder.classes_)
        valid_crop_types = list(crop_encoder.classes_)
        
        # Step 2: Validate Soil_Type against known categories
        # If the input soil type is not in training data, return helpful error
        if request.Soil_Type not in valid_soil_types:
            logger.warning(f"Unknown Soil_Type: {request.Soil_Type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown Soil_Type: '{request.Soil_Type}'. "
                       f"Supported types: {', '.join(valid_soil_types)}"
            )
        
        # Step 3: Validate Crop_Type against known categories
        # If the input crop type is not in training data, return helpful error
        if request.Crop_Type not in valid_crop_types:
            logger.warning(f"Unknown Crop_Type: {request.Crop_Type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown Crop_Type: '{request.Crop_Type}'. "
                       f"Supported types: {', '.join(valid_crop_types)}"
            )
        
        # Step 4: Encode categorical variables to integers
        # The model expects encoded integers, not string categories
        soil_type_encoded = int(soil_encoder.transform([request.Soil_Type])[0])
        crop_type_encoded = int(crop_encoder.transform([request.Crop_Type])[0])
        
        logger.debug(f"Encoded Soil_Type '{request.Soil_Type}' -> {soil_type_encoded}")
        logger.debug(f"Encoded Crop_Type '{request.Crop_Type}' -> {crop_type_encoded}")
        
        # Step 5: Create feature dictionary with exact column names
        # CRITICAL: Column names MUST match training data EXACTLY, including misspellings and spaces
        # Training CSV order: Temparature, Humidity , Moisture, Soil Type, Crop Type, Nitrogen, Potassium, Phosphorous
        features_dict = {
            'Temparature': request.Temperature,  # Note: misspelled 'Temparature' as in training data
            'Humidity ': request.Humidity,  # Note: trailing space after 'Humidity' as in training data
            'Moisture': request.Moisture,
            'Soil Type': soil_type_encoded,  # Space in column name (matches training data)
            'Crop Type': crop_type_encoded,  # Space in column name (matches training data)
            'Nitrogen': request.Nitrogen,
            'Potassium': request.Potassium,  # Note: capital 'K' - not 'potassium'
            'Phosphorous': request.Phosphorous  # Note: capital 'P' - not 'phosphorous'
        }
        
        # Step 6: Feature vector in the same column order the model was trained with
        input_data = {
            "Temparature": request.Temperature,
            "Humidity ": request.Humidity,
            "Moisture": request.Moisture,
            "Soil Type": soil_type_encoded,
            "Crop Type": crop_type_encoded,
        }
        feature_names = list(fert_model.feature_names_in_)
        model_input = np.array(
            [[input_data[name] for name in feature_names]], dtype=np.float64
        )

        logger.debug(f"Model features: {feature_names}")
        logger.debug(f"Model input: {model_input}")

        # Step 7: Make prediction using the pre-trained model
        prediction_encoded = fert_model.predict(model_input)[0]

        # Step 8: Get prediction probabilities for confidence score
        prediction_proba = fert_model.predict_proba(model_input)[0]
        
        # Get the highest probability (confidence) and convert to percentage
        confidence = float(max(prediction_proba)) * 100
        
        # Step 9: Decode the predicted class integer back to fertilizer name
        # inverse_transform converts encoded integer to original fertilizer name
        recommended_fertilizer = fertilizer_encoder.inverse_transform([prediction_encoded])[0]
        
        # Step 10: Log the prediction
        logger.info(f"Prediction: {recommended_fertilizer} (confidence: {confidence:.2f}%)")
        
        # Step 11: Return response with fertilizer name and confidence
        return FertilizerResponse(
            recommended_fertilizer=recommended_fertilizer,
            confidence=round(confidence, 2)
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
    
    except ValueError as ve:
        # Handle validation errors from the model or encoders
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
            detail=f"Fertilizer prediction failed: {str(e)}"
        )


@router.get(
    "/supported-fertilizers",
    summary="Get supported fertilizers",
    description="List all fertilizers that the model can recommend"
)
async def get_supported_fertilizers() -> dict:
    """
    Get list of all supported fertilizer types
    
    Endpoint: GET /api/v1/fertilizer/supported-fertilizers
    
    Returns:
    - fertilizers: List of all fertilizer names the model can predict
    - total: Total number of supported fertilizers
    
    This helps users understand which fertilizers are available
    for prediction in the system
    """
    
    # Check if encoder is loaded
    if fertilizer_encoder is None:
        logger.error("Fertilizer encoder not loaded")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Fertilizer encoder not available"
        )
    
    try:
        # Get all fertilizer classes from the label encoder
        # encoder.classes_ returns the unique classes it was trained on
        fertilizers = list(fertilizer_encoder.classes_)
        
        logger.info(f"Retrieved {len(fertilizers)} supported fertilizers")
        
        return {
            "fertilizers": fertilizers,
            "total": len(fertilizers)
        }
    
    except Exception as e:
        logger.error(f"Failed to fetch supported fertilizers: {str(e)}")
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
    """
    Get list of all supported soil types
    
    Endpoint: GET /api/v1/fertilizer/supported-soil-types
    
    Returns:
    - soil_types: List of valid soil type names
    - total: Total number of supported soil types
    """
    
    # Check if encoder is loaded
    if soil_encoder is None:
        logger.error("Soil encoder not loaded")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Soil encoder not available"
        )
    
    try:
        # Get all soil type classes from the label encoder
        soil_types = list(soil_encoder.classes_)
        
        logger.info(f"Retrieved {len(soil_types)} supported soil types")
        
        return {
            "soil_types": soil_types,
            "total": len(soil_types)
        }
    
    except Exception as e:
        logger.error(f"Failed to fetch supported soil types: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch supported soil types"
        )


@router.get(
    "/supported-crop-types",
    summary="Get supported crop types",
    description="List all crop types accepted by the fertilizer model"
)
async def get_supported_crop_types() -> dict:
    """
    Get list of all supported crop types for fertilizer model
    
    Endpoint: GET /api/v1/fertilizer/supported-crop-types
    
    Returns:
    - crop_types: List of valid crop type names
    - total: Total number of supported crop types
    """
    
    # Check if encoder is loaded
    if crop_encoder is None:
        logger.error("Crop encoder not loaded")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Crop encoder not available"
        )
    
    try:
        # Get all crop type classes from the label encoder
        crop_types = list(crop_encoder.classes_)
        
        logger.info(f"Retrieved {len(crop_types)} supported crop types")
        
        return {
            "crop_types": crop_types,
            "total": len(crop_types)
        }
    
    except Exception as e:
        logger.error(f"Failed to fetch supported crop types: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch supported crop types"
        )


@router.get(
    "/categories",
    summary="Get all input categories",
    description="Get all valid Soil Types and Crop Types for frontend dropdowns"
)
async def get_categories() -> dict:
    """
    Get all valid categories for fertilizer recommendation inputs
    
    Endpoint: GET /api/v1/fertilizer/categories
    
    Returns:
    - soil_types: List of all valid soil type options
    - crop_types: List of all valid crop type options
    
    This endpoint is designed for frontend applications to populate
    dropdown menus and prevent unknown-category validation errors.
    The categories returned are exactly what the model expects.
    """
    
    # Check if encoders are loaded
    if soil_encoder is None or crop_encoder is None:
        logger.error("Encoders not loaded")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Category encoders not available"
        )
    
    try:
        # Get all categories from the label encoders
        # .classes_ returns numpy array, convert to list for JSON serialization
        soil_types = soil_encoder.classes_.tolist()
        crop_types = crop_encoder.classes_.tolist()
        
        logger.info(f"Retrieved categories - Soil Types: {len(soil_types)}, Crop Types: {len(crop_types)}")
        
        return {
            "soil_types": soil_types,
            "crop_types": crop_types
        }
    
    except Exception as e:
        logger.error(f"Failed to fetch categories: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch input categories"
        )


# Health check endpoint for fertilizer service
@router.get(
    "/health",
    summary="Health check",
    description="Check if fertilizer prediction service is operational"
)
async def fertilizer_health() -> dict:
    """
    Health check for fertilizer prediction service
    
    Endpoint: GET /api/v1/fertilizer/health
    
    Returns:
    - status: 'healthy' if models are loaded, 'unhealthy' otherwise
    - models_loaded: Boolean indicating if all models and encoders are ready
    """
    
    # Check if all models and encoders are loaded
    models_loaded = all([
        fert_model is not None,
        soil_encoder is not None,
        crop_encoder is not None,
        fertilizer_encoder is not None
    ])
    
    status_msg = "healthy" if models_loaded else "unhealthy"
    
    return {
        "status": status_msg,
        "models_loaded": models_loaded,
        "service": "fertilizer_recommendation"
    }
