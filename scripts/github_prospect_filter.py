"""
GitHub prospect filter.

Flags repos/users whose README/issues mention lead-response latency,
slow replies, follow-ups, or checkout gaps — exact problem match.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

KEYWORDS = [
    "lead",
    "followup",
    "follow-up",
    "reply",
    "checkout",
    "revenue",
    "agency",
    "automation",
    "browser",
]

PM_PATTERNS = [
    re.compile(r"\b(lead\s*response|first\s*reply|follow\s*up|checkout|revenue\s*attribution|browser\s*automation)\b", re.I),
]


def score_text(text: str) -> float:
    if not text:
        return 0.0
    t = text.lower()
    kw = sum(1 for k in KEYWORDS if k in t)
    pm = sum(1 for p in PM_PATTERNS if p.search(t))
    return min(1.0, kw * 0.1 + pm * 0.3)


def flag_repo(name: str, description: str, readme_excerpt: str):
    s = score_text(description + " " + readme_excerpt)
    return {
        "ts": datetime.now(timezone.utc).isoformat(),
        "name": name,
        "score": round(s, 3),
        "flagged": s >= 0.5,
    }


if __name__ == "__main__":
    samples = [
        ("owner/repo", "Lead capture and browser automation backend", "FastAPI lead bot with follow-up queue"),
        ("owner/crm", "Full CRM with email and support", "Customer support and ticketing"),
    ]
    for repo, desc, excerpt in samples:
        print(flag_repo(repo, desc, excerpt))
