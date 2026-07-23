from __future__ import annotations
import os
from typing import Optional
from .base import ChannelPost

def missing() -> Optional[str]:
    return "needs-session-automation"


def post(post: ChannelPost) -> dict:
    return {"ok": False, "error": "HN posting not implemented; needs session automation"}