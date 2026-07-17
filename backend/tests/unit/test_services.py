"""
Unit tests for services.
"""

import pytest
from app.services.session import SessionManager
from app.services.task import TaskManager
from app.models.domain import ActionType


@pytest.mark.asyncio
class TestSessionManager:
    """Tests for SessionManager class."""

    async def test_create_session(self):
        """Test session creation."""
        manager = SessionManager()
        session = await manager.create_session()
        
        assert session is not None
        assert session.session_id is not None
        assert session.is_active is True

    async def test_get_session(self):
        """Test getting a session."""
        manager = SessionManager()
        session = await manager.create_session()
        
        retrieved = await manager.get_session(session.session_id)
        assert retrieved is not None
        assert retrieved.session_id == session.session_id

    async def test_close_session(self):
        """Test closing a session."""
        manager = SessionManager()
        session = await manager.create_session()
        
        result = await manager.close_session(session.session_id)
        assert result is True
        
        retrieved = await manager.get_session(session.session_id)
        assert retrieved is None

    async def test_list_sessions(self):
        """Test listing sessions."""
        manager = SessionManager()
        await manager.create_session()
        await manager.create_session()
        
        sessions = await manager.list_sessions()
        assert len(sessions) == 2

    async def test_update_session_url(self):
        """Test updating session URL."""
        manager = SessionManager()
        session = await manager.create_session()
        
        await manager.update_session_url(session.session_id, "https://example.com")
        
        updated = await manager.get_session(session.session_id)
        assert updated.current_url == "https://example.com"


@pytest.mark.asyncio
class TestTaskManager:
    """Tests for TaskManager class."""

    async def test_create_task(self):
        """Test task creation."""
        manager = TaskManager()
        task = await manager.create_task(
            "session_1",
            "Search for Python tutorials",
            "Find top 5 Python tutorial websites"
        )
        
        assert task is not None
        assert task.task_id is not None
        assert task.session_id == "session_1"

    async def test_get_task(self):
        """Test getting a task."""
        manager = TaskManager()
        task = await manager.create_task("session_1", "Test objective")
        
        retrieved = await manager.get_task(task.task_id)
        assert retrieved is not None
        assert retrieved.task_id == task.task_id

    async def test_add_action_to_task(self):
        """Test adding an action to a task."""
        manager = TaskManager()
        task = await manager.create_task("session_1", "Test objective")
        
        action = await manager.add_action_to_task(
            task.task_id,
            ActionType.NAVIGATE,
            {"url": "https://example.com"},
            "Navigate to example"
        )
        
        assert action is not None
        assert len(task.actions) == 1

    async def test_complete_task(self):
        """Test completing a task."""
        manager = TaskManager()
        task = await manager.create_task("session_1", "Test objective")
        
        await manager.complete_task(task.task_id, {"result": "success"})
        
        updated = await manager.get_task(task.task_id)
        assert updated.status == "completed"
        assert updated.result == {"result": "success"}

    async def test_list_tasks_by_session(self):
        """Test listing tasks by session."""
        manager = TaskManager()
        await manager.create_task("session_1", "Task 1")
        await manager.create_task("session_1", "Task 2")
        await manager.create_task("session_2", "Task 3")
        
        tasks = await manager.list_tasks("session_1")
        assert len(tasks) == 2
        assert all(t.session_id == "session_1" for t in tasks)
