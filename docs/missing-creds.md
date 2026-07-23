# Missing Channel Credentials — Exact Format Needed

Provide each once; keep secrets out of chat if possible. Use repo secrets for production.

## Twitter/X (Optional for read/search)
- TWITTER_BEARER_TOKEN : Bearer token from developer portal
- For posting: TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET

## LinkedIn (Optional for posting)
- LINKEDIN_ACCESS_TOKEN : OAuth access token with w_member_social or openid profile email scopes
- Client id/secret alone are not enough unless Marketing Developer Platform product is approved

## Reddit (Optional for posting)
- REDDIT_CLIENT_ID
- REDDIT_CLIENT_SECRET
- REDDIT_USER_AGENT : descriptive string, e.g. "replypilot/0.1 by Brighton-Lyrax"
- REDDIT_USERNAME + REDDIT_PASSWORD : only if posting as user

## Hacker News (Optional for posting)
- HN_COOKIE : session cookie value from browser after login
- Or HN_ACCOUNT + HN_PASSWORD for basic auth

## Telegram (Optional for delivery/bot)
- TELEGRAM_BOT_TOKEN : from @BotFather
- TELEGRAM_CHAT_ID : group/channel target

## Discord (Optional)
- DISCORD_BOT_TOKEN
- DISCORD_GUILD_ID + DISCORD_CHANNEL_ID

## Gumroad webhooks (Optional)
- GUMROAD_WEBHOOK_SECRET : random string for signature verification
- Set webhook URL to https://browser-agent-steel.vercel.app/webhook/gumroad

## YouTube (Optional)
- YOUTUBE_API_KEY : Data API v3 key
- For uploads: OAuth client + refresh token
