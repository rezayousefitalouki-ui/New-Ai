from fastapi import APIRouter, HTTPException
from redis.asyncio import Redis
from sqlalchemy import text
from app.core.config import get_settings
from app.db.session import SessionFactory

router = APIRouter(tags=["health"])

@router.get("/health/live")
async def liveness() -> dict[str, str]:
    return {"status": "ok"}

@router.get("/health/ready")
async def readiness() -> dict[str, str]:
    try:
        async with SessionFactory() as session:
            await session.execute(text("SELECT 1"))
        redis = Redis.from_url(get_settings().redis_url)
        try:
            await redis.ping()
        finally:
            await redis.aclose()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="A required dependency is unavailable") from exc
    return {"status": "ok", "database": "ok", "redis": "ok"}
