from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
_LOG = BASE / "logs" / "calendar_posts.jsonl"
_DOC = BASE / "docs" / "status-handoff.md"
_ENV = BASE / ".env"
if _ENV.exists():
    from dotenv import load_dotenv
    load_dotenv(_ENV)


def _stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def main() -> None:
    if not _LOG.exists():
        print("status_export: no calendar log")
        return
    rows = []
    for line in _LOG.read_text(encoding="utf-8").splitlines()[-200:]:
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    by_target = {}
    for row in rows:
        by_target[row.get("target", "unknown")] = by_target.get(row.get("target", "unknown"), 0) + 1
    lines = [
        "",
        f"## {datetime.now(timezone.utc).date().isoformat()} status",
        f"- calendar_posts_total={len(rows)}",
    ]
    for k, v in sorted(by_target.items()):
        lines.append(f"- calendar_posts_target={k}: count={v}")
    last = rows[-1] if rows else {}
    intent_source = (last.get("content", "") + "\n" + last.get("url", "")).strip()
    handoff_hash = _stable_hash(intent_source) if intent_source else "NO_HANDOFF"
    expected_hash = last.get("verify_handoff", "") or last.get("handoff_id", "") or ""
    handoff_status = "ok" if expected_hash in {handoff_hash, "NO_HANDOFF"} else "mismatch" if expected_hash else "missing"
    handoff_id = last.get("handoff_id", "")
    if handoff_id:
        lines.append(f"- most_recent_post_handoff_id={handoff_id}")
    lines.append(f"- most_recent_post_handoff_hash={handoff_hash}")
    lines.append(f"- handoff_status={handoff_status}")
    snippet = "\n".join(lines)
    _DOC.parent.mkdir(parents=True, exist_ok=True)
    text = _DOC.read_text(encoding="utf-8") if _DOC.exists() else ""
    _DOC.write_text(text + "\n" + snippet + "\n", encoding="utf-8")
    print("status_export: wrote to", _DOC)


if __name__ == "__main__":
    main()
