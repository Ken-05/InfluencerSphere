"""
main.py
-------
The main entry point for the FastAPI application.
Initializes core settings, configures logging, includes API routers,
and sets up application lifespan events (startup/shutdown).
"""
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .core.config import get_settings
from .core.logging_config import configure_logging
from .api.v1.router import api_router
from .services.firestore_service import get_firestore_service  # Ensure DB is initialized early
from .services.scheduler import get_scheduler, BackgroundScheduler  # For background tasks

# Load settings immediately
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown events.
    Handles configuration, service initialization, and cleanup.
    """
    print("--- APPLICATION STARTUP ---")

    # Configure Logging
    configure_logging(log_level="INFO")

    # Initialize Core Services (Ensures singletons are created)
    db_service = get_firestore_service()
    print(f"INFO: Firestore Service initialized for user: {db_service.current_user_id}")

    # Start Background Scheduler for Alerts
    scheduler: BackgroundScheduler = get_scheduler()
    scheduler.start()

    print("--- STARTUP COMPLETE ---")
    yield

    # --- SHUTDOWN ---
    print("--- APPLICATION SHUTDOWN ---")

    # Stop Background Scheduler gracefully
    scheduler.shutdown()

    print("--- SHUTDOWN COMPLETE ---")


app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    version="1.0.0",
    lifespan=lifespan  # startup, shutdown logic
)

# --- MIDDLEWARE ---
# Configure CORS to allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API ROUTERS ---
# Include the aggregated v1 API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", include_in_schema=False)
async def root():
    """
    Root endpoint for health check and simple version display.
    """
    return {
        "message": f"{settings.APP_NAME} API is running.",
        "version": app.version,
        "api_docs": "/docs"
    }

# NOTE on Dependencies: The `lifespan` function guarantees that services
# (like `get_firestore_service()`) are initialized before any request is processed.