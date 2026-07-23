from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
_env_path = BASE / ".env"
if _env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(_env_path)
else:
    import os
    for _k in list(os.environ):
        if _k.startswith("SMTP_") or False:
            pass

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


def main():
    parser = argparse.ArgumentParser(description="ReplyPilot channel poster")
    parser.add_argument("channel", nargs="?", choices=list(CHANNELS.keys()) + ["all"], help="target channel")
    parser.add_argument("--content", required=False, default="", help="post text")
    parser.add_argument("--url", required=False, default="", help="optional link")
    parser.add_argument("--media", required=False, default="", help="comma-separated media URLs")
    parser.add_argument("--list", action="store_true", help="list configured channels")
    args = parser.parse_args()

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
        missing = mod.missing() if hasattr(mod, "missing") else None
        if missing:
            row = {"channel": name, "ok": False, "error": f"missing env: {missing}"}
        else:
            try:
                result = mod.post(post_obj)
                row = {"channel": name, "ok": bool(result.get("ok")) if isinstance(result, dict) else False, "result": result}
            except Exception as e:
                row = {"channel": name, "ok": False, "error": str(e)}
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
