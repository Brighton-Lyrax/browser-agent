from __future__ import annotations
import os
import re
from typing import Optional
from .base import ChannelPost


def missing() -> Optional[str]:
    fields = []
    if not os.getenv("HN_USERNAME"):
        fields.append("HN_USERNAME")
    if not os.getenv("HN_PASSWORD"):
        fields.append("HN_PASSWORD")
    return ", ".join(fields) if fields else None


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
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=(
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        ))
        page = context.new_page()

        if not _is_logged_in(page):
            _login(page, username, password)
            if not _is_logged_in(page):
                browser.close()
                return {"ok": False, "error": "login failed", "state": "login_failed", "url": page.url}

        # Bypass front-page false-positive by loading submit directly.
        page.goto("https://news.ycombinator.com/submit", timeout=15000, wait_until="domcontentloaded")
        body = page.evaluate("document.body.innerText") or ""
        if "Sorry." in body or "/login" in (page.url or "").lower():
            browser.close()
            return {
                "ok": False,
                "error": "HN submit unavailable: account may require stronger auth, karma, or is rate-limited",
                "state": "submit_locked",
                "url": page.url,
            }

        try:
            if is_link:
                page.locator("input[name='title']").first.fill(title)
                page.locator("input[name='url']").first.fill(post.url or "")
            else:
                body_text = (post.content or "").strip()
                if not body_text:
                    browser.close()
                    return {"ok": False, "error": "no content for HN text post"}
                page.locator("input[name='title']").first.fill(title)
                page.locator("textarea").first.fill(body_text)

            page.locator("form button[type='submit'], button:has-text('submit')").first.click()
            try:
                page.wait_for_load_state("domcontentloaded", timeout=12000)
            except Exception:
                pass
            browser.close()
            return {"ok": True, "url": page.url, "state": "submitted_or_navigate_pending"}
        except Exception as exc:
            browser.close()
            return {"ok": False, "error": f"submit form action failed: {exc}", "state": "action_failed", "url": page.url}


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
