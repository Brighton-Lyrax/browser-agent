from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
_ENV = BASE / ".env"
if _ENV.exists():
    from dotenv import load_dotenv
    load_dotenv(_ENV)

from app.channels.base import ChannelPost
from app.channels import twitter, reddit, linkedin, hn, telegram, discord

CHANNELS = {
    "twitter": twitter,
    "x": twitter,
    "reddit": reddit,
    "linkedin": linkedin,
    "hn": hn,
    "telegram": telegram,
    "discord": discord,
}


def _stable_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def main() -> None:
    parser = argparse.ArgumentParser(description="ReplyPilot channel poster")
    parser.add_argument("channel", nargs="?", choices=list(CHANNELS.keys()) + ["all"], help="target channel")
    parser.add_argument("--content", required=False, default="", help="post text")
    parser.add_argument("--url", required=False, default="", help="optional link")
    parser.add_argument("--media", required=False, default="", help="comma-separated media URLs")
    parser.add_argument("--list", action="store_true", help="list configured channels")
    parser.add_argument("--handoff-id", required=False, default="", help="stable handoff identifier")
    parser.add_argument("--verify-handoff", required=False, default="", help="prevent stale retry if intent/read-set changed")
    args = parser.parse_args()

    intent_source = (args.content + "\n" + args.url + "\n" + args.media).strip()
    if args.handoff_id:
        current_hash = "NO_HANDOFF"
        if intent_source:
            current_hash = _stable_hash(intent_source)
        if args.verify_handoff and current_hash not in {args.verify_handoff, "NO_HANDOFF"}:
            print(json.dumps({"ok": False, "error": "handoff_hash_mismatch", "expected": args.verify_handoff, "actual": current_hash}))
            sys.exit(0)

    if args.list:
        hints = {
            "twitter": "needs_billing_upgrade" if not os.getenv("TWITTER_API_KEY") else "blocked_by_402",
            "x": "needs_billing_upgrade" if not os.getenv("TWITTER_API_KEY") else "blocked_by_402",
            "reddit": "needs_reddit_token",
            "linkedin": "needs_linkedin_token",
            "hn": "needs_hn_credentials_and_manual_profile",
            "telegram": "ready",
            "discord": "needs_discord_token",
        }
        for name, mod in CHANNELS.items():
            missing = None
            if hasattr(mod, "missing"):
                missing = mod.missing()
            if missing:
                status = f"missing: {missing}"
            else:
                status = hints.get(name, "ready")
            print(f"{name}: {status}")
        return

    if not args.channel:
        parser.error("channel is required unless using --list")

    post_obj = ChannelPost(
        content=args.content,
        url=args.url or None,
        media_urls=[m.strip() for m in args.media.split(",") if m.strip()] or None,
    )

    targets = []
    if args.channel == "all":
        targets = [("twitter", twitter), ("reddit", reddit), ("linkedin", linkedin), ("telegram", telegram), ("discord", discord)]
    else:
        targets = [(args.channel, CHANNELS[args.channel])]

    results = []
    for name, mod in targets:
        if hasattr(mod, "missing") and mod.missing():
            row = {"channel": name, "ok": False, "error": f"missing env: {mod.missing()}"}
        else:
            try:
                result = mod.post(post_obj)
                row = {"channel": name, "ok": bool(result.get("ok")) if isinstance(result, dict) else False, "result": result}
            except Exception as e:
                row = {"channel": name, "ok": False, "error": str(e)}
        row.setdefault("handoff_id", args.handoff_id)
        results.append(row)
        print(row)

    out = BASE / "logs" / "posts.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("a", encoding="utf-8") as f:
        for row in results:
            row["ts"] = datetime.now(timezone.utc).isoformat()
            f.write(json.dumps(row) + "\n")


if __name__ == "__main__":
    main()
