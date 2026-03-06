"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: initialise DB on startup."""
    logger.info("Starting Memora API…")
    try:
        await init_db()
        logger.info("Database initialised.")
    except Exception as exc:
        logger.error("Database initialisation failed: %s", exc)
    yield
    logger.info("Memora API shutting down.")


app = FastAPI(
    title="Memora API",
    version="1.0.0",
    description="Personal AI Memory System API",
    lifespan=lifespan,
)

# CORS
origins = ["*"] if settings.ENVIRONMENT == "development" else []
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
from app.api.router import router as api_router  # noqa: E402

app.include_router(api_router)


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """Service health check."""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/", tags=["root"])
async def root() -> dict:
    """Root endpoint."""
    return {"message": "Welcome to Memora API", "docs": "/docs"}
