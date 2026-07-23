from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from datetime import datetime, timezone
import json, os, random, string, secrets, time
from pathlib import Path
from urllib.parse import urlencode
from http.client import HTTPSConnection

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
DATA.mkdir(exist_ok=True)

def _load_project_env() -> None:
    env_path = BASE / ".env"
    if not env_path.exists():
        return
    try:
        text = env_path.read_text(encoding="utf-8")
    except Exception:
        return
    env_map: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key:
            env_map[key] = value

    def resolve(value: str) -> str:
        out = value
        changed = True
        while changed:
            changed = False
            for k, v in env_map.items():
                placeholder = f"${{{k}}}"
                if placeholder in out and v:
                    out = out.replace(placeholder, v)
                    changed = True
            if "$" not in out:
                break
        return out

    for key, value in env_map.items():
        if key not in os.environ:
            os.environ[key] = resolve(value)

_load_project_env()
logger = __import__("logging").getLogger("uvicorn.error")
logger.info("Loaded browser-agent env PAYMENT_PROVIDER=%s BASE_URL=%s", os.getenv("PAYMENT_PROVIDER", ""), os.getenv("BASE_URL", ""))

LEADS = DATA / "leads.jsonl"
FOLLOWUPS = DATA / "followups.jsonl"
EVENTS = DATA / "events.jsonl"
TEMPLATES = DATA / "templates.json"
CHECKOUTS = DATA / "checkouts.jsonl"

APP_HOST = os.getenv("HOST", "0.0.0.0")
APP_PORT = int(os.getenv("PORT", "8788"))
BASE_URL = os.getenv("BASE_URL", "").rstrip("/")
PAYMENT_PROVIDER = os.getenv("PAYMENT_PROVIDER", "stripe").lower()
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID", "")
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET", "")
PAYPAL_MODE = os.getenv("PAYPAL_MODE", "sandbox").lower()

app = FastAPI(title="Lead Response Bot", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root(request: Request):
    accept = (request.headers.get("accept") or "").lower()
    path = BASE / "landing" / "index.html"
    if "text/html" in accept and path.exists():
        return HTMLResponse(path.read_text(encoding="utf-8"))
    return {"ok": True, "app": "ReplyPilot", "health": "/health", "docs": "/docs", "repo": "https://github.com/Brighton-Lyrax/browser-agent"}


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
                "body": "Hi {name},\n\nChecking in — last message got buried. Do you still want to talk this week?\n\nReply and I’ll send 3 focused options.\n\n{payment_here}\n\nBest,\n{Sender}"
            },
            "followup_2": {
                "subject": "Last check-in, {name}",
                "body": "Hi {name},\n\nI don't want to keep emailing if this isn't a fit. If you're still interested, pick one:\n\n- 15 min call\n- async video\n- pricing doc\n\nIf not, no reply needed.\n\n{payment_here}\n\nBest,\n{Sender}"
            },
            "purchase_confirm": {
                "subject": "Purchase confirmed, {name}",
                "body": "Hi {name},\n\nYour purchase is confirmed. We're preparing access now.\n\nDM to expedite onboarding.\n\nBest,\n{Sender}"
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

class CheckoutCreate(BaseModel):
    lead_email: str
    item: str = "lead-response"
    price_id: str | None = None
    payment_link: str | None = None
    success_url: str | None = None
    cancel_url: str | None = None


ITEM_LINKS: dict[str, str] = {}
for _item_key, _env_key in [
    ("hobby", "GUMROAD_HOBBY_LINK"),
    ("pro", "GUMROAD_PRO_LINK"),
    ("agency", "GUMROAD_AGENCY_LINK"),
    ("lead-response", "GUMROAD_CHECKOUT_LINK"),
]:
    _val = os.getenv(_env_key, "").strip()
    if _val:
        ITEM_LINKS[_item_key] = _val


def _normal_base_url(lead_email: str) -> str:
    candidate = BASE_URL
    if candidate:
        return candidate
    return f"http://{APP_HOST}:{APP_PORT}"

def _default_success_url(lead_email: str) -> str:
    return f"{_normal_base_url(lead_email)}/checkout/thanks?session_id={{CHECKOUT_SESSION_ID}}"

def _default_cancel_url(lead_email: str) -> str:
    return f"{_normal_base_url(lead_email)}/?canceled=1"

@app.post("/api/checkout")
async def create_checkout(payload: CheckoutCreate):
    row = payload.model_dump()
    row["created_at"] = datetime.now(timezone.utc).isoformat()
    row["checkout_id"] = f"CO-{int(time.time())}"
    row["status"] = "pending"

    if PAYMENT_PROVIDER == "paypal" and PAYPAL_CLIENT_ID and PAYPAL_SECRET:
        base = "https://api-m.paypal.com" if PAYPAL_MODE == "live" else "https://api-m.sandbox.paypal.com"
        success_url = (payload.success_url or "").strip() or _default_success_url(payload.lead_email)
        cancel_url = (payload.cancel_url or "").strip() or _default_cancel_url(payload.lead_email)

        auth = None
        order_id = None
        order_url = None
        err_text = None
        try:
            # Get bearer token
            token_payload = urlencode({"grant_type": "client_credentials"}).encode("utf-8")
            token_req = HTTPSConnection("api-m.sandbox.paypal.com" if PAYPAL_MODE != "live" else "api-m.paypal.com", 443, timeout=20)
            token_req.request(
                "POST",
                "/v1/oauth2/token",
                token_payload,
                {
                    "Authorization": f"Basic {__import__('base64').b64encode(f'{PAYPAL_CLIENT_ID}:{PAYPAL_SECRET}'.encode()).decode()}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )
            token_resp = token_req.getresponse()
            token_raw = token_resp.read().decode("utf-8")
            token_req.close()
            token_data = json.loads(token_raw)
            auth = token_data.get("access_token")
            if not auth:
                raise ValueError(f"paypal-token-error: {token_raw[:300]}")

            # Create order
            order_body = {
                "intent": "CAPTURE",
                "purchase_units": [
                    {
                        "reference_id": payload.lead_email,
                        "amount": {
                            "currency_code": "USD",
                            "value": "20.00",
                        },
                    }
                ],
                "application_context": {
                    "return_url": success_url,
                    "cancel_url": cancel_url,
                    "user_action": "PAY_NOW",
                },
            }
            order_payload = json.dumps(order_body).encode("utf-8")
            api_host = "api-m.paypal.com" if PAYPAL_MODE == "live" else "api-m.sandbox.paypal.com"
            order_req = HTTPSConnection(api_host, 443, timeout=20)
            order_req.request(
                "POST",
                "/v2/checkout/orders",
                order_payload,
                {
                    "Authorization": f"Bearer {auth}",
                    "Content-Type": "application/json",
                },
            )
            order_resp = order_req.getresponse()
            order_raw = order_resp.read().decode("utf-8")
            order_req.close()
            order_data = json.loads(order_raw)
            order_id = order_data.get("id")
            approve_link = None
            for link in order_data.get("links", []):
                if link.get("rel") == "approve":
                    approve_link = link.get("href")
                    break
            order_url = approve_link
            row["status"] = "redirect"
        except Exception as err:
            order_id = None
            order_url = None
            row["status"] = "error"
            err_text = str(err)

        row["provider_session_id"] = order_id
        row["provider_payment_link"] = None
        row["session_url"] = order_url
        if err_text:
            row["error"] = err_text[:500]
    elif ITEM_LINKS:
        item_code = (payload.item or "lead-response").strip().lower()
        provider_payment_link = ITEM_LINKS.get(item_code) or ITEM_LINKS.get("lead-response")
        if provider_payment_link:
            row["status"] = "redirect"
            row["provider_payment_link"] = provider_payment_link
            row["session_url"] = None
            row["provider_session_id"] = None
    if row.get("status") == "pending":
        row["status"] = "unconfigured"

    _append_jsonl(CHECKOUTS, row)
    _append_jsonl(EVENTS, {"ts": row["created_at"], "event": "checkout_created", "lead_id": row["lead_email"], "checkout_id": row["checkout_id"]})
    out = {"ok": True, "checkout_id": row["checkout_id"], "status": row["status"], "provider": PAYMENT_PROVIDER}
    if row.get("session_url"):
        out["session_url"] = row["session_url"]
    if row.get("provider_payment_link"):
        out["payment_link"] = row["provider_payment_link"]
    if row.get("error"):
        out["error"] = row["error"]
    return JSONResponse(out)

@app.get("/checkout/thanks")
async def checkout_thanks(session_id: str | None = None):
    html = """
    <html><body style="font-family:system-ui,sans-serif;padding:2rem;background:#0b0c10;color:#d8dde6">
      <h1>Payment started</h1>
      <p>Session: {session}</p>
      <p>You can close this tab.</p>
    </body></html>
    """
    return HTMLResponse(content=html.replace("{session}", session_id or "unknown"))

@app.post("/webhook/{source}")
async def generic_webhook(source: str, request: Request):
    body = await request.json()
    _append_jsonl(EVENTS, {"ts": datetime.now(timezone.utc).isoformat(), "event": f"webhook_{source}", "body": body})
    return {"ok": True}

def send_welcome(lead: dict):
    lead["first_reply_at"] = datetime.now(timezone.utc).isoformat()
    _append_jsonl(EVENTS, {"ts": lead["first_reply_at"], "event": "reply_sent", "lead_id": lead["lead_id"], "channel": "email"})
