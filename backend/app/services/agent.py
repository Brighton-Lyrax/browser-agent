"""
Main agent service orchestrating browser automation and task execution.
"""

from typing import Dict, Any, Optional
from app.core.browser import BrowserAgent, browser_pool
from app.core.logging import get_logger
from app.core.exceptions import AgentException, ValidationException
from app.models.domain import ActionType, Task, Action
from app.services.session import session_manager
from app.services.task import task_manager
import asyncio

logger = get_logger(__name__)


class AgentService:
    """Main service orchestrating agent operations."""

    def __init__(self):
        self.browser_agent = BrowserAgent(browser_pool)

    async def initialize(self):
        """Initialize the agent service."""
        await browser_pool.initialize()
        logger.info("agent_service_initialized")

    async def create_session(self) -> str:
        """Create a new browser session."""
        try:
            session = await session_manager.create_session()
            await browser_pool.create_page(session.session_id)
            logger.info("agent_session_created", session_id=session.session_id)
            return session.session_id
        except Exception as e:
            logger.error("session_creation_failed", error=str(e))
            raise AgentException(f"Failed to create session: {e}")

    async def execute_action(
        self,
        session_id: str,
        action_type: ActionType,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single action."""
        try:
            session = await session_manager.get_session(session_id)
            if not session:
                raise ValidationException(f"Session {session_id} not found")
            
            logger.info(
                "action_execution_started",
                session_id=session_id,
                action_type=action_type
            )

            if action_type == ActionType.NAVIGATE:
                result = await self.browser_agent.navigate(
                    session_id,
                    parameters.get("url")
                )
                await session_manager.update_session_url(
                    session_id,
                    parameters.get("url")
                )

            elif action_type == ActionType.CLICK:
                result = await self.browser_agent.click(
                    session_id,
                    parameters.get("selector")
                )

            elif action_type == ActionType.TYPE:
                result = await self.browser_agent.type_text(
                    session_id,
                    parameters.get("selector"),
                    parameters.get("text"),
                    parameters.get("delay", 50)
                )

            elif action_type == ActionType.SCROLL:
                result = await self.browser_agent.scroll(
                    session_id,
                    parameters.get("direction", "down"),
                    parameters.get("amount", 3)
                )

            elif action_type == ActionType.SCREENSHOT:
                result = await self.browser_agent.take_screenshot(session_id)

            elif action_type == ActionType.GET_CONTENT:
                result = await self.browser_agent.get_page_content(session_id)

            elif action_type == ActionType.EXECUTE_JS:
                result = await self.browser_agent.execute_javascript(
                    session_id,
                    parameters.get("script")
                )

            elif action_type == ActionType.WAIT_FOR_ELEMENT:
                result = await self.browser_agent.wait_for_element(
                    session_id,
                    parameters.get("selector"),
                    parameters.get("timeout", 5000)
                )

            else:
                raise ValidationException(f"Unknown action type: {action_type}")

            logger.info(
                "action_execution_completed",
                session_id=session_id,
                action_type=action_type
            )
            return result

        except Exception as e:
            logger.error(
                "action_execution_failed",
                session_id=session_id,
                action_type=action_type,
                error=str(e)
            )
            raise

    async def close_session(self, session_id: str):
        """Close a session and cleanup resources."""
        try:
            await browser_pool.close_page(session_id)
            await session_manager.close_session(session_id)
            logger.info("agent_session_closed", session_id=session_id)
        except Exception as e:
            logger.error("session_close_failed", session_id=session_id, error=str(e))

    async def execute_task(
        self,
        session_id: str,
        objective: str,
        description: Optional[str] = None
    ) -> Task:
        """Execute a high-level task by creating a task and executing actions."""
        try:
            session = await session_manager.get_session(session_id)
            if not session:
                raise ValidationException(f"Session {session_id} not found")

            task = await task_manager.create_task(session_id, objective, description)
            
            logger.info(
                "task_execution_started",
                task_id=task.task_id,
                session_id=session_id
            )

            # In a real scenario, an LLM would parse the objective and generate actions
            # For now, this is a placeholder showing the architecture
            
            return task

        except Exception as e:
            logger.error(
                "task_execution_failed",
                session_id=session_id,
                objective=objective,
                error=str(e)
            )
            raise

    async def cleanup(self):
        """Cleanup resources."""
        try:
            await browser_pool.close_all()
            logger.info("agent_service_cleanup_completed")
        except Exception as e:
            logger.error("agent_service_cleanup_failed", error=str(e))


# Global agent service instance
agent_service = AgentService()
