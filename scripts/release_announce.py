from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

BASE = Path(__file__).resolve().parent.parent
_NOTES = BASE / "docs" / "release-notes.md"
_ENV = BASE / ".env"
if _ENV.exists():
    load_dotenv(_ENV)
_LOG = BASE / "logs" / "release_announces.jsonl"
_LOG.parent.mkdir(parents=True, exist_ok=True)

from app.channels import telegram  # noqa: E402


def _latest_version(text: str):
    m = re.search(r"^##\s+(v?\d+\.\d+\.\d+)", text, re.M | re.I)
    return m.group(1) if m else None


def _already_sent(version: str) -> bool:
    if not _LOG.exists():
        return False
    today = datetime.now(timezone.utc).date().isoformat()
    try:
        for line in _LOG.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row.get("version") == version and row.get("date") == today:
                return True
    except Exception:
        pass
    return False


def main():
    if not _NOTES.exists():
        print("release_announce: no release notes")
        return
    text = _NOTES.read_text(encoding="utf-8")
    version = _latest_version(text)
    if not version:
        print("release_announce: no version heading found")
        return
    if _already_sent(version):
        print(f"release_announce: already sent {version} today")
        return
    missing = telegram.missing() if hasattr(telegram, "missing") else None
    if missing:
        print(f"release_announce: telegram not ready — {missing}")
        return
    content = f"ReplyPilot {version} is live. See release notes in docs/release-notes.md"
    result = telegram.post(telegram.ChannelPost(content=content, url="https://browser-agent-steel.vercel.app"))
    with _LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(), "date": datetime.now(timezone.utc).date().isoformat(), "version": version, "result": result}) + "\n")
    print("release_announce:", result)


if __name__ == "__main__":
    main()
