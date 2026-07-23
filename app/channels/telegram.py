from __future__ import annotations
import os
from typing import Optional
from .base import ChannelPost

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

def missing() -> Optional[str]:
    if not all([TOKEN, CHAT_ID]):
        return "TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID"
    return None

def post(post: ChannelPost) -> dict:
    if missing():
        return {"ok": False, "error": f"missing env: {missing()}"}
    try:
        import requests
        r = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": post.content or ""}, timeout=20)
        return {"ok": r.status_code == 200, "status": r.status_code}
    except Exception as e:
        return {"ok": False, "error": str(e)}
