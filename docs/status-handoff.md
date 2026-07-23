# Status Handoff — ReplyPilot v0.3.7+
Date: 2026-07-23
Live site: https://browser-agent-steel.vercel.app

## Working
- Vercel deploy live
- /health green
- Gumroad products create and links resolving
- Outreach templates + prospecting CLI ready
- Automation cron scheduled every hour
- / root serves landing with live Buy links when Accept: text/html

## Needs Human Action
- Railway: replace token with token from Railway account tokens page
- Fly: replace token with output of `fly tokens create`
- LinkedIn: provide OAuth access token or enable approved product access
- HN/Reddit/X/LinkedIn: enable corresponding CLI auth for scheduled publishing
- Payment webhooks: add Gumroad webhook secret to `.env` if you want event ingestion

## Reproducible Verification
- curl https://browser-agent-steel.vercel.app/health should return HTTP 200
- curl -H 'Accept: text/html' https://browser-agent-steel.vercel.app should return HTML with Gumroad links
- scripts/outreach_manager.py draft hn jane_doe should save a prospect record
