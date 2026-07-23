"""Twitter channel stub."""
from __future__ import annotations
import os
from .base import ChannelPost
TWITTER_BEARER = os.getenv("TWITTER_BEARER_TOKEN", "")
async def post(post: ChannelPost) -> dict:
    if not TWITTER_BEARER:
        return {"ok": False, "error": "TWITTER_BEARER_TOKEN missing"}
    return {"ok": False, "error": "not implemented"}
