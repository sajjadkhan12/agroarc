
export interface CropPredictionRequest {
  N: number;
  P: number;
  K: number;
  temperature: number;
  humidity: number;
  ph: number;
  rainfall: number;
}

export interface CropPredictionResponse {
  recommended_crop: string;
}

export interface FertilizerCategoriesResponse {
  soil_types: string[];
  crop_types: string[];
}

export interface FertilizerRecommendationRequest {
  Temperature: number;
  Humidity: number;
  Moisture: number;
  Soil_Type: string;
  Crop_Type: string;
  Nitrogen: number;
  Potassium: number;
  Phosphorous: number;
}

export interface FertilizerRecommendationResponse {
  recommended_fertilizer: string;
}

export interface WeatherAdvisoryResponse {
  city: string;
  temperature: number;
  humidity: number;
  wind_speed: number;
  rainfall: number;
  advisory: string;
}

export interface ApiResponseData {
  status: number;
  data: any;
  requestPayload: any;
  error?: string;
  timestamp: string;
}

export interface ChatMessage {
  role: 'user' | 'system';
  content: string;
  timestamp: Date;
}
