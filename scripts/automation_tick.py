#!/usr/bin/env python3
"""ReplyPilot automation: hourly trend/repo scan stub."""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone

LOG = Path(__file__).resolve().parent.parent / "logs" / "automation.jsonl"
LOG.parent.mkdir(parents=True, exist_ok=True)


def log_event(event: str, detail: str = ""):
    row = {"ts": datetime.now(timezone.utc).isoformat(), "event": event, "detail": detail}
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "
")
    return row


if __name__ == "__main__":
    print(log_event("automation_tick", "scanned trends/repos"))
