"""
Agent actions API endpoints.
"""

from fastapi import APIRouter, HTTPException, status
from app.schemas.requests import ActionExecuteRequest, ActionResponse
from app.services.session import session_manager
from app.services.agent import agent_service
from app.core.logging import get_logger
from app.models.domain import ActionType
from datetime import datetime
import uuid

logger = get_logger(__name__)
router = APIRouter(prefix="/sessions/{session_id}/actions", tags=["actions"])


@router.post(
    "",
    response_model=ActionResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute action",
    description="Execute a browser automation action"
)
async def execute_action(session_id: str, request: ActionExecuteRequest):
    """Execute an action on a session."""
    try:
        # Verify session exists
        session = await session_manager.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )

        # Execute the action
        result = await agent_service.execute_action(
            session_id,
            ActionType(request.action_type),
            request.parameters
        )

        action_id = str(uuid.uuid4())
        
        return ActionResponse(
            action_id=action_id,
            session_id=session_id,
            action_type=request.action_type,
            status="success",
            result=result,
            created_at=datetime.utcnow().isoformat(),
            completed_at=datetime.utcnow().isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "action_execution_error",
            session_id=session_id,
            action_type=request.action_type,
            error=str(e)
        )
        action_id = str(uuid.uuid4())
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "action_id": action_id,
                "session_id": session_id,
                "action_type": request.action_type,
                "status": "failed",
                "error": str(e),
                "created_at": datetime.utcnow().isoformat()
            }
        )


# Additional endpoint schemas for specific actions
@router.post(
    "/navigate",
    response_model=ActionResponse,
    summary="Navigate to URL",
    description="Navigate the browser to a specific URL"
)
async def navigate(session_id: str, url: str):
    """Navigate to a URL."""
    try:
        session = await session_manager.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )

        result = await agent_service.execute_action(
            session_id,
            ActionType.NAVIGATE,
            {"url": url}
        )

        return ActionResponse(
            action_id=str(uuid.uuid4()),
            session_id=session_id,
            action_type="navigate",
            status="success",
            result=result,
            created_at=datetime.utcnow().isoformat(),
            completed_at=datetime.utcnow().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("navigate_error", session_id=session_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/screenshot",
    response_model=ActionResponse,
    summary="Take screenshot",
    description="Take a screenshot of the current page"
)
async def take_screenshot(session_id: str):
    """Take a screenshot."""
    try:
        session = await session_manager.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )

        result = await agent_service.execute_action(
            session_id,
            ActionType.SCREENSHOT,
            {}
        )

        return ActionResponse(
            action_id=str(uuid.uuid4()),
            session_id=session_id,
            action_type="screenshot",
            status="success",
            result=result,
            created_at=datetime.utcnow().isoformat(),
            completed_at=datetime.utcnow().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("screenshot_error", session_id=session_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
