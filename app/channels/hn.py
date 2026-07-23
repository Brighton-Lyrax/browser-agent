from __future__ import annotations
import os
import re
from typing import Optional
from .base import ChannelPost

try:
    from ..app.browser import open_page, type_text, click, wait_for, get_url
except Exception:  # pragma: no cover
    open_page = type_text = click = wait_for = get_url = None

_USERNAME = os.getenv("HN_USERNAME", "")
_PASSWORD = os.getenv("HN_PASSWORD", "")
_2FA = os.getenv("HN_2FA_CODE", "")
_BASE = "https://news.ycombinator.com"
_SUBMIT = f"{_BASE}/submit"


def missing() -> Optional[str]:
    if not _USERNAME or not _PASSWORD:
        return "HN_USERNAME and HN_PASSWORD are required"
    return None


def post(post: ChannelPost) -> dict:
    if missing():
        return {"ok": False, "error": f"missing env: {missing()}"}
    if open_page is None:
        return {"ok": False, "error": "browser module unavailable"}
    error = _try_post(post)
    if error:
        return error
    url = get_url() or ""
    item_url = url
    title = (post.title or post.content or "").splitlines()[0][:120]
    head_note = "submitted HN post" if not post.url else "submitted HN comment"
    return {
        "ok": True,
        "url": item_url,
        "state": "submitted_or_navigate_pending",
        "detail": head_note,
        "title": title,
    }


def _try_post(post: ChannelPost) -> dict | None:
    try:
        # Avoid duplicate redirect loops by directly loading submit page with navguard.
        open_page(
            f"{_SUBMIT}?navguard=replypilot-hn-auto",
            wait_seconds=8,
        )
        if not _is_logged_in():
            _login()
        if post.url and re.match(r"^https?://", post.url, re.IGNORECASE):
            if not _maybe_fill_link(post):
                if _looks_on_compose_or_throttle():
                    return {
                        "ok": False,
                        "error": "HN routed away from submit after detect login/compose state; retry later.",
                        "state": "routed_away",
                    }
                return {"ok": False, "error": "HN submit form not available after login/compose state"}
            return None
        if not _maybe_fill_text(post):
            return {"ok": False, "error": "HN submit form not available for text submission"}
        return None
    except Exception as exc:  # pragma: no cover
        return {"ok": False, "error": f"hn automation failed: {exc}"}


def _is_logged_in() -> bool:
    try:
        wait_for("a[href='/logout']", seconds=6)
        return True
    except Exception:
        return False


def _login() -> None:
    try:
        open_page(f"{_BASE}/login?navguard=replypilot-hn-login", wait_seconds=8)
        type_text("#create_account input[name='acct']", _USERNAME)
        type_text("#create_account input[name='pw']", _PASSWORD)
        click("#create_account button[type='submit']")
        _handle_challenge_if_visible()
        wait_for("a[href='/submit']", seconds=12)
        open_page(
            f"{_SUBMIT}?navguard=replypilot-hn-after-login",
            wait_seconds=8,
        )
    except Exception as exc:
        raise RuntimeError(f"login failed: {exc}")


def _handle_challenge_if_visible() -> None:
    try:
        if wait_for("input[name='wait']", seconds=3):
            code = _resolve_2fa()
            if code:
                type_text("input[name='wait']", code)
                click("form button[type='submit']")
    except Exception:
        pass


def _resolve_2fa() -> str:
    try:
        import pyotp
    except Exception:
        return _2FA or ""
    secret = os.getenv("HN_TOTP_SECRET", "")
    if not secret:
        return _2FA or ""
    return pyotp.TOTP(secret).now()


def _maybe_fill_link(post: ChannelPost) -> bool:
    try:
        wait_for("form[action='/submit'] input[name='title']", seconds=6)
    except Exception:
        return False
    title = (post.title or post.content or "").splitlines()[0][:80]
    type_text("form[action='/submit'] input[name='title']", title)
    if post.url:
        type_text("form[action='/submit'] input[name='url']", post.url)
    else:
        text = (post.content or "").strip()
        if not text:
            return False
        type_text("form[action='/submit'] textarea[name='text']", text)
    click("form[action='/submit'] button[type='submit']")
    _wait_post_result()
    return True


def _maybe_fill_text(post: ChannelPost) -> bool:
    text = (post.content or "").strip()
    if not text:
        return False
    try:
        wait_for("form[action='/submit'] textarea[name='text']", seconds=6)
    except Exception:
        return False
    type_text("form[action='/submit'] textarea[name='text']", text)
    click("form[action='/submit'] button[type='submit']")
    _wait_post_result()
    return True


def _wait_post_result() -> None:
    try:
        wait_for("form[action='/submit']", invert=True, seconds=8)
    except Exception:
        pass
    try:
        wait_for(".fatitem, .commtext, .error:not(:empty)", seconds=10)
    except Exception:
        pass


def _looks_on_compose_or_throttle() -> bool:
    try:
        text = (get_url() or "").lower() + ""
        body_text = ""
        try:
            body_text = __import__("hermes_tools").browser_console(expression="document.body.innerText")["body"]
        except Exception:
            pass
        composite = text + " " + body_text.lower()
        return any(token in composite for token in ["submit", "throttle", "you're doing that too much"])
    except Exception:
        return False
