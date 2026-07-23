from __future__ import annotations
import os
from typing import Optional
from .base import ChannelPost

BEARER = os.getenv("TWITTER_BEARER_TOKEN", "")
API_KEY = os.getenv("TWITTER_CLIENT_ID", "")
API_SECRET = os.getenv("TWITTER_CLIENT_SECRET", "")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "")
REFRESH_TOKEN = os.getenv("TWITTER_REFRESH_TOKEN", "")


def missing() -> Optional[str]:
    if not all([BEARER, API_KEY, API_SECRET, ACCESS_TOKEN, REFRESH_TOKEN]):
        return "TWITTER_BEARER_TOKEN, TWITTER_CLIENT_ID, TWITTER_CLIENT_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_REFRESH_TOKEN"
    return None


def post(post: ChannelPost) -> dict:
    if missing():
        return {"ok": False, "error": f"missing env: {missing()}"}
    try:
        import tweepy
        client = tweepy.Client(
            bearer_token=BEARER,
            consumer_key=API_KEY,
            consumer_secret=API_SECRET,
            access_token=ACCESS_TOKEN,
            # access_token_secret not available in current mapping; if needed, set TWITTER_ACCESS_SECRET
        )
        result = client.create_tweet(text=post.content or "")
        return {"ok": True, "id": result.data.get("id") if result and result.data else None, "url": f"https://x.com/i/status/{result.data['id']}" if result and result.data else None}
    except Exception as e:
        return {"ok": False, "error": str(e)}
