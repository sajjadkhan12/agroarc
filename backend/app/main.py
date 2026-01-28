"""
AgroArc FastAPI Backend Application
Main entry point for the API server
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from .config import get_settings
from .routes import crop, fertilizer
from .core.exceptions import AgroArcException
from .utils.logger import setup_logging

# Setup logging
logger = setup_logging()

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(AgroArcException)
async def agroarc_exception_handler(request, exc: AgroArcException):
    """Handle AgroArc custom exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("=" * 80)
    logger.info("🚀 AgroArc Backend Starting...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info("=" * 80)
    
    # Verify models are loaded
    try:
        from .core.models import model_manager
        logger.info("✓ All ML models loaded successfully")
    except Exception as e:
        logger.error(f"✗ Failed to load models: {str(e)}")
        raise


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("=" * 80)
    logger.info("🛑 AgroArc Backend Shutting Down...")
    logger.info("=" * 80)


# Include routers
app.include_router(crop.router)
app.include_router(fertilizer.router)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """
    Health check endpoint
    
    Returns status of the API and models
    """
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": settings.API_VERSION
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> dict:
    """Root endpoint with API information"""
    return {
        "name": settings.API_TITLE,
        "description": settings.API_DESCRIPTION,
        "version": settings.API_VERSION,
        "documentation": "/docs",
        "endpoints": {
            "health": "/health",
            "crop_prediction": "/api/v1/crop/predict",
            "fertilizer_prediction": "/api/v1/fertilizer/predict",
        }
    }


# API info endpoint
@app.get("/api/v1", tags=["Info"])
async def api_info() -> dict:
    """Get API information and available endpoints"""
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "description": settings.API_DESCRIPTION,
        "endpoints": {
            "crop_recommendation": {
                "predict": "/api/v1/crop/predict",
                "batch_predict": "/api/v1/crop/batch-predict",
                "supported_crops": "/api/v1/crop/supported-crops"
            },
            "fertilizer_recommendation": {
                "predict": "/api/v1/fertilizer/predict",
                "batch_predict": "/api/v1/fertilizer/batch-predict",
                "supported_fertilizers": "/api/v1/fertilizer/supported-fertilizers",
                "supported_soil_types": "/api/v1/fertilizer/supported-soil-types",
                "supported_crop_types": "/api/v1/fertilizer/supported-crop-types"
            }
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=settings.DEBUG
    )
