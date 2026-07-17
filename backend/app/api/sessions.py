"""
Session management API endpoints.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.requests import SessionCreateRequest, SessionResponse
from app.services.session import session_manager
from app.services.agent import agent_service
from app.core.logging import get_logger
from datetime import datetime
import uuid

logger = get_logger(__name__)
router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new session",
    description="Create a new browser session for automation"
)
async def create_session(request: SessionCreateRequest):
    """Create a new browser session."""
    try:
        session_id = await agent_service.create_session()
        session = await session_manager.get_session(session_id)
        
        return SessionResponse(
            session_id=session.session_id,
            created_at=session.created_at.isoformat(),
            is_active=session.is_active,
            current_url=session.current_url
        )
    except Exception as e:
        logger.error("session_creation_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {str(e)}"
        )


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
    summary="Get session",
    description="Get information about a specific session"
)
async def get_session(session_id: str):
    """Get a session by ID."""
    try:
        session = await session_manager.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        return SessionResponse(
            session_id=session.session_id,
            created_at=session.created_at.isoformat(),
            is_active=session.is_active,
            current_url=session.current_url
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_session_error", session_id=session_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Close session",
    description="Close a browser session and cleanup resources"
)
async def close_session(session_id: str):
    """Close a session."""
    try:
        await agent_service.close_session(session_id)
    except Exception as e:
        logger.error("close_session_error", session_id=session_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "",
    response_model=List[SessionResponse],
    summary="List sessions",
    description="List all active sessions"
)
async def list_sessions():
    """List all sessions."""
    try:
        sessions = await session_manager.list_sessions()
        return [
            SessionResponse(
                session_id=s.session_id,
                created_at=s.created_at.isoformat(),
                is_active=s.is_active,
                current_url=s.current_url
            )
            for s in sessions
        ]
    except Exception as e:
        logger.error("list_sessions_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
