# Channel Setup Guide

Use this to enable scheduled/automated posting. Provide each item once; never push origin without saying so.

## Twitter/X
Needed:
- TWITTER_BEARER_TOKEN
- Optional: TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
If Bearer-only is enough for read/search, I can enable lightweight posting via OAuth 1.0a user context.

## LinkedIn
Needed:
- LINKEDIN_ACCESS_TOKEN or MARKETING_ACCESS_TOKEN
The client id/secret alone are not enough for posting unless Marketing Developer Platform product is approved.
Provide an OAuth access token with `w_member_social` or `openid profile email` scopes.

## Reddit
Needed:
- REDDIT_CLIENT_ID
- REDDIT_CLIENT_SECRET
- REDDIT_USER_AGENT
- Optional REDDIT_USERNAME + REDDIT_PASSWORD if posting as user

## Hacker News
Needed:
- HN_COOKIE or HN_ACCOUNT
Posting on HN usually needs authenticated session; exact value format: `user=xxx; pass=yyy` or session cookie.

## Telegram
Needed:
- TELEGRAM_BOT_TOKEN
- Channel/group target IDs

## Discord
Needed:
- DISCORD_BOT_TOKEN
- Guild/channel IDs

## Gumroad Webhooks
Needed:
- GUMROAD_WEBHOOK_SECRET
Configure webhook URL to `https://browser-agent-steel.vercel.app/webhook/gumroad`

## YouTube
Needed:
- YOUTUBE_API_KEY
For uploads: OAuth client + refresh token

## Email
Needed:
- SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
Or RESEND_API_KEY

## Instagram/TikTok
Not available yet; these require approved developer access.
