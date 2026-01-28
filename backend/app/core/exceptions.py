"""
Custom exceptions for AgroArc Backend
"""

from fastapi import HTTPException, status


class AgroArcException(HTTPException):
    """Base exception for AgroArc"""
    pass


class ModelLoadError(AgroArcException):
    """Raised when model fails to load"""
    def __init__(self, detail: str = "Failed to load ML model"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class InvalidInputError(AgroArcException):
    """Raised when input validation fails"""
    def __init__(self, detail: str = "Invalid input data"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class PredictionError(AgroArcException):
    """Raised when prediction fails"""
    def __init__(self, detail: str = "Prediction failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class EncoderError(AgroArcException):
    """Raised when encoding/decoding fails"""
    def __init__(self, detail: str = "Encoding error"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )
