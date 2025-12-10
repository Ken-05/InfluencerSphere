"""
deps.py
-------
Defines common dependency injection functions for FastAPI endpoints.
This includes:
1. Extracting the authenticated user's ID (or mock ID) for service scoping.
2. Providing singleton instances of core services (e.g., FirestoreService).
"""
from typing import Generator, Optional
from fastapi import Header, HTTPException, status
from functools import lru_cache

from ..services.firestore_service import get_firestore_service, FirestoreService
from ..services.ml_prediction_service import get_ml_prediction_service, MLPredictionService
from ..services.influencer_service import get_influencer_service, InfluencerService
from ..services.alert_service import get_alert_service, AlertService
from ..services.data_ingestion_service import get_data_ingestion_service, DataIngestionService


# --- User Authentication Dependency ---

# NOTE: this dependency simulates extracting the validated user ID from the authentication layer
# Later: involve JWT or Firebase token verification

def get_current_user_id() -> str:
    """
    Dependency that returns the authenticated user's ID from the FirestoreService.
    This ID is used to scope private data access (e.g., user alerts).
    """
    db_service = get_firestore_service()
    user_id = db_service.current_user_id

    if not user_id:
        # This should ideally never happen if the service is initialized correctly
        # with an auth token, but acts as a security fallback.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or user ID.",
        )
    return user_id


# --- Service Dependency Injection ---

def get_db() -> FirestoreService:
    """Provides a cached instance of the Firestore Service."""
    return get_firestore_service()


def get_ml_service() -> MLPredictionService:
    """Provides a cached instance of the ML Prediction Service."""
    return get_ml_prediction_service()


def get_influencer_svc() -> InfluencerService:
    """Provides a cached instance of the Influencer Business Service."""
    return get_influencer_service()


def get_alert_svc() -> AlertService:
    """Provides a cached instance of the Alert Business Service."""
    return get_alert_service()


def get_ingestion_svc() -> DataIngestionService:
    """Provides a cached instance of the Data Ingestion Service."""
    return get_data_ingestion_service()