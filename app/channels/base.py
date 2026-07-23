from __future__ import annotations

"""Base channel interface."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class ChannelPost:
    content: str
    url: Optional[str] = None
    media_urls: list[str] | None = None
    tags: list[str] | None = None
