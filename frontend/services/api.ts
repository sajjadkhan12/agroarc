
import { 
  CropPredictionRequest, 
  FertilizerRecommendationRequest, 
  ApiResponseData 
} from '../types';

export class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
  }

  private async handleResponse(response: Response, payload: any): Promise<ApiResponseData> {
    const data = await response.json().catch(() => ({}));
    return {
      status: response.status,
      data: data,
      requestPayload: payload,
      timestamp: new Date().toLocaleTimeString(),
      error: response.ok ? undefined : (data.detail || 'An unexpected error occurred')
    };
  }

  async checkStatus(): Promise<ApiResponseData> {
    try {
      const response = await fetch(`${this.baseUrl}/`);
      const text = await response.text();
      return {
        status: response.status,
        data: { message: text },
        requestPayload: null,
        timestamp: new Date().toLocaleTimeString()
      };
    } catch (err: any) {
      return { status: 0, data: null, requestPayload: null, error: err.message, timestamp: new Date().toLocaleTimeString() };
    }
  }

  async predictCrop(payload: CropPredictionRequest): Promise<ApiResponseData> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/crop/predict-crop`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      return this.handleResponse(response, payload);
    } catch (err: any) {
      return { status: 0, data: null, requestPayload: payload, error: err.message, timestamp: new Date().toLocaleTimeString() };
    }
  }

  async getFertilizerCategories(): Promise<ApiResponseData> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/fertilizer/categories`);
      return this.handleResponse(response, null);
    } catch (err: any) {
      return { status: 0, data: null, requestPayload: null, error: err.message, timestamp: new Date().toLocaleTimeString() };
    }
  }

  async recommendFertilizer(payload: FertilizerRecommendationRequest): Promise<ApiResponseData> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/fertilizer/recommend-fertilizer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      return this.handleResponse(response, payload);
    } catch (err: any) {
      return { status: 0, data: null, requestPayload: payload, error: err.message, timestamp: new Date().toLocaleTimeString() };
    }
  }

  async getWeatherAdvisory(city: string): Promise<ApiResponseData> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/weather/weather-advice?city=${encodeURIComponent(city)}`);
      return this.handleResponse(response, { city });
    } catch (err: any) {
      return { status: 0, data: null, requestPayload: { city }, error: err.message, timestamp: new Date().toLocaleTimeString() };
    }
  }
}
