"""Uptime check for deployed endpoints."""
from __future__ import annotations

import json
from pathlib import Path
from urllib.request import urlopen
from datetime import datetime, timezone

BASE = Path(__file__).resolve().parent.parent
SITES = [
    ("vercel", "https://browser-agent-steel.vercel.app/health"),
    ("gumroad", "https://brightonlyrax.gumroad.com/l/rzafxw"),
]


def check(name: str, url: str) -> dict:
    status = "down"
    code = None
    error = None
    try:
        with urlopen(url, timeout=15) as r:
            code = getattr(r, "status", None)
            status = "up" if (code or 200) < 500 else "degraded"
    except Exception as exc:
        error = str(exc)
        status = "down"
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "name": name,
        "url": url,
        "status": status,
        "code": code,
        "error": error,
    }
    return row


def main():
    rows = [check(name, url) for name, url in SITES]
    out = BASE / "logs" / "uptime.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
