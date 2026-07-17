"""
Main FastAPI application factory.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.core.logging import setup_logging, get_logger
from app.services.agent import agent_service
from app.api import sessions, actions, health
import time

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    setup_logging()
    logger.info(
        "app_startup",
        app_name=settings.app_name,
        app_version=settings.app_version,
        debug=settings.debug
    )
    await agent_service.initialize()
    yield
    # Shutdown
    logger.info("app_shutdown")
    await agent_service.cleanup()


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Autonomous browser agent for human-like web automation",
        lifespan=lifespan
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request logging middleware
    @app.middleware("http")
    async def request_logging_middleware(request: Request, call_next):
        """Log all incoming requests."""
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        logger.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            process_time=process_time
        )
        
        return response

    # Include routers
    app.include_router(
        health.router,
        prefix=settings.api_prefix
    )
    app.include_router(
        sessions.router,
        prefix=settings.api_prefix
    )
    app.include_router(
        actions.router,
        prefix=settings.api_prefix
    )

    # Root endpoint
    @app.get("/", tags=["root"])
    async def root():
        """Root endpoint."""
        return {
            "message": f"Welcome to {settings.app_name}",
            "version": settings.app_version,
            "documentation": "/docs",
            "api_prefix": settings.api_prefix
        }

    return app


# Create the application instance
app = create_app()
