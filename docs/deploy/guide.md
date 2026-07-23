# Deploy ReplyPilot

## Railway
1. Push this repo to GitHub.
2. Create new Railway project.
3. Connect repo; Railway detects Dockerfile automatically.
4. Set env vars from `.env.example`.
5. Deploy.

## Vercel
Frontend landing only. API requires Railway/Render/Fly.

```bash
vercel --prod
```

## Render
1. New Web Service.
2. Build: `docker build -t replypilot .`
3. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Fly.io
```bash
fly launch
fly deploy
```

## Docker Compose (self-hosted)
```bash
docker compose up
```
