"""
Browser automation engine using Playwright.
Handles browser instances and interactions.
"""

from typing import List, Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from app.core.logging import get_logger
from app.core.exceptions import BrowserException, TimeoutException, InteractionException, NavigationException
from app.config import settings
import asyncio

logger = get_logger(__name__)


class BrowserPool:
    """Manages a pool of browser instances for concurrent operations."""

    def __init__(self):
        self.browsers: List[Browser] = []
        self.pages: Dict[str, Page] = {}
        self.playwright = None
        self.max_instances = settings.max_browser_instances

    async def initialize(self):
        """Initialize the browser pool."""
        try:
            self.playwright = await async_playwright().start()
            logger.info(
                "browser_pool_initialized",
                browser_type=settings.browser_type,
                max_instances=self.max_instances
            )
        except Exception as e:
            logger.error("browser_pool_init_failed", error=str(e))
            raise BrowserException(f"Failed to initialize browser pool: {e}")

    async def get_browser(self) -> Browser:
        """Get or create a browser instance."""
        try:
            if len(self.browsers) < self.max_instances:
                browser = await self.playwright.chromium.launch(
                    headless=settings.headless_mode
                )
                self.browsers.append(browser)
                logger.info("browser_created", total_browsers=len(self.browsers))
                return browser
            else:
                logger.warning("max_browser_instances_reached")
                return self.browsers[0]
        except Exception as e:
            logger.error("browser_creation_failed", error=str(e))
            raise BrowserException(f"Failed to create browser instance: {e}")

    async def create_page(self, session_id: str) -> Page:
        """Create a new page for a session."""
        try:
            browser = await self.get_browser()
            page = await browser.new_page()
            self.pages[session_id] = page
            
            # Set viewport for consistent rendering
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            logger.info("page_created", session_id=session_id)
            return page
        except Exception as e:
            logger.error("page_creation_failed", session_id=session_id, error=str(e))
            raise BrowserException(f"Failed to create page: {e}")

    async def get_page(self, session_id: str) -> Optional[Page]:
        """Get an existing page for a session."""
        return self.pages.get(session_id)

    async def close_page(self, session_id: str):
        """Close a page and cleanup."""
        try:
            page = self.pages.pop(session_id, None)
            if page:
                await page.close()
                logger.info("page_closed", session_id=session_id)
        except Exception as e:
            logger.error("page_close_failed", session_id=session_id, error=str(e))

    async def close_all(self):
        """Close all browsers and cleanup."""
        try:
            for session_id in list(self.pages.keys()):
                await self.close_page(session_id)
            
            for browser in self.browsers:
                await browser.close()
            
            if self.playwright:
                await self.playwright.stop()
            
            logger.info("browser_pool_closed")
        except Exception as e:
            logger.error("browser_pool_close_failed", error=str(e))


class BrowserAgent:
    """Main agent for browser automation and human-like actions."""

    def __init__(self, pool: BrowserPool):
        self.pool = pool

    async def navigate(self, session_id: str, url: str) -> Dict[str, Any]:
        """Navigate to a URL."""
        try:
            page = await self.pool.get_page(session_id)
            if not page:
                raise BrowserException("Page not found for session")
            
            await asyncio.wait_for(
                page.goto(url, wait_until="domcontentloaded"),
                timeout=settings.browser_timeout / 1000
            )
            
            title = await page.title()
            logger.info("page_navigated", session_id=session_id, url=url, title=title)
            
            return {
                "success": True,
                "url": page.url,
                "title": title,
                "message": f"Successfully navigated to {url}"
            }
        except asyncio.TimeoutError:
            logger.error("navigation_timeout", session_id=session_id, url=url)
            raise TimeoutException(f"Navigation to {url} timed out")
        except Exception as e:
            logger.error("navigation_failed", session_id=session_id, url=url, error=str(e))
            raise NavigationException(f"Failed to navigate to {url}: {e}")

    async def click(self, session_id: str, selector: str) -> Dict[str, Any]:
        """Click an element on the page."""
        try:
            page = await self.pool.get_page(session_id)
            if not page:
                raise BrowserException("Page not found for session")
            
            await page.click(selector, timeout=settings.browser_timeout)
            
            logger.info("element_clicked", session_id=session_id, selector=selector)
            return {
                "success": True,
                "message": f"Successfully clicked element: {selector}"
            }
        except Exception as e:
            logger.error("click_failed", session_id=session_id, selector=selector, error=str(e))
            raise InteractionException(f"Failed to click element {selector}: {e}")

    async def type_text(self, session_id: str, selector: str, text: str, delay: int = 50) -> Dict[str, Any]:
        """Type text into an input field with human-like delays."""
        try:
            page = await self.pool.get_page(session_id)
            if not page:
                raise BrowserException("Page not found for session")
            
            await page.fill(selector, "")  # Clear first
            await page.type(selector, text, delay=delay)
            
            logger.info(
                "text_typed",
                session_id=session_id,
                selector=selector,
                text_length=len(text)
            )
            return {
                "success": True,
                "message": f"Successfully typed text into {selector}"
            }
        except Exception as e:
            logger.error("type_failed", session_id=session_id, selector=selector, error=str(e))
            raise InteractionException(f"Failed to type text in {selector}: {e}")

    async def scroll(self, session_id: str, direction: str = "down", amount: int = 3) -> Dict[str, Any]:
        """Scroll the page."""
        try:
            page = await self.pool.get_page(session_id)
            if not page:
                raise BrowserException("Page not found for session")
            
            scroll_distance = amount * 100  # pixels
            if direction.lower() == "down":
                await page.evaluate(f"window.scrollBy(0, {scroll_distance})")
            elif direction.lower() == "up":
                await page.evaluate(f"window.scrollBy(0, {-scroll_distance})")
            else:
                raise ValueError(f"Invalid scroll direction: {direction}")
            
            logger.info(
                "page_scrolled",
                session_id=session_id,
                direction=direction,
                amount=amount
            )
            return {
                "success": True,
                "message": f"Successfully scrolled {direction}"
            }
        except Exception as e:
            logger.error("scroll_failed", session_id=session_id, error=str(e))
            raise InteractionException(f"Failed to scroll: {e}")

    async def get_page_content(self, session_id: str) -> Dict[str, Any]:
        """Get the current page HTML content."""
        try:
            page = await self.pool.get_page(session_id)
            if not page:
                raise BrowserException("Page not found for session")
            
            content = await page.content()
            
            logger.info("page_content_retrieved", session_id=session_id)
            return {
                "success": True,
                "content": content,
                "url": page.url
            }
        except Exception as e:
            logger.error("get_content_failed", session_id=session_id, error=str(e))
            raise BrowserException(f"Failed to get page content: {e}")

    async def take_screenshot(self, session_id: str) -> Dict[str, Any]:
        """Take a screenshot of the current page."""
        try:
            page = await self.pool.get_page(session_id)
            if not page:
                raise BrowserException("Page not found for session")
            
            screenshot = await page.screenshot(full_page=False)
            
            import base64
            screenshot_b64 = base64.b64encode(screenshot).decode('utf-8')
            
            logger.info("screenshot_taken", session_id=session_id)
            return {
                "success": True,
                "screenshot": screenshot_b64,
                "url": page.url
            }
        except Exception as e:
            logger.error("screenshot_failed", session_id=session_id, error=str(e))
            raise BrowserException(f"Failed to take screenshot: {e}")

    async def execute_javascript(self, session_id: str, script: str) -> Dict[str, Any]:
        """Execute JavaScript on the page."""
        try:
            page = await self.pool.get_page(session_id)
            if not page:
                raise BrowserException("Page not found for session")
            
            result = await page.evaluate(script)
            
            logger.info("javascript_executed", session_id=session_id)
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            logger.error("javascript_execution_failed", session_id=session_id, error=str(e))
            raise BrowserException(f"Failed to execute JavaScript: {e}")

    async def wait_for_element(self, session_id: str, selector: str, timeout: int = 5000) -> Dict[str, Any]:
        """Wait for an element to appear on the page."""
        try:
            page = await self.pool.get_page(session_id)
            if not page:
                raise BrowserException("Page not found for session")
            
            await page.wait_for_selector(selector, timeout=timeout)
            
            logger.info("element_found", session_id=session_id, selector=selector)
            return {
                "success": True,
                "message": f"Element found: {selector}"
            }
        except Exception as e:
            logger.error("wait_for_element_failed", session_id=session_id, selector=selector, error=str(e))
            raise TimeoutException(f"Element not found: {selector}")


# Global browser pool instance
browser_pool = BrowserPool()
