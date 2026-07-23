from __future__ import annotations
import os
from typing import Optional
from .base import ChannelPost

CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
USER_AGENT = os.getenv("REDDIT_USER_AGENT", "replypilot/0.1 by Brighton-Lyrax")
USERNAME = os.getenv("REDDIT_USERNAME", "")
PASSWORD = os.getenv("REDDIT_PASSWORD", "")

def missing() -> Optional[str]:
    if not all([CLIENT_ID, CLIENT_SECRET, USER_AGENT, USERNAME, PASSWORD]):
        return "REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT, REDDIT_USERNAME, REDDIT_PASSWORD"
    return None

def post(post: ChannelPost) -> dict:
    if missing():
        return {"ok": False, "error": f"missing env: {missing()}"}
    try:
        import praw
        reddit = praw.Reddit(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            user_agent=USER_AGENT,
            username=USERNAME,
            password=PASSWORD,
        )
        reddit.validate_on_submit = True
        sub = os.getenv("REDDIT_SUBREDDIT", "test")
        submission = reddit.subreddit(sub).submit(post.content or "", url=post.url or "")
        return {"ok": True, "id": submission.id, "url": f"https://reddit.com{submission.permalink}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
