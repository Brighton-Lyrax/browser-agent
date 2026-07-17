"""
Unit tests for the browser module.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.core.browser import BrowserPool, BrowserAgent
from app.core.exceptions import BrowserException, TimeoutException


@pytest.mark.asyncio
class TestBrowserPool:
    """Tests for BrowserPool class."""

    async def test_initialize(self):
        """Test browser pool initialization."""
        pool = BrowserPool()
        with patch('app.core.browser.async_playwright') as mock_pw:
            mock_pw.return_value.start = AsyncMock()
            await pool.initialize()
            mock_pw.return_value.start.assert_called_once()

    async def test_create_browser(self):
        """Test browser creation."""
        pool = BrowserPool()
        pool.playwright = MagicMock()
        pool.playwright.chromium.launch = AsyncMock(return_value=MagicMock())
        
        browser = await pool.get_browser()
        assert browser is not None
        assert len(pool.browsers) == 1

    async def test_max_browsers_limit(self):
        """Test that max browser instances limit is respected."""
        pool = BrowserPool()
        pool.max_instances = 2
        pool.playwright = MagicMock()
        pool.playwright.chromium.launch = AsyncMock(return_value=MagicMock())
        
        # Create 2 browsers
        browser1 = await pool.get_browser()
        browser2 = await pool.get_browser()
        assert len(pool.browsers) == 2
        
        # Trying to create 3rd should return first one
        browser3 = await pool.get_browser()
        assert browser3 == browser1
        assert len(pool.browsers) == 2


@pytest.mark.asyncio
class TestBrowserAgent:
    """Tests for BrowserAgent class."""

    async def test_navigate(self):
        """Test navigation to URL."""
        pool = BrowserPool()
        agent = BrowserAgent(pool)
        
        mock_page = AsyncMock()
        mock_page.title = AsyncMock(return_value="Test Page")
        mock_page.goto = AsyncMock()
        mock_page.url = "https://example.com"
        
        pool.pages["session_1"] = mock_page
        
        result = await agent.navigate("session_1", "https://example.com")
        
        assert result["success"] is True
        assert result["url"] == "https://example.com"
        mock_page.goto.assert_called_once()

    async def test_navigate_timeout(self):
        """Test navigation timeout."""
        pool = BrowserPool()
        agent = BrowserAgent(pool)
        
        mock_page = AsyncMock()
        mock_page.goto = AsyncMock(side_effect=Exception("Timeout"))
        
        pool.pages["session_1"] = mock_page
        
        with pytest.raises(Exception):
            await agent.navigate("session_1", "https://example.com")

    async def test_click(self):
        """Test clicking an element."""
        pool = BrowserPool()
        agent = BrowserAgent(pool)
        
        mock_page = AsyncMock()
        mock_page.click = AsyncMock()
        
        pool.pages["session_1"] = mock_page
        
        result = await agent.click("session_1", ".button")
        
        assert result["success"] is True
        mock_page.click.assert_called_once()

    async def test_type_text(self):
        """Test typing text into an input."""
        pool = BrowserPool()
        agent = BrowserAgent(pool)
        
        mock_page = AsyncMock()
        mock_page.fill = AsyncMock()
        mock_page.type = AsyncMock()
        
        pool.pages["session_1"] = mock_page
        
        result = await agent.type_text("session_1", "input[name='search']", "test query")
        
        assert result["success"] is True
        mock_page.fill.assert_called_once()
        mock_page.type.assert_called_once()
