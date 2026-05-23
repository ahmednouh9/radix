from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from loguru import logger

from app.config import settings
from app.database import engine, Base
from app.models import PlatformConfig, Campaign, ProcessedComment, Notification
from app.templates_setup import templates


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting SocialAutoReply...")
    Base.metadata.create_all(bind=engine)
    # Add new columns for older databases (safe to run multiple times)
    from sqlalchemy import inspect, text
    inspector = inspect(engine)
    columns = [c["name"] for c in inspector.get_columns("platform_configs")]
    with engine.connect() as conn:
        if "instagram_username" not in columns:
            conn.execute(text("ALTER TABLE platform_configs ADD COLUMN instagram_username VARCHAR(255)"))
            logger.info("Added column: instagram_username")
        if "instagram_password" not in columns:
            conn.execute(text("ALTER TABLE platform_configs ADD COLUMN instagram_password TEXT"))
            logger.info("Added column: instagram_password")
        conn.commit()
    logger.info("Database tables created successfully")
    yield
    logger.info("Shutting down SocialAutoReply...")


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    max_age=86400,
    same_site="lax",
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.app_version}


@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard")


# Import and register routers after app creation to avoid circular imports
def register_routers():
    from app.routers import (
        webhook_instagram,
        webhook_facebook,
        campaigns,
        configs,
        notifications,
        analytics,
        sse,
        auth,
        pages,
    )

    app.include_router(webhook_instagram.router, prefix="/webhook", tags=["Webhooks"])
    app.include_router(webhook_facebook.router, prefix="/webhook", tags=["Webhooks"])
    app.include_router(campaigns.router, prefix="/api/v1", tags=["Campaigns"])
    app.include_router(configs.router, prefix="/api/v1", tags=["Configs"])
    app.include_router(notifications.router, prefix="/api/v1", tags=["Notifications"])
    app.include_router(analytics.router, prefix="/api/v1", tags=["Analytics"])
    app.include_router(sse.router, prefix="/api", tags=["SSE"])
    app.include_router(auth.router, tags=["Auth"])
    app.include_router(pages.router, tags=["Pages"])

    logger.info("All routers registered")


register_routers()
