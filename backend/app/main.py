"""
AgroArc FastAPI Backend Application
Main entry point for the API server
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Import all route modules
from .routes import crop, fertilizer, weather

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application instance
app = FastAPI(
    title="AgroArc API",
    description="Smart Agriculture Recommendation System - ML-powered crop and fertilizer predictions with weather advisories",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware - Allow all origins for development
# In production, replace ["*"] with specific frontend URLs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (development only)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Include API routers
# Each router handles a specific domain of the application
app.include_router(crop.router)  # Crop recommendation endpoints
app.include_router(fertilizer.router)  # Fertilizer recommendation endpoints
app.include_router(weather.router)  # Weather advisory endpoints


# Exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """Log detailed validation errors for debugging"""
    logger.error(f"Validation error on {request.url.path}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body if hasattr(exc, 'body') else None
        }
    )

# Root health check endpoint
@app.get("/", tags=["Health"])
async def root() -> dict:
    """
    Root endpoint - Health check and API information
    
    Endpoint: GET /
    
    Returns:
    - status: Service status
    - message: Welcome message
    - version: API version
    - documentation: Link to interactive API docs
    - endpoints: Available API endpoint groups
    """
    return {
        "status": "healthy",
        "message": "Welcome to AgroArc API - Smart Agriculture Recommendation System",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "crop_recommendation": "/api/v1/crop",
            "fertilizer_recommendation": "/api/v1/fertilizer",
            "weather_advisory": "/api/v1/weather"
        }
    }
