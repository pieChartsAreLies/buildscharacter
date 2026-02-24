"""Health endpoint for Uptime Kuma monitoring."""

from fastapi import FastAPI

app = FastAPI(title="Hobson Agent", version="0.1.0")


@app.get("/health")
async def health():
    return {"status": "ok", "agent": "hobson", "version": "0.1.0"}
