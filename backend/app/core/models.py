"""
ML Model Loader - Singleton pattern
Load models once at startup, reuse for all predictions
"""

import pickle
from pathlib import Path
from typing import Optional
import logging
from ..config import get_settings
from .exceptions import ModelLoadError

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Singleton class to manage ML models loading and caching
    Loads models once at startup, reuses for all requests
    """
    
    _instance: Optional["ModelManager"] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.settings = get_settings()
        self.models_dir = self.settings.MODELS_DIR
        
        # Initialize model variables
        self.crop_model = None
        self.crop_encoder = None
        self.fertilizer_model = None
        self.soil_encoder = None
        self.crop_encoder_fert = None
        self.fertilizer_encoder = None
        
        self._load_models()
        self._initialized = True
    
    def _load_model(self, model_path: Path) -> any:
        """Load a single model from pickle file"""
        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            logger.info(f"✓ Loaded model: {model_path.name}")
            return model
        except FileNotFoundError:
            raise ModelLoadError(f"Model file not found: {model_path}")
        except Exception as e:
            raise ModelLoadError(f"Error loading {model_path.name}: {str(e)}")
    
    def _load_models(self):
        """Load all models and encoders at startup"""
        try:
            # Load crop model
            self.crop_model = self._load_model(
                self.models_dir / "crop_recommendation_model.pkl"
            )
            self.crop_encoder = self._load_model(
                self.models_dir / "crop_label_encoder.pkl"
            )
            
            # Load fertilizer model
            self.fertilizer_model = self._load_model(
                self.models_dir / "fertilizer_recommendation_model.pkl"
            )
            
            # Load encoders dict or individual encoders
            encoders_path = self.models_dir / "fertilizer_encoders.pkl"
            if encoders_path.exists():
                with open(encoders_path, 'rb') as f:
                    encoders_dict = pickle.load(f)
                
                if isinstance(encoders_dict, dict):
                    self.soil_encoder = encoders_dict.get('soil_encoder')
                    self.crop_encoder_fert = encoders_dict.get('crop_encoder')
                    self.fertilizer_encoder = encoders_dict.get('fertilizer_encoder')
                else:
                    # Handle legacy format
                    self.soil_encoder = encoders_dict
                logger.info("✓ Loaded fertilizer encoders")
            
            logger.info("✓ All models loaded successfully!")
            
        except ModelLoadError:
            raise
        except Exception as e:
            raise ModelLoadError(f"Unexpected error loading models: {str(e)}")
    
    def predict_crop(self, features: list) -> dict:
        """
        Predict crop recommendation
        
        Args:
            features: List of feature values [N, P, K, temperature, humidity, ph, rainfall]
        
        Returns:
            dict with prediction and confidence
        """
        try:
            prediction_encoded = self.crop_model.predict([features])[0]
            prediction_proba = self.crop_model.predict_proba([features])[0]
            confidence = max(prediction_proba) * 100
            
            crop_name = self.crop_encoder.inverse_transform([prediction_encoded])[0]
            
            return {
                "crop": crop_name,
                "confidence": round(confidence, 2),
                "encoded_value": int(prediction_encoded)
            }
        except Exception as e:
            raise ModelLoadError(f"Crop prediction failed: {str(e)}")
    
    def predict_fertilizer(self, features: list) -> dict:
        """
        Predict fertilizer recommendation
        
        Args:
            features: List of feature values [Temperature, Humidity, Moisture, 
                     Soil_Type_encoded, Crop_Type_encoded, N, P, K]
        
        Returns:
            dict with prediction and confidence
        """
        try:
            prediction_encoded = self.fertilizer_model.predict([features])[0]
            prediction_proba = self.fertilizer_model.predict_proba([features])[0]
            confidence = max(prediction_proba) * 100
            
            fertilizer_name = self.fertilizer_encoder.inverse_transform([prediction_encoded])[0]
            
            return {
                "fertilizer": fertilizer_name,
                "confidence": round(confidence, 2),
                "encoded_value": int(prediction_encoded)
            }
        except Exception as e:
            raise ModelLoadError(f"Fertilizer prediction failed: {str(e)}")
    
    def encode_categorical(self, encoder_type: str, value: str) -> int:
        """
        Encode categorical value
        
        Args:
            encoder_type: 'soil' or 'crop'
            value: Value to encode
        
        Returns:
            Encoded integer value
        """
        try:
            if encoder_type == "soil":
                return int(self.soil_encoder.transform([value])[0])
            elif encoder_type == "crop":
                return int(self.crop_encoder_fert.transform([value])[0])
            else:
                raise ValueError(f"Unknown encoder type: {encoder_type}")
        except Exception as e:
            raise ModelLoadError(f"Encoding failed: {str(e)}")
    
    def decode_categorical(self, encoder_type: str, encoded_value: int) -> str:
        """
        Decode categorical value
        
        Args:
            encoder_type: 'soil' or 'crop'
            encoded_value: Encoded value
        
        Returns:
            Original string value
        """
        try:
            if encoder_type == "soil":
                return self.soil_encoder.inverse_transform([encoded_value])[0]
            elif encoder_type == "crop":
                return self.crop_encoder_fert.inverse_transform([encoded_value])[0]
            else:
                raise ValueError(f"Unknown encoder type: {encoder_type}")
        except Exception as e:
            raise ModelLoadError(f"Decoding failed: {str(e)}")


# Global instance
model_manager = ModelManager()
