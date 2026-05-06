# AgroArc Frontend-Backend Integration Guide

## Overview
This guide explains how the React frontend integrates with the FastAPI backend.

## Architecture

```
Frontend (React + Vite)     Backend (FastAPI)
Port: 3000                  Port: 8000
├── services/api.ts    →    ├── /api/v1/crop/predict-crop
├── components/        →    ├── /api/v1/fertilizer/recommend-fertilizer
└── App.tsx           →    ├── /api/v1/fertilizer/categories
                           └── /api/v1/weather/weather-advice
```

## Configuration

### Backend (.env)
Located at: `backend/.env`
```env
OPENWEATHER_API_KEY=your_openweather_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
DEBUG=True
DATABASE_URL=sqlite:///./agroarc.db
```

### Frontend (.env.local)
Located at: `frontend/.env.local`
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## API Endpoints Mapping

| Frontend Service Method | Backend Endpoint | Method | Description |
|------------------------|------------------|--------|-------------|
| `checkStatus()` | `/` | GET | Health check |
| `predictCrop()` | `/api/v1/crop/predict-crop` | POST | Crop recommendation |
| `getFertilizerCategories()` | `/api/v1/fertilizer/categories` | GET | Get soil/crop types |
| `recommendFertilizer()` | `/api/v1/fertilizer/recommend-fertilizer` | POST | Fertilizer recommendation |
| `getWeatherAdvisory()` | `/api/v1/weather/weather-advice` | GET | Weather advisory |

## Running the Application

### Step 1: Start Backend Server
```powershell
# Terminal 1
cd "c:\Users\Danyal\Downloads\Personal\UOS - CS\FYP - I\agroarc"
.\.venv\Scripts\Activate.ps1
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend will run on: **http://127.0.0.1:8000**

### Step 2: Start Frontend Development Server
```powershell
# Terminal 2 (NEW TERMINAL)
cd "c:\Users\Danyal\Downloads\Personal\UOS - CS\FYP - I\agroarc\frontend"
npm run dev
```

Frontend will run on: **http://localhost:3000**

### Step 3: Open Browser
Navigate to: **http://localhost:3000**

## CORS Configuration

### Development Mode
Frontend uses Vite proxy (configured in `vite.config.ts`):
- All `/api/*` requests are proxied to `http://127.0.0.1:8000`
- No CORS issues during development

### Production Mode
Backend has CORS enabled for all origins (in `backend/app/main.py`):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Request/Response Examples

### Crop Prediction
**Frontend:**
```typescript
const response = await apiService.predictCrop({
  N: 90,
  P: 42,
  K: 43,
  temperature: 20.8,
  humidity: 82,
  ph: 6.5,
  rainfall: 202.9
});
```

**Backend Response:**
```json
{
  "recommended_crop": "rice",
  "confidence": 99.32
}
```

### Fertilizer Recommendation
**Frontend:**
```typescript
const response = await apiService.recommendFertilizer({
  Temperature: 26,
  Humidity: 52,
  Moisture: 38,
  Soil_Type: "Loamy",
  Crop_Type: "Maize",
  Nitrogen: 37,
  Potassium: 0,
  Phosphorous: 0
});
```

**Backend Response:**
```json
{
  "recommended_fertilizer": "Urea",
  "confidence": 35.0
}
```

### Weather Advisory
**Frontend:**
```typescript
const response = await apiService.getWeatherAdvisory("Lahore");
```

**Backend Response:**
```json
{
  "city": "Lahore",
  "country": "PK",
  "temperature": 18.5,
  "humidity": 65.0,
  "wind_speed": 2.5,
  "rainfall": 0.0,
  "weather_description": "clear sky",
  "advisory": "✅ Optimal temperature (18.5°C) for most crops..."
}
```

## Troubleshooting

### Issue: "Network Error" or "Failed to fetch"
**Solution:**
1. Verify backend is running: `curl http://127.0.0.1:8000/`
2. Check frontend .env.local has correct `VITE_API_BASE_URL`
3. Restart both servers

### Issue: CORS Error
**Solution:**
1. Verify vite.config.ts has proxy configured
2. Check backend CORS middleware is enabled
3. Clear browser cache and restart

### Issue: "Cannot GET /api/v1/..."
**Solution:**
1. Check endpoint exists in backend: http://127.0.0.1:8000/docs
2. Verify URL in frontend matches backend route exactly
3. Check for typos in API paths

### Issue: Wrong predictions
**Solution:**
1. Verify request payload matches backend schema
2. Check field names are exact (case-sensitive):
   - `Soil_Type` not `soil_type`
   - `Crop_Type` not `crop_type`
3. Use `/fertilizer/categories` to get valid values

## Testing Integration

### Quick Test Commands
```powershell
# Test backend health
curl http://127.0.0.1:8000/

# Test crop prediction
curl -X POST http://127.0.0.1:8000/api/v1/crop/predict-crop -H "Content-Type: application/json" -d "{\"N\":90,\"P\":42,\"K\":43,\"temperature\":20.8,\"humidity\":82,\"ph\":6.5,\"rainfall\":202.9}"

# Test fertilizer categories
curl http://127.0.0.1:8000/api/v1/fertilizer/categories

# Test weather
curl "http://127.0.0.1:8000/api/v1/weather/weather-advice?city=Lahore"
```

## Production Deployment

### Backend
```bash
# Update CORS origins in main.py
allow_origins=["https://your-frontend-domain.com"]

# Use production server
gunicorn backend.app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend
```bash
# Build for production
npm run build

# Serve with static server
npm run preview
```

### Environment Variables
Update `.env.local` with production backend URL:
```env
VITE_API_BASE_URL=https://api.your-domain.com
```

## Security Checklist
- ✅ `.env` files in `.gitignore`
- ✅ No API keys in frontend code
- ✅ CORS configured properly
- ✅ HTTPS in production
- ✅ Environment variables for sensitive data

## Additional Resources
- Backend API Docs: http://127.0.0.1:8000/docs
- Vite Proxy: https://vitejs.dev/config/server-options.html#server-proxy
- FastAPI CORS: https://fastapi.tiangolo.com/tutorial/cors/
