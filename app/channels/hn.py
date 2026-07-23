from __future__ import annotations
import os
from typing import Optional
from .base import ChannelPost


def missing() -> Optional[str]:
    missing_fields = []
    if not os.getenv("HN_USERNAME"):
        missing_fields.append("HN_USERNAME")
    if not os.getenv("HN_PASSWORD"):
        missing_fields.append("HN_PASSWORD")
    return ", ".join(missing_fields) if missing_fields else None


def post(post: ChannelPost) -> dict:
    if err := missing():
        return {"ok": False, "error": f"missing env: {err}"}

    username = os.getenv("HN_USERNAME", "")
    password = os.getenv("HN_PASSWORD", "")
    title = (post.content or "").strip().splitlines()[0][:80]
    is_link = bool(post.url)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {"ok": False, "error": "playwright not installed"}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        logged_in = _is_logged_in(page)
        print('DEBUG_LOGGED_IN=', logged_in)
        if not logged_in:
            _login(page, username, password)

        print('DEBUG_URL_AFTER_LOGIN=', page.url)
        print('DEBUG_TITLE_AFTER_LOGIN=', page.title())
        print('DEBUG_VISIBLE_SUBMIT=', page.is_visible("text=submit", timeout=1000))

        page.goto("https://news.ycombinator.com/submit", timeout=15000, wait_until="domcontentloaded")
        print('DEBUG_SUBMIT_URL=', page.url)
        print('DEBUG_SUBMIT_TITLE=', page.title())
        print('DEBUG_SUBMIT_BODY=', page.evaluate("document.body.innerText")[:2000])

        try:
            page.locator("input[name='title']").first.fill(title)
            print('DEBUG_TITLE_FILLED')
        except Exception as e:
            print('DEBUG_TITLE_FILL_FAIL=', repr(e))

        action = "link" if is_link else "text"
        result = _perform_action(page, title, action, post.url, post.content)
        browser.close()
        return result


def _is_logged_in(page) -> bool:
    try:
        page.goto("https://news.ycombinator.com", timeout=15000, wait_until="domcontentloaded")
        return page.is_visible("text=submit", timeout=3000)
    except Exception:
        return False


def _login(page, username: str, password: str) -> None:
    page.goto("https://news.ycombinator.com/login", timeout=15000, wait_until="domcontentloaded")
    page.fill("input[name='acct']", username)
    page.fill("input[name='pw']", password)
    page.click("button:has-text('login')")
    page.wait_for_url("**/news*", timeout=15000)


def _perform_action(page, title: str, action: str, url: Optional[str], text: Optional[str]) -> dict:
    try:
        page.locator("input[name='title']").first.fill(title)
    except Exception as e:
        return {"ok": False, "error": f"submit form not available: {e}", "state": "form_missing", "url": page.url, "debug_body": page.evaluate("document.body.innerText")[:2000]}

    try:
        if action == "link" and url:
            page.locator("input[name='url']").first.fill(url)
        elif text:
            textarea = page.locator("textarea").first
            textarea.fill(text or "")

        page.locator("form button[type='submit'], button:has-text('submit')").first.click()
        try:
            page.wait_for_load_state("domcontentloaded", timeout=12000)
        except Exception:
            pass
        return {"ok": True, "url": page.url, "state": "submitted_or_navigate_pending"}
    except Exception as exc:
        return {"ok": False, "error": f"submit form action failed: {exc}", "state": "action_failed", "url": page.url, "debug_body": page.evaluate("document.body.innerText")[:2000]}
