from __future__ import annotations
import os
from typing import Optional
from .base import ChannelPost

ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", "")

def missing() -> Optional[str]:
    if not ACCESS_TOKEN:
        return "LINKEDIN_ACCESS_TOKEN"
    return None

def post(post: ChannelPost) -> dict:
    if missing():
        return {"ok": False, "error": f"missing env: {missing()}"}
    try:
        import requests
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json",
        }
        # Simplified post stub; real posting requires person URN and valid content payload
        payload = {
            "author": "urn:li:person:REPLACE_WITH_PERSON_URN",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": post.content or ""},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }
        r = requests.post("https://api.linkedin.com/v2/ugcPosts", json=payload, headers=headers, timeout=20)
        return {"ok": r.status_code in (200, 201), "status": r.status_code, "response": r.text}
    except Exception as e:
        return {"ok": False, "error": str(e)}
