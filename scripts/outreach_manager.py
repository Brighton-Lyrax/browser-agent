"""
Outreach manager — personalized, non-spam prospecting.

Usage:
  python scripts/outreach_manager.py list
  python scripts/outreach_manager.py draft <source> <handle>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
import datetime

BASE = Path(__file__).resolve().parent.parent
PROSPECTS = BASE / "outreach" / "prospects.jsonl"
SEQUENCES = BASE / "outreach" / "sequences.jsonl"


def load_prospects():
    if not PROSPECTS.exists():
        return []
    rows = []
    with PROSPECTS.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def save_prospect(row):
    PROSPECTS.parent.mkdir(parents=True, exist_ok=True)
    with PROSPECTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    return row


def list_prospects():
    rows = load_prospects()
    print(f"loaded {len(rows)} prospects")
    for r in rows[-20:]:
        print(
            f"- {r.get('ts','?')[:10]} | {r.get('source','?')} | {r.get('handle','?')} | {r.get('status','?')}"
        )


def draft(source, handle):
    templates = {
        "email": BASE / "outreach/templates/email.md",
        "twitter": BASE / "outreach/templates/twitter.md",
        "hn": BASE / "outreach/templates/hn.md",
        "reddit": BASE / "outreach/templates/reddit.md",
    }
    key = (source or "").lower()
    tpl_path = templates.get(key, templates["email"])
    tpl = tpl_path.read_text(encoding="utf-8").strip()
    rendered = tpl.replace("{name}", handle)
    print("TEMPLATE:")
    print(rendered)
    row = {
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source": source,
        "handle": handle,
        "status": "drafted",
        "template": key,
    }
    return save_prospect(row)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("commands: list | draft <source> <handle>")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "list":
        list_prospects()
    elif cmd == "draft" and len(sys.argv) >= 4:
        draft(sys.argv[2], sys.argv[3])
    else:
        print("unknown command")
        sys.exit(1)
