"""
Data models for the application.
"""

from typing import Optional, List
from datetime import datetime
from enum import Enum


class ActionType(str, Enum):
    """Supported action types."""
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    SCREENSHOT = "screenshot"
    GET_CONTENT = "get_content"
    EXECUTE_JS = "execute_js"
    WAIT_FOR_ELEMENT = "wait_for_element"


class ActionStatus(str, Enum):
    """Status of an action execution."""
    PENDING = "pending"
    EXECUTING = "executing"
    SUCCESS = "success"
    FAILED = "failed"


class Session:
    """Browser session model."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.utcnow()
        self.last_action_at = datetime.utcnow()
        self.is_active = True
        self.current_url = None


class Action:
    """Agent action model."""
    
    def __init__(
        self,
        action_id: str,
        session_id: str,
        action_type: ActionType,
        parameters: dict,
        description: Optional[str] = None
    ):
        self.action_id = action_id
        self.session_id = session_id
        self.action_type = action_type
        self.parameters = parameters
        self.description = description
        self.status = ActionStatus.PENDING
        self.created_at = datetime.utcnow()
        self.started_at = None
        self.completed_at = None
        self.result = None
        self.error = None

    def mark_executing(self):
        """Mark action as executing."""
        self.status = ActionStatus.EXECUTING
        self.started_at = datetime.utcnow()

    def mark_success(self, result):
        """Mark action as successful."""
        self.status = ActionStatus.SUCCESS
        self.completed_at = datetime.utcnow()
        self.result = result

    def mark_failed(self, error: str):
        """Mark action as failed."""
        self.status = ActionStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error = error


class Task:
    """Complex task composed of multiple actions."""
    
    def __init__(
        self,
        task_id: str,
        session_id: str,
        objective: str,
        description: Optional[str] = None
    ):
        self.task_id = task_id
        self.session_id = session_id
        self.objective = objective
        self.description = description
        self.created_at = datetime.utcnow()
        self.started_at = None
        self.completed_at = None
        self.actions: List[Action] = []
        self.status = "pending"
        self.result = None
        self.error = None
