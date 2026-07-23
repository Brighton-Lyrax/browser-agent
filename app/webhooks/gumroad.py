"""
Gumroad webhook handler stub.

Set GUMROAD_WEBHOOK_SECRET in .env to verify signatures.
"""
from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any

from fastapi import APIRouter, Request

from app.main import _append_jsonl
from app.main import EVENTS

router = APIRouter()


def _verify(body: bytes, secret: str, signature: str | None) -> bool:
    if not signature:
        return False
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/webhook/gumroad")
async def gumroad_webhook(request: Request):
    raw = await request.body()
    sig = request.headers.get("X-Gumroad-Signature")
    from app.main import _load_project_env; _load_project_env()
    import os
    secret = os.getenv("GUMROAD_WEBHOOK_SECRET", "")
    if secret and not _verify(raw, secret, sig):
        return {"ok": False, "error": "bad signature"}
    try:
        body = json.loads(raw)
    except Exception:
        body = {"raw": raw.decode("utf-8", errors="replace")}
    _append_jsonl(EVENTS, {"ts": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(), "event": "webhook_gumroad", "body": body})
    return {"ok": True}
