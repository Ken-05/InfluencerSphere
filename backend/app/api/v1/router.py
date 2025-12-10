"""
router.py
---------
Aggregates all individual route modules (influencers, search, alerts, predictions)
into a single, consolidated FastAPI APIRouter for version 1 of the API.
"""
from fastapi import APIRouter

# Import the modular route files
from .routes import predictions
from .routes import influencers
from .routes import search
from .routes import alerts

api_router = APIRouter()

# Include all modular routers here
api_router.include_router(predictions.router, prefix="", tags=["Predictions & Data Ingestion"])
api_router.include_router(influencers.router, prefix="", tags=["Influencer Profiles"])
api_router.include_router(search.router, prefix="", tags=["Search & Filter"])
api_router.include_router(alerts.router, prefix="", tags=["Alerts Management"])