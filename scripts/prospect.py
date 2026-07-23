#!/usr/bin/env python3
"""ReplyPilot customer prospecting workflow."""
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

LEADS_DIR = Path(__file__).resolve().parent.parent / "data"
LEADS_DIR.mkdir(exist_ok=True)

PROSPECTS_FILE = LEADS_DIR / "prospects.jsonl"


def log_prospect(source: str, handle: str, context: str):
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "handle": handle,
        "context": context,
        "status": "identified",
    }
    with PROSPECTS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "
")
    return row


if __name__ == "__main__":
    samples = [
        ("reddit", "u/agency_owner", "Asked about lead response tools in r/digital_marketing"),
        ("hn", "jane_doe", "Comment: 'We need something faster than Intercom'"),
        ("twitter", "@founder_sam", "Tweeted about slow lead replies killing pipeline"),
    ]
    for src, handle, ctx in samples:
        print(log_prospect(src, handle, ctx))
    print("prospects logged to", PROSPECTS_FILE)
