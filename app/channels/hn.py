"""Hacker News channel stub."""
from __future__ import annotations
import os
from .base import ChannelPost
HN_COOKIE = os.getenv("HN_COOKIE", "")
async def post(post: ChannelPost) -> dict:
    if not HN_COOKIE:
        return {"ok": False, "error": "HN_COOKIE missing"}
    return {"ok": False, "error": "not implemented"}
