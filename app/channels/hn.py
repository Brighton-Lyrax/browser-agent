from __future__ import annotations
import os
from typing import Optional
from .base import ChannelPost

def missing() -> Optional[str]:
    return None

def post(post: ChannelPost) -> dict:
    # HN posting requires authenticated session; left as manual-ready stub
    return {"ok": False, "error": "HN posting not implemented; needs session automation"}
