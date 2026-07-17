"""
Task management service for complex agent operations.
"""

from typing import Dict, Optional, List
from app.models.domain import Task, Action, ActionType
from app.core.logging import get_logger
from app.core.exceptions import ValidationException
import uuid

logger = get_logger(__name__)


class TaskManager:
    """Manages agent tasks and their actions."""

    def __init__(self):
        self._tasks: Dict[str, Task] = {}

    async def create_task(
        self,
        session_id: str,
        objective: str,
        description: Optional[str] = None
    ) -> Task:
        """Create a new task."""
        task_id = str(uuid.uuid4())
        task = Task(task_id, session_id, objective, description)
        self._tasks[task_id] = task
        
        logger.info(
            "task_created",
            task_id=task_id,
            session_id=session_id,
            objective=objective
        )
        return task

    async def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self._tasks.get(task_id)

    async def add_action_to_task(
        self,
        task_id: str,
        action_type: ActionType,
        parameters: dict,
        description: Optional[str] = None
    ) -> Optional[Action]:
        """Add an action to a task."""
        task = self._tasks.get(task_id)
        if not task:
            raise ValidationException(f"Task {task_id} not found")
        
        action_id = str(uuid.uuid4())
        action = Action(action_id, task.session_id, action_type, parameters, description)
        task.actions.append(action)
        
        logger.info(
            "action_added_to_task",
            task_id=task_id,
            action_id=action_id,
            action_type=action_type
        )
        return action

    async def get_task_actions(self, task_id: str) -> Optional[List[Action]]:
        """Get all actions for a task."""
        task = self._tasks.get(task_id)
        if task:
            return task.actions
        return None

    async def complete_task(self, task_id: str, result: dict):
        """Mark a task as completed."""
        task = self._tasks.get(task_id)
        if task:
            task.status = "completed"
            task.result = result
            logger.info("task_completed", task_id=task_id)

    async def fail_task(self, task_id: str, error: str):
        """Mark a task as failed."""
        task = self._tasks.get(task_id)
        if task:
            task.status = "failed"
            task.error = error
            logger.error("task_failed", task_id=task_id, error=error)

    async def list_tasks(self, session_id: Optional[str] = None) -> List[Task]:
        """List all tasks, optionally filtered by session."""
        if session_id:
            return [t for t in self._tasks.values() if t.session_id == session_id]
        return list(self._tasks.values())


# Global task manager instance
task_manager = TaskManager()
