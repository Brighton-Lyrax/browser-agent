from __future__ import annotations
import os
from typing import Optional
from .base import ChannelPost

TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID", "")

def missing() -> Optional[str]:
    if not all([TOKEN, CHANNEL_ID]):
        return "DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID"
    return None

def post(post: ChannelPost) -> dict:
    if missing():
        return {"ok": False, "error": f"missing env: {missing()}"}
    try:
        import discord
        import asyncio
        async def send():
            client = discord.Client(intents=discord.Intents.default())
            await client.wait_until_ready()
            channel = client.get_channel(int(CHANNEL_ID))
            if channel is None:
                return {"ok": False, "error": "channel not found"}
            await channel.send(post.content or "")
            await client.close()
            return {"ok": True}
        return asyncio.run(send())
    except Exception as e:
        return {"ok": False, "error": str(e)}
