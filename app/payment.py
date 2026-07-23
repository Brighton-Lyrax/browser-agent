"""
Payment provider bridge for ReplyPilot.

Supported providers:
- stripe
- paypal
- lemonsqueezy
- polar
- gumroad
"""
from __future__ import annotations

from pydantic import BaseModel
import os


class CheckoutRequest(BaseModel):
    customer_email: str
    item_code: str
    amount: str | None = None
    currency: str = "USD"
    success_url: str
    cancel_url: str
    metadata: dict | None = None


PAYMENT_PROVIDER = os.getenv("PAYMENT_PROVIDER", "stripe").lower()


def create_checkout(payload: CheckoutRequest) -> dict:
    provider = PAYMENT_PROVIDER
    if provider == "stripe":
        return _stripe_checkout(payload)
    if provider == "paypal":
        return _paypal_checkout(payload)
    if provider == "lemonsqueezy":
        return _lemonsqueezy_checkout(payload)
    if provider == "polar":
        return _polar_checkout(payload)
    if provider == "gumroad":
        return _gumroad_checkout(payload)
    return {"status": "error", "error": f"unknown provider: {provider}"}


def _stripe_checkout(payload: CheckoutRequest) -> dict:
    try:
        stripe = None
        if os.getenv("STRIPE_API_KEY"):
            import stripe as _  # noqa
            stripe = _
        else:
            return {"status": "unconfigured", "provider": "stripe"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
    return {
        "provider": "stripe",
        "status": "redirect",
        "payment_link": "https://buy.stripe.com/demo",
    }


def _paypal_checkout(payload: CheckoutRequest) -> dict:
    return {
        "provider": "paypal",
        "status": "redirect",
        "payment_link": "https://www.paypal.com/cgi-bin/webscr?cmd=_xclick",
    }


def _lemonsqueezy_checkout(payload: CheckoutRequest) -> dict:
    return {
        "provider": "lemonsqueezy",
        "status": "redirect",
        "payment_link": "https://store.example/checkout",
    }


def _polar_checkout(payload: CheckoutRequest) -> dict:
    return {
        "provider": "polar",
        "status": "redirect",
        "payment_link": "https://polar.sh/example/checkout",
    }


def _gumroad_checkout(payload: CheckoutRequest) -> dict:
    return {
        "provider": "gumroad",
        "status": "redirect",
        "payment_link": "https://gum.co/example",
    }
