"""
Session management service.
"""

from typing import Dict, Optional
from app.models.domain import Session
from app.core.logging import get_logger
from datetime import datetime
import uuid

logger = get_logger(__name__)


class SessionManager:
    """Manages browser sessions."""

    def __init__(self):
        self._sessions: Dict[str, Session] = {}

    async def create_session(self) -> Session:
        """Create a new browser session."""
        session_id = str(uuid.uuid4())
        session = Session(session_id)
        self._sessions[session_id] = session
        
        logger.info("session_created", session_id=session_id)
        return session

    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID."""
        return self._sessions.get(session_id)

    async def close_session(self, session_id: str) -> bool:
        """Close a session."""
        if session_id in self._sessions:
            session = self._sessions.pop(session_id)
            session.is_active = False
            logger.info("session_closed", session_id=session_id)
            return True
        return False

    async def list_sessions(self) -> list:
        """List all active sessions."""
        return list(self._sessions.values())

    async def update_session_url(self, session_id: str, url: str):
        """Update the current URL of a session."""
        session = self._sessions.get(session_id)
        if session:
            session.current_url = url
            session.last_action_at = datetime.utcnow()

    def get_session_count(self) -> int:
        """Get the number of active sessions."""
        return len(self._sessions)


# Global session manager instance
session_manager = SessionManager()
