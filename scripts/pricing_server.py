"""
Optional pricing server hard-coded with current plan URLs.
Used when live payment keys are unavailable.
"""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="ReplyPilot Pricing")

PLANS = [
    {"id": "hobby", "name": "Hobby", "price": "$29/mo", "url": "https://buy.stripe.com/demo_hobby"},
    {"id": "pro", "name": "Pro", "price": "$149/mo", "url": "https://buy.stripe.com/demo_pro"},
    {"id": "agency", "name": "Agency", "price": "$499/mo", "url": "https://buy.stripe.com/demo_agency"},
]


@app.get("/api/pricing")
async def pricing():
    return JSONResponse({"plans": PLANS})


@app.post("/api/checkout")
async def checkout(request: Request):
    body = await request.json()
    plan_id = body.get("plan_id", "hobby")
    plan = next((p for p in PLANS if p["id"] == plan_id), PLANS[0])
    return JSONResponse({"ok": True, "payment_link": plan["url"], "plan_id": plan_id})
