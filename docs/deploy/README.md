# Deploy Guide

Current live endpoint: https://browser-agent-steel.vercel.app

## Vercel (Done)
- Auth: Vercel token with account access
- Status: Deployed and healthy

## Railway (Token Fix Needed)
Likely causes:
- Token must be a Railway project-scoped API token
- It must include deployments access
Create token at https://railway.app/account/tokens and rerun:
  railway login --token $RAILWAY_TOKEN

## Fly (Headless Token Needed)
`fly auth login` needs a non-interactive token. Fix steps:
- Create token: `fly tokens create`
- Write it to `.env` as FLY_TOKEN
- Login: `fly auth login -t "$FLY_TOKEN"`
If login still asks for browser, rerun with headless mode only after creating API token with correct scopes.

## LinkedIn (Auth Pending)
Values provided:
- client id: 77v41k3avdyj26
- client secret: WPL_AP1.3eK4KUMwZOMAydRo.A/y5LQ==
LinkedIn posting requires OAuth user access token or Marketing Developer Platform product approval. Add the token to `.env` as LINKEDIN_ACCESS_TOKEN when available, then enable posting in scripts.

## Gumroad (Live)
- Hobby: https://brightonlyrax.gumroad.com/l/rzafxw
- Pro: https://brightonlyrax.gumroad.com/l/nlqnr
- Agency: https://brightonlyrax.gumroad.com/l/seixck

## Missing Retrospective
- no Product Hunt or HN post executed
- automated cron is scheduled but output remains local-only
- Railway and Fly remain unauthorized

## Next Actions
1. Fix Railway and Fly auth
2. Provide LinkedIn access token
3. Execute outreach using scripts/outreach_manager.py
4. Schedule HN/Reddit/LinkedIn content publication
