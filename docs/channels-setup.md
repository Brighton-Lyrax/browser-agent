# Channel Setup Guide

## Automated posting script
`python scripts/channel_poster.py`
- `--list` shows which channels are ready/missing
- `python scripts/channel_poster.py twitter --content "..."` posts to Twitter/X
- `python scripts/channel_poster.py reddit --content "..." --url "..."` posts to Reddit
- `python scripts/channel_poster.py linkedin --content "..."` posts to LinkedIn
- `python scripts/channel_poster.py telegram --content "..."` posts to Telegram
- `python scripts/channel_poster.py discord --content "..."` posts to Discord
- `python scripts/channel_poster.py all --content "..."` attempts all enabled channels

## Required credentials
Add these to your local `.env` file. Do NOT share secrets in chat.

### Twitter/X (for posting)
- TWITTER_BEARER_TOKEN
- TWITTER_API_KEY
- TWITTER_API_SECRET
- TWITTER_ACCESS_TOKEN
- TWITTER_ACCESS_SECRET

Get from: https://developer.twitter.com/en/portal/projects-and-apps

### Reddit (for posting)
- REDDIT_CLIENT_ID
- REDDIT_CLIENT_SECRET
- REDDIT_USER_AGENT : "replypilot/0.1 by Brighton-Lyrax"
- REDDIT_USERNAME
- REDDIT_PASSWORD

Get from: https://www.reddit.com/prefs/apps
Password: use your Reddit account password with an app-specific password if 2FA is enabled.

### LinkedIn (for posting)
- LINKEDIN_ACCESS_TOKEN : OAuth user access token with `w_member_social` or `openid profile email` scopes

Get from: LinkedIn Developer Portal > Your App > Products > Marketing Developer Platform > OAuth 2.0 client credentials > authorize user.

Note: client id/secret alone are not enough unless Marketing Developer Platform product is approved. If not approved, you need Marketing Developer Platform access.

### Telegram (for bot delivery)
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID

Get bot token from @BotFather. Get chat ID by messaging @userinfobot or using `/start` on your bot.

### Discord (for bot delivery)
- DISCORD_BOT_TOKEN
- DISCORD_CHANNEL_ID

Get from Discord Developer Portal > Bot > Token. Channel ID: enable Developer Mode in Discord, right-click channel, Copy ID.

### Hacker News
- No automated posting implemented yet; needs session automation or API access.

## Automation
Once credentials are in `.env`, add your chosen channel(s) to the hourly automation cron.
