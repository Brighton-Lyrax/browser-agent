"""
Health and status check endpoints.
"""

from fastapi import APIRouter, status
from app.schemas.requests import HealthResponse
from app.config import settings
from app.services.session import session_manager
from datetime import datetime

router = APIRouter(prefix="/health", tags=["health"])


@router.get(
    "",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check application health and status"
)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        app_version=settings.app_version,
        timestamp=datetime.utcnow().isoformat()
    )


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
    description="Check if the application is ready to accept requests"
)
async def readiness_check():
    """Readiness check endpoint."""
    return {
        "ready": True,
        "sessions_active": session_manager.get_session_count(),
        "timestamp": datetime.utcnow().isoformat()
    }
