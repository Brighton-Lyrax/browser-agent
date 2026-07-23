from __future__ import annotations
import os
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

        logged_in = _is_logged_in(page)
        if not logged_in:
            _login(page, username, password)
            logged_in = _is_logged_in(page)
            if not logged_in:
                browser.close()
                return {"ok": False, "error": "login failed", "state": "login_failed", "url": page.url}

        page.goto("https://news.ycombinator.com/submit", timeout=15000, wait_until="domcontentloaded")

        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            pass

        title_input = page.locator("input[name='title']").first
        if not title_input.count() or not title_input.is_visible():
            return {
                "ok": False,
                "error": "submit form not available: title input missing",
                "state": "form_missing",
                "url": page.url,
                "debug_body": page.evaluate("document.body.innerText")[:200],
                "debug_html": page.evaluate("document.body.innerHTML")[:500],
            }
        title_input.fill(title)

        if is_link:
            page.locator("input[name='url']").first.fill(post.url or "")
        else:
            body_text = (post.content or "").strip()
            if body_text:
                textarea = page.locator("textarea").first
                textarea.wait_for(state="visible", timeout=15000)
                textarea.fill(body_text)

        page.locator("form button[type='submit'], button:has-text('submit')").first.click()

        try:
            page.wait_for_load_state("domcontentloaded", timeout=12000)
        except Exception:
            pass
        browser.close()
        return {"ok": True, "url": page.url, "state": "submitted_or_navigate_pending"}


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
    page.click("input[value='login'], button:has-text('login')")
    page.wait_for_url("**/news*", timeout=15000)
