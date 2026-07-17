"""
Custom exception classes for the application.
"""


class AgentException(Exception):
    """Base exception for agent-related errors."""
    pass


class BrowserException(AgentException):
    """Raised when browser automation fails."""
    pass


class NavigationException(BrowserException):
    """Raised when page navigation fails."""
    pass


class InteractionException(BrowserException):
    """Raised when element interaction fails."""
    pass


class TimeoutException(BrowserException):
    """Raised when operation times out."""
    pass


class ValidationException(AgentException):
    """Raised when input validation fails."""
    pass


class ConfigurationException(AgentException):
    """Raised when configuration is invalid."""
    pass


class SecurityException(AgentException):
    """Raised when security policy is violated."""
    pass
