from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from datetime import datetime, timezone
import json, os, random, string, secrets, time
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
DATA.mkdir(exist_ok=True)

LEADS = DATA / "leads.jsonl"
FOLLOWUPS = DATA / "followups.jsonl"
EVENTS = DATA / "events.jsonl"
TEMPLATES = DATA / "templates.json"

app = FastAPI(title="Lead Response Bot", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Lead(BaseModel):
    name: str
    email: str
    company: str | None = None
    phone: str | None = None
    source: str = "landing"
    interest: str | None = None
    consent: bool = True

class Followup(BaseModel):
    lead_email: str
    channel: str
    subject: str
    body: str
    delay_minutes: int = 60
    send_at: str | None = None

def _append_jsonl(path: Path, row: dict):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")

def _read_jsonl(path: Path, limit: int = 50):
    if not path.exists():
        return []
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows[-limit:]

def _ensure_templates():
    if not TEMPLATES.exists():
        defaults = {
            "welcome": {
                "subject": "Thanks, {name} — replying now",
                "body": "Hi {name},\n\nThanks for reaching out from {company}. I'm replying personally within the next few minutes.\n\nIf this is urgent: {phone_here}\n\nBest,\n{Sender}"
            },
            "followup_1": {
                "subject": "Quick next step, {name}",
                "body": "Hi {name},\n\nChecking in — last message got buried. Do you still want to talk this week?\n\nReply and I’ll send 3 focused options.\n\nBest,\n{Sender}"
            },
            "followup_2": {
                "subject": "Last check-in, {name}",
                "body": "Hi {name},\n\nI don't want to keep emailing if this isn't a fit. If you're still interested, pick one:\n\n- 15 min call\n- async video\n- pricing doc\n\nIf not, no reply needed.\n\nBest,\n{Sender}"
            }
        }
        TEMPLATES.write_text(json.dumps(defaults, indent=2), encoding="utf-8")

_ensure_templates()

@app.get("/health")
async def health():
    return {"ok": True, "ts": datetime.now(timezone.utc).isoformat()}

@app.post("/api/lead")
async def create_lead(lead: Lead):
    row = lead.model_dump()
    row["received_at"] = datetime.now(timezone.utc).isoformat()
    row["lead_id"] = f"L-{int(time.time())}-{''.join(random.choices(string.ascii_lowercase, k=4))}"
    row["first_reply_at"] = None
    row["revenue_impact"] = {
        "est_value": None,
        "probability": None,
        "expected_value": None,
        "status": "new"
    }
    _append_jsonl(LEADS, row)
    _append_jsonl(EVENTS, {"ts": row["received_at"], "event": "lead_received", "lead_id": row["lead_id"]})
    send_welcome(row)
    return {"ok": True, "lead_id": row["lead_id"], "first_reply_seconds": 0}

@app.get("/api/lead")
async def list_leads(limit: int = 50, source: str | None = None):
    rows = _read_jsonl(LEADS, limit)
    if source:
        rows = [r for r in rows if r.get("source") == source]
    return {"count": len(rows), "latest": rows}

@app.post("/api/followup")
async def create_followup(f: Followup):
    row = f.model_dump()
    row["created_at"] = datetime.now(timezone.utc).isoformat()
    row["followup_id"] = f"F-{int(time.time())}-{''.join(random.choices(string.ascii_uppercase, k=4))}"
    row["sent_at"] = None
    row["opened_at"] = None
    row["replied_at"] = None
    _append_jsonl(FOLLOWUPS, row)
    _append_jsonl(EVENTS, {"ts": row["created_at"], "event": "followup_queued", "lead_id": row["lead_email"], "followup_id": row["followup_id"]})
    return {"ok": True, "followup_id": row["followup_id"]}

@app.get("/api/followup")
async def list_followups(limit: int = 50):
    return {"count": len(_read_jsonl(FOLLOWUPS, limit)), "latest": _read_jsonl(FOLLOWUPS, limit)}

@app.get("/api/revenue")
async def revenue_report():
    rows = _read_jsonl(LEADS, 200)
    total_leads = len(rows)
    with_value = [r for r in rows if r.get("revenue_impact", {}).get("est_value")]
    total_est = sum(float(r["revenue_impact"].get("est_value", 0) or 0) for r in with_value)
    avg_response_seconds = 0.0
    response_times = []
    for r in rows:
        if r.get("first_reply_at") and r.get("received_at"):
            try:
                a = datetime.fromisoformat(r["received_at"].replace("Z", "+00:00"))
                b = datetime.fromisoformat(r["first_reply_at"].replace("Z", "+00:00"))
                sec = (b - a).total_seconds()
                response_times.append(sec)
            except Exception:
                pass
    avg_response_seconds = round(sum(response_times) / len(response_times), 1) if response_times else 0.0
    return {
        "total_leads": total_leads,
        "leads_with_value": len(with_value),
        "total_estimated_value": round(total_est, 2),
        "avg_response_seconds": avg_response_seconds,
        "threshold_seconds": 60,
        "over_threshold": sum(1 for s in response_times if s > 60)
    }

@app.get("/api/templates")
async def templates():
    if TEMPLATES.exists():
        return json.loads(TEMPLATES.read_text(encoding="utf-8"))
    return {}

@app.post("/api/templates/{key}")
async def update_template(key: str, payload: dict):
    current = {}
    if TEMPLATES.exists():
        current = json.loads(TEMPLATES.read_text(encoding="utf-8"))
    current[key] = payload
    TEMPLATES.write_text(json.dumps(current, indent=2), encoding="utf-8")
    return {"ok": True, "key": key}

_CHECKOUT = DATA / "checkouts.jsonl"

class CheckoutCreate(BaseModel):
    lead_email: str
    item: str
    price_id: str | None = None
    payment_link: str | None = None
    success_url: str | None = None
    cancel_url: str | None = None

@app.post("/api/checkout")
async def create_checkout(payload: CheckoutCreate):
    row = payload.model_dump()
    row["created_at"] = datetime.now(timezone.utc).isoformat()
    row["checkout_id"] = f"CO-{int(time.time())}"
    row["status"] = "pending"
    _append_jsonl(_CHECKOUT, row)
    _append_jsonl(EVENTS, {"ts": row["created_at"], "event": "checkout_created", "lead_id": row["lead_email"], "checkout_id": row["checkout_id"]})
    return {"ok": True, "checkout_id": row["checkout_id"], "status": row["status"]}

@app.get("/api/checkout")
async def list_checkouts(limit: int = 20):
    rows = _read_jsonl(_CHECKOUT, limit)
    return {"count": len(rows), "latest": rows}

@app.post("/webhook/{source}")
async def generic_webhook(source: str, request: Request):
    body = await request.json()
    _append_jsonl(EVENTS, {"ts": datetime.now(timezone.utc).isoformat(), "event": f"webhook_{source}", "body": body})
    return {"ok": True}

def send_welcome(lead: dict):
    lead["first_reply_at"] = datetime.now(timezone.utc).isoformat()
    _append_jsonl(EVENTS, {"ts": lead["first_reply_at"], "event": "reply_sent", "lead_id": lead["lead_id"], "channel": "email"})
