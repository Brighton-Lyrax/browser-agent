from __future__ import annotations
import os
import re
import tempfile
from pathlib import Path
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

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {"ok": False, "error": "playwright not installed"}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Attempt login if not already logged in
        if not _is_logged_in(page):
            _login(page, username, password)

        result = _perform_action(page, title, "link" if post.url else "text", post.url, post.content)

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
    try:
        page.wait_for_selector("#create_account", timeout=5000)
    except Exception:
        pass
    page.fill("input[name='acct']", username)
    page.fill("input[name='pw']", password)
    page.click("form button[type='submit']")
    page.wait_for_url("**/news*", timeout=15000)


def _perform_action(page, title: str, action: str, url: Optional[str], text: Optional[str]) -> dict:
    try:
        page.goto("https://news.ycombinator.com/submit", timeout=15000, wait_until="domcontentloaded")
    except Exception as e:
        return {"ok": False, "error": f"submit page load failed: {e}"}

    if page.is_visible("text=login", timeout=2000):
        return {"ok": False, "error": "login required even after _login flow", "state": "login_required"}

    try:
        if action == "link" and url:
            page.fill("input[name='title']", title)
            page.fill("input[name='url']", url)
            page.click("form button[type='submit']")
        else:
            page.fill("input[name='title']", title)
            if page.query_selector("textarea[name='text']"):
                page.fill("textarea[name='text']", text or "")
            page.click("form button[type='submit']")

        _wait_post_result(page)
        return {"ok": True, "url": page.url, "state": "submitted_or_navigate_pending"}
    except Exception as exc:
        return {"ok": False, "error": f"submit form action failed: {exc}"}


def _wait_post_result(page, timeout: int = 15000):
    try:
        page.wait_for_load_state("domcontentloaded", timeout=timeout)
    except Exception:
        pass
