"""Reddit channel stub."""
from __future__ import annotations

import os
from .base import ChannelPost

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")

async def post(post: ChannelPost) -> dict:
    if not REDDIT_CLIENT_ID or not REDDIT_CLIENT_SECRET:
        return {"ok": False, "error": "REDDIT_CLIENT_ID or REDDIT_CLIENT_SECRET missing"}
    return {"ok": False, "error": "not implemented"}
