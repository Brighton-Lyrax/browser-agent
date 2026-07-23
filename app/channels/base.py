from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class ChannelPost:
    content: str
    title: Optional[str] = None
    url: Optional[str] = None
    media_urls: list[str] | None = None
    tags: list[str] | None = None
