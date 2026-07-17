"""
Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum


class ActionTypeSchema(str, Enum):
    """Supported action types."""
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    SCREENSHOT = "screenshot"
    GET_CONTENT = "get_content"
    EXECUTE_JS = "execute_js"
    WAIT_FOR_ELEMENT = "wait_for_element"


class SessionCreateRequest(BaseModel):
    """Request to create a new session."""
    description: Optional[str] = None


class SessionResponse(BaseModel):
    """Response with session information."""
    session_id: str
    created_at: str
    is_active: bool
    current_url: Optional[str] = None


class ActionExecuteRequest(BaseModel):
    """Request to execute an action."""
    action_type: ActionTypeSchema
    parameters: Dict[str, Any] = Field(default_factory=dict)
    description: Optional[str] = None


class ActionResponse(BaseModel):
    """Response with action execution result."""
    action_id: str
    session_id: str
    action_type: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None


class TaskCreateRequest(BaseModel):
    """Request to create a new task."""
    objective: str = Field(..., description="Main goal of the task")
    description: Optional[str] = None


class TaskResponse(BaseModel):
    """Response with task information."""
    task_id: str
    session_id: str
    objective: str
    description: Optional[str] = None
    status: str
    created_at: str
    completed_at: Optional[str] = None
    actions: List[ActionResponse] = []
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
    request_id: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    app_name: str
    app_version: str
    timestamp: str


class NavigateRequest(BaseModel):
    """Request for navigate action."""
    url: str = Field(..., description="URL to navigate to")


class ClickRequest(BaseModel):
    """Request for click action."""
    selector: str = Field(..., description="CSS selector of element to click")


class TypeRequest(BaseModel):
    """Request for type action."""
    selector: str = Field(..., description="CSS selector of input element")
    text: str = Field(..., description="Text to type")
    delay: int = Field(default=50, description="Delay between keystrokes in milliseconds")


class ScrollRequest(BaseModel):
    """Request for scroll action."""
    direction: str = Field(default="down", description="Scroll direction: up or down")
    amount: int = Field(default=3, description="Number of scroll increments")


class ExecuteJSRequest(BaseModel):
    """Request for JavaScript execution."""
    script: str = Field(..., description="JavaScript code to execute")


class WaitForElementRequest(BaseModel):
    """Request to wait for element."""
    selector: str = Field(..., description="CSS selector to wait for")
    timeout: int = Field(default=5000, description="Timeout in milliseconds")


class PageInfoResponse(BaseModel):
    """Response with page information."""
    url: str
    title: Optional[str] = None
    content_length: int
    screenshot: Optional[str] = None
