"""
Gumroad sales sync: pull recent sales and append to logs/revenue.md + data/events.jsonl.
Requires GUMROAD_ACCESS_TOKEN in environment.
"""
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

BASE = Path(__file__).resolve().parent.parent
EVENTS = BASE / "data" / "events.jsonl"
REVENUE_LOG = BASE / "logs" / "revenue.md"


def log_revenue_event(event: dict):
    EVENTS.parent.mkdir(parents=True, exist_ok=True)
    with EVENTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def append_revenue_md(summary: str):
    REVENUE_LOG.parent.mkdir(parents=True, exist_ok=True)
    with REVENUE_LOG.open("a", encoding="utf-8") as f:
        f.write(f"- {datetime.now(timezone.utc).date().isoformat()} — {summary}\n")


def main():
    import urllib.request
    import os
    token = os.environ.get("GUMROAD_ACCESS_TOKEN", "")
    if not token:
        print("GUMROAD_ACCESS_TOKEN missing; sync skipped")
        return
    req = urllib.request.Request(
        "https://api.gumroad.com/v2/sales",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    sales = data.get("sales", []) if isinstance(data, dict) else []
    total_cents = 0
    for sale in sales:
        total_cents += int(sale.get("price", 0) or 0)
        event = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": "gumroad_sale",
            "sale_id": sale.get("id"),
            "product_id": sale.get("product_id"),
            "price_cents": sale.get("price"),
            "currency": sale.get("currency", "usd"),
            "email": sale.get("email"),
        }
        log_revenue_event(event)
    summary = f"Gumroad sales={len(sales)} estimated_usd={total_cents/100:.2f}"
    append_revenue_md(summary)
    print(f"synced sales={len(sales)} est_usd={total_cents/100:.2f}")
    try:
        import os as _os
        bot_token = _os.environ.get("TELEGRAM_BOT_TOKEN", "")
        chat_id = _os.environ.get("TELEGRAM_CHAT_ID", "")
        if bot_token and chat_id and total_cents > 0:
            text = f"Revenue sync: {summary}"
            payload = json.dumps({"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}).encode("utf-8")
            req = urllib.request.Request(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                resp.read()
    except Exception:
        pass


if __name__ == "__main__":
    main()
