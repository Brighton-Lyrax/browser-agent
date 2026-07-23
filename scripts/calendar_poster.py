"""
Daily calendar poster: posts one item per day from marketing/calendar/q3-2026.md
to available channels. Intended to run from cron.
"""
from __future__ import annotations

import re
from pathlib import Path
from datetime import datetime, timezone

BASE = Path(__file__).resolve().parent.parent
CALENDAR = BASE / "marketing" / "calendar" / "q3-2026.md"
POST_LOG = BASE / "logs" / "calendar_posts.jsonl"


def load_calendar_items():
    items = []
    if not CALENDAR.exists():
        return items
    text = CALENDAR.read_text(encoding="utf-8")
    for line in text.splitlines():
        line = line.strip()
        m = re.match(r"^- \w+: (\w+)\s+(.+)$", line)
        if not m:
            continue
        channel, text_body = m.group(1), m.group(2)
        if channel not in {"Twitter", "LinkedIn", "Reddit", "Telegram", "Newsletter", "HN"}:
            continue
        items.append({"channel": channel.lower(), "text": text_body})
    return items


def pick_today(items):
    if not items:
        return None
    idx = int(datetime.now(timezone.utc).timestamp() / 86400) % len(items)
    return items[idx]


def render_text(pick):
    template_map = {
        "twitter": "🚀 {text}",
        "linkedin": "📢 {text}",
        "reddit": "{text}",
        "telegram": "📣 {text}",
        "hn": "📰 {text}",
        "newsletter": "📧 {text}",
    }
    prefix = template_map.get(pick["channel"], "")
    return prefix.format(text=pick["text"]) if prefix else pick["text"]


def main():
    items = load_calendar_items()
    pick = pick_today(items)
    if not pick:
        print("no calendar items")
        return
    channel = pick["channel"]
    text = render_text(pick)
    if channel == "newsletter":
        print(f"skipping channel: {channel}")
        return
    target = "telegram" if channel in {"twitter", "linkedin", "reddit"} else channel
    if target not in {"twitter", "telegram"}:
        print(f"skipping channel: {channel}")
        return
    from scripts.channel_poster import main as poster_main
    import sys
    sys.argv = ["channel_poster.py", target, "--content", text]
    try:
        poster_main()
    except SystemExit:
        pass
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "channel": channel,
        "target": target,
        "content": text,
    }
    with POST_LOG.open("a", encoding="utf-8") as f:
        f.write(__import__("json").dumps(row) + "\n")
    print(row)


if __name__ == "__main__":
    main()
