# Privacy Policy
Effective date: 2026-07-23

## Overview
ReplyPilot is built by Brighton-Lyrax. This policy describes how we handle data across the ReplyPilot platform, self-hosted deployments, hosted endpoints, and customer installations.

## Data We Collect
ReplyPilot collects only data required for lead routing, follow-up logging, revenue attribution, and checkout operations. This includes:
- Lead fields entered by users or integrations (`name`, `email`, `company`, `phone`, `interest`)
- Server-side events (`received_at`, `first_reply_at`, `followup_sent_at`, `checkout_created_at`)
- Webhooks from external providers

## Data Storage
Defaults to local JSONL storage on the host filesystem. Hosted deployments store data in encrypted object storage. We do not resell lead data.

## Payments
Payments are processed by the selected provider: Stripe, LemonSqueezy, Polar, Gumroad, or PayPal. We do not store full card numbers on the ReplyPilot backend.

## Security
We follow secure config defaults, CORS restrictions, and least-privilege IAM where applicable. Browser automation integrations should be reviewed by operators before use in regulated environments.

## Retention
Self-hosted operators control retention. Hosted deployments retain lead and event data for up to 12 months unless deleted sooner by request.

## Contact
Email: operators@replypilot.io
