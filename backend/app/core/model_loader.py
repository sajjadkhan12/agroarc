"""
Model Loader Module
Load pre-trained ML models and encoders from /models folder
Uses joblib for efficient pickle loading with pathlib for path resolution
"""

import joblib
from pathlib import Path
from typing import Tuple
import logging

# Configure logging
logger = logging.getLogger(__name__)


def get_models_dir() -> Path:
    """
    Resolve the /models directory path relative to project root
    
    Path logic explanation:
    - __file__ = backend/app/core/model_loader.py (current file)
    - .parent = backend/app/core/
    - .parent.parent = backend/app/
    - .parent.parent.parent = backend/
    - .parent.parent.parent.parent = project root (agroarc/)
    - models_dir = project_root / "models"
    
    Returns:
        Path: Absolute path to /models directory
    """
    # Get the absolute path of this file
    current_file = Path(__file__).resolve()
    
    # Navigate up 4 directory levels to reach project root
    # backend/app/core/model_loader.py -> agroarc/
    project_root = current_file.parent.parent.parent.parent
    
    # Construct path to models folder at project root
    models_dir = project_root / "models"
    
    logger.debug(f"Models directory resolved to: {models_dir}")
    
    return models_dir


def load_crop_assets() -> Tuple:
    """
    Load crop recommendation model and label encoder from /models
    
    Expected files:
    - models/crop_recommendation_model.pkl (trained RandomForest model)
    - models/crop_label_encoder.pkl (LabelEncoder for crop names)
    
    Returns:
        Tuple[model, encoder]: (crop_model, crop_label_encoder)
    
    Raises:
        FileNotFoundError: If pickle files not found in /models
        Exception: If joblib fails to load files
    """
    models_dir = get_models_dir()
    
    # Define exact paths to crop model files
    crop_model_path = models_dir / "crop_recommendation_model.pkl"
    crop_encoder_path = models_dir / "crop_label_encoder.pkl"
    
    # Validate crop model file exists
    if not crop_model_path.exists():
        raise FileNotFoundError(
            f"\n{'='*70}\n"
            f"❌ CROP MODEL FILE NOT FOUND\n"
            f"{'='*70}\n"
            f"Expected location: {crop_model_path}\n"
            f"File name: crop_recommendation_model.pkl\n"
            f"Models directory: {models_dir}\n"
            f"Verify /models folder exists and contains the .pkl file\n"
            f"{'='*70}"
        )
    
    # Validate crop encoder file exists
    if not crop_encoder_path.exists():
        raise FileNotFoundError(
            f"\n{'='*70}\n"
            f"❌ CROP ENCODER FILE NOT FOUND\n"
            f"{'='*70}\n"
            f"Expected location: {crop_encoder_path}\n"
            f"File name: crop_label_encoder.pkl\n"
            f"Models directory: {models_dir}\n"
            f"Verify /models folder exists and contains the .pkl file\n"
            f"{'='*70}"
        )
    
    try:
        # Load crop model using joblib
        crop_model = joblib.load(crop_model_path)
        logger.info(f"✓ Loaded crop model: {crop_model_path.name}")
        
        # Load crop label encoder using joblib
        crop_label_encoder = joblib.load(crop_encoder_path)
        logger.info(f"✓ Loaded crop encoder: {crop_encoder_path.name}")
        
        return crop_model, crop_label_encoder
        
    except Exception as e:
        raise Exception(
            f"\n{'='*70}\n"
            f"❌ FAILED TO LOAD CROP ASSETS\n"
            f"{'='*70}\n"
            f"Error: {str(e)}\n"
            f"Models directory: {models_dir}\n"
            f"Ensure files are valid pickle files (.pkl)\n"
            f"{'='*70}"
        )


def load_fertilizer_assets() -> Tuple:
    """
    Load fertilizer recommendation model and all encoders from /models
    
    Expected files:
    - models/fertilizer_recommendation_model.pkl (trained RandomForest model)
    - models/fertilizer_encoders.pkl (dict with soil_encoder, crop_encoder, fertilizer_encoder)
    
    The encoders dict structure:
    {
        'soil_encoder': LabelEncoder,      # Encodes soil types
        'crop_encoder': LabelEncoder,      # Encodes crop types
        'fertilizer_encoder': LabelEncoder # Encodes fertilizer types
    }
    
    Returns:
        Tuple[model, encoder, encoder, encoder]: (fert_model, soil_encoder, crop_encoder, fertilizer_encoder)
    
    Raises:
        FileNotFoundError: If pickle files not found in /models
        ValueError: If encoders dict missing required keys
        Exception: If joblib fails to load files
    """
    models_dir = get_models_dir()
    
    # Define exact paths to fertilizer model files
    fert_model_path = models_dir / "fertilizer_recommendation_model.pkl"
    fert_encoders_path = models_dir / "fertilizer_encoders.pkl"
    
    # Validate fertilizer model file exists
    if not fert_model_path.exists():
        raise FileNotFoundError(
            f"\n{'='*70}\n"
            f"❌ FERTILIZER MODEL FILE NOT FOUND\n"
            f"{'='*70}\n"
            f"Expected location: {fert_model_path}\n"
            f"File name: fertilizer_recommendation_model.pkl\n"
            f"Models directory: {models_dir}\n"
            f"Verify /models folder exists and contains the .pkl file\n"
            f"{'='*70}"
        )
    
    # Validate fertilizer encoders file exists
    if not fert_encoders_path.exists():
        raise FileNotFoundError(
            f"\n{'='*70}\n"
            f"❌ FERTILIZER ENCODERS FILE NOT FOUND\n"
            f"{'='*70}\n"
            f"Expected location: {fert_encoders_path}\n"
            f"File name: fertilizer_encoders.pkl\n"
            f"Models directory: {models_dir}\n"
            f"Verify /models folder exists and contains the .pkl file\n"
            f"{'='*70}"
        )
    
    try:
        # Load fertilizer model using joblib
        fert_model = joblib.load(fert_model_path)
        logger.info(f"✓ Loaded fertilizer model: {fert_model_path.name}")
        
        # Load encoders dictionary using joblib
        encoders_dict = joblib.load(fert_encoders_path)
        logger.info(f"✓ Loaded encoders dict: {fert_encoders_path.name}")
        
        # Extract individual encoders from the dictionary
        soil_encoder = encoders_dict.get('soil_encoder')
        crop_encoder = encoders_dict.get('crop_encoder')
        fertilizer_encoder = encoders_dict.get('fertilizer_encoder')
        
        # Validate all required encoders are present
        if not all([soil_encoder, crop_encoder, fertilizer_encoder]):
            missing = []
            if not soil_encoder:
                missing.append('soil_encoder')
            if not crop_encoder:
                missing.append('crop_encoder')
            if not fertilizer_encoder:
                missing.append('fertilizer_encoder')
            
            raise ValueError(
                f"\n{'='*70}\n"
                f"❌ MISSING ENCODERS IN DICT\n"
                f"{'='*70}\n"
                f"Missing encoders: {', '.join(missing)}\n"
                f"Available keys: {list(encoders_dict.keys())}\n"
                f"Expected keys: soil_encoder, crop_encoder, fertilizer_encoder\n"
                f"File: {fert_encoders_path}\n"
                f"{'='*70}"
            )
        
        logger.info("✓ Extracted soil_encoder")
        logger.info("✓ Extracted crop_encoder")
        logger.info("✓ Extracted fertilizer_encoder")
        
        return fert_model, soil_encoder, crop_encoder, fertilizer_encoder
        
    except ValueError as ve:
        raise ValueError(str(ve))
    except Exception as e:
        raise Exception(
            f"\n{'='*70}\n"
            f"❌ FAILED TO LOAD FERTILIZER ASSETS\n"
            f"{'='*70}\n"
            f"Error: {str(e)}\n"
            f"Models directory: {models_dir}\n"
            f"Ensure files are valid pickle files (.pkl)\n"
            f"{'='*70}"
        )
