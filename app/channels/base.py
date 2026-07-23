"""Base channel interface."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

@dataclass
class ChannelPost:
    content: str
    url: Optional[str] = None
    media_urls: list[str] | None = None
    tags: list[str] | None = None
EOF

cat > app/channels/linkedin.py <<'PY'
"""LinkedIn channel stub."""
from __future__ import annotations

import os
from .base import ChannelPost

LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", "")

async def post(post: ChannelPost) -> dict:
    if not LINKEDIN_ACCESS_TOKEN:
        return {"ok": False, "error": "LINKEDIN_ACCESS_TOKEN missing"}
    return {"ok": False, "error": "not implemented"}
