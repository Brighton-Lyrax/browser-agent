"""ReplyPilot configuration from environment.

Avoids third-party imports at module load so this works even if runtime
dependencies are not installed yet. Use `load()` in the app.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class EnvConfig:
    stripe_secret: Optional[str] = None
    vercel_token: Optional[str] = None
    gumroad_application_id: Optional[str] = None
    gumroad_secret_key: Optional[str] = None
    gumroad_access_token: Optional[str] = None
    railway_token: Optional[str] = None
    fly_token: Optional[str] = None
    linkedin_client_id: Optional[str] = None
    linkedin_client_secret: Optional[str] = None


def load() -> EnvConfig:
    data = {}
    for key in EnvConfig.__dataclass_fields__:
        val = os.environ.get(key.upper())
        if val is not None:
            data[key] = val
    return EnvConfig(**data)


if __name__ == "__main__":
    cfg = load()
    redacted = {}
    for k, v in cfg.__dict__.items():
        redacted[k] = f"{v[:6]}...***" if isinstance(v, str) and len(v) > 9 else "***"
    print(redacted)
