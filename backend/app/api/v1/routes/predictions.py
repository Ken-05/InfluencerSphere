"""
predictions.py
--------------
Defines endpoints related to machine learning inference and the data ingestion pipeline.
- POST /realtime-plep: Triggers Post-Level Engagement Prediction.
- POST /data-ingestion: Submits raw metrics for processing and saving to the database.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List

from ....services.ml_prediction_service import MLPredictionService
from ....services.data_ingestion_service import DataIngestionService
from ....api import deps

router = APIRouter()


# --- Pydantic Schemas for Request/Response ---

class RealtimePredictionRequest(BaseModel):
    """Input schema for triggering real-time PLEP prediction."""
    influencer_id: str = Field(..., description="Unique ID of the target influencer (e.g., platform_username).")
    post_text: str = Field(..., description="The full caption/text of the new post to be analyzed.")
    # For image URL or mock image data path provided for the CV agent
    mock_image_path: str = Field("path/to/mock/image.jpg", description="Mock image path for Content Visual Agent.")


class IngestionDataRequest(BaseModel):
    """Input schema for submitting raw data for ingestion/update."""
    username: str = Field(..., description="Influencer's platform username.")
    platform: str = Field(..., description="Social media platform (e.g., 'Instagram', 'TikTok').")
    follower_count: int = Field(..., ge=1, description="Current follower count.")
    recent_post_captions: List[str] = Field(..., description="List of recent post texts/captions.")
    bio: str = Field("", description="Influencer's current bio.")
    recent_likes: int = Field(0, description="Total likes from recent posts for engagement calculation.")


class RealtimePredictionResponse(BaseModel):
    """Output schema for a prediction result."""
    influencer_id: str
    predicted_engagement: float = Field(..., description="Predicted average engagement rate (%) for the post.")
    market_score: float = Field(..., description="Market Valuation Score (0-100).")
    niche_diagnostics: str = Field(..., description="Summary of niche profiling results.")


# --- Endpoints ---

@router.post("/realtime-plep", response_model=RealtimePredictionResponse, status_code=status.HTTP_200_OK)
async def realtime_prediction(
        request: RealtimePredictionRequest,
        ml_service: MLPredictionService = Depends(deps.get_ml_service),
        user_id: str = Depends(deps.get_current_user_id)  # Ensure user is authenticated
):
    """
    Triggers a real-time ML prediction for a single post on a target influencer.
    Combines PLEP and Market Ranking Agents.
    """
    try:
        # Call the ML Prediction Service to get the combined feature vector and predictions
        results = await ml_service.predict_post_engagement_and_rank(
            influencer_id=request.influencer_id,
            post_text=request.post_text,
            mock_image_path=request.mock_image_path
        )

        return RealtimePredictionResponse(
            influencer_id=request.influencer_id,
            predicted_engagement=results.get('predicted_engagement_rate', 0.0),
            market_score=results.get('market_score', 0.0),
            niche_diagnostics=results.get('niche_summary', 'Niche analysis complete.')
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {e.__class__.__name__}"
        )


@router.post("/data-ingestion", status_code=status.HTTP_202_ACCEPTED)
async def ingest_raw_data(
        raw_data: IngestionDataRequest,
        ingestion_service: DataIngestionService = Depends(deps.get_ingestion_svc),
        user_id: str = Depends(deps.get_current_user_id)  # Ensure authorized service access
):
    """
    Submits raw influencer data to the ingestion pipeline for validation,
    ML enrichment (Niche Profiler), and persistence in Firestore.
    """
    try:
        # The ingestion service handles validation and persistence
        processed_id = await ingestion_service.process_raw_influencer_data(raw_data.model_dump())

        return {
            "message": "Raw data submitted for processing.",
            "status": "Accepted",
            "processed_id": processed_id
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Data ingestion failed: {e.__class__.__name__}"
        )