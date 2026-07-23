# Privacy Scan Report

Generated: 2026-07-23T14:15:03.591791+00:00

## Scope

- `/home/oengakeenlay/browser-agent`
- `/home/oengakeenlay/agentic-app/chat-bot`
- Excluded: `.env` files by directive.

## Scan Summary

| category | finding_count | redacted |
| --- | --- | ---: |
 secrets / tokens / keys | 1 | 1 |
 real names / emails | 2 | 1 |
 chat/agent identifiers | 2 | 2 |
 docs with example credentials | 1 | 1 |
 session logs with identifiers | 2 | 2 |

## Findings

### secrets/tokens/keys

- `/home/oengakeenlay/browser-agent/docs/deploy/README.md`
  - Finding: actual LinkedIn OAuth client secret hardcoded.
  - Action: redacted to `[REDACTED]`.

### real names / emails

- `/home/oengakeenlay/agentic-app/chat-bot/README.md`
  - Finding: literal Telegram credential-style placeholder values.
  - Action: replaced with `___TELEGRAM_BOT_TOKEN___` style placeholders.
- `/home/oengakeenlay/browser-agent/pyproject.toml`, `browser_agent.egg-info/PKG-INFO`, `/home/oengakeenlay/browser-agent/docs/privacy-policy.md`, `/home/oengakeenlay/browser-agent/docs/faq.md`
  - Finding: public support email / identity bundled into metadata and docs.
  - Action: reported here; no redaction performed because these are public identity/metadata fields, not secrets.

### chat/agent identifiers

- `/home/oengakeenlay/agentic-app/chat-bot/sessions/2026-07-21.jsonl`
  - Finding: 15 logged session records include Telegram `user_id` and `username`.
  - Action: in-place redaction of both fields.
- `/home/oengakeenlay/agentic-app/chat-bot/sessions/2026-07-22.jsonl`
  - Finding: 12 logged session records include Telegram `user_id` and `username`.
  - Action: in-place redaction of both fields.

### docs with example credentials

- `/home/oengakeenlay/agentic-app/chat-bot/README.md`
  - Finding: example setup command used fake but credential-like values.
  - Action: redacted to masked placeholder values.

## Actions Taken

1. Modified `/home/oengakeenlay/browser-agent/docs/deploy/README.md`.
2. Modified `/home/oengakeenlay/agentic-app/chat-bot/README.md`.
3. Redacted 2 session log files in-agentic-app/chat-bot/sessions/.

## Residual Risks

- public/identity fields in `pyproject.toml` and related docs retain an operator-facing email and product identity; treat as public metadata, not secret material.
- existing channel webhook logs and Telegram launch consent still contain session-like status fields, but no values identified as sensitive.

## Recommendation

- rotate the exposed LinkedIn client secret.
- replace public identity email with a dedicated support address if the repo becomes public.
- review future .md examples before commit to avoid credential-shaped placeholders.
