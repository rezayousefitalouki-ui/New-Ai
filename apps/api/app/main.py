from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.health import router as health_router
from app.core.config import get_settings
from app.db.session import engine

@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await engine.dispose()

settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.include_router(health_router)
