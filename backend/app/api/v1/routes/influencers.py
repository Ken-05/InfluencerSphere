"""
influencers.py
--------------
Defines endpoints for retrieving and managing individual influencer profiles.
- GET /influencers/{influencer_id}: Retrieves a full profile.
- PUT /influencers/{influencer_id}: Updates a profile (e.g., manual corrections).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional

from ....services.influencer_service import InfluencerService
from ....api import deps

router = APIRouter()

# --- Pydantic Schemas for Request/Response ---

class InfluencerProfile(BaseModel):
    """Full detailed profile of an influencer."""
    platform_id: str = Field(..., description="Unique ID of the influencer (e.g., Instagram user ID).")
    username: str = Field(..., description="Platform username.")
    platform: str
    niche_tags: List[str] = Field(default_factory=list, description="ML-derived niche tags.")
    follower_count: int
    engagement_rate: float
    market_score: float
    last_updated: str = Field(..., description="Timestamp of the last data sync.")

class ProfileUpdate(BaseModel):
    """Schema for updating specific fields in a profile."""
    niche_tags: Optional[List[str]] = None
    manual_notes: Optional[str] = None

# --- Dependencies Mock (in deps.py) ---

# get_influencer_svc() in deps.py is the actual
def get_influencer_service_mock() -> InfluencerService:
    # Mock implementation of the InfluencerService methods
    class MockInfluencerService:
        async def get_profile(self, influencer_id: str, user_id: str) -> Optional[dict]:
            # Mock data based on the ID (hard)
            if influencer_id == "mock_user_1":
                return InfluencerProfile(
                    platform_id="mock_user_1",
                    username="MockUser1",
                    platform="TikTok",
                    niche_tags=["Gaming", "Comedy"],
                    follower_count=500000,
                    engagement_rate=4.5,
                    market_score=85.2,
                    last_updated="2024-10-27T10:00:00Z"
                ).model_dump()
            return None

        async def update_profile(self, influencer_id: str, user_id: str, update_data: dict) -> bool:
            return True # Mock success

    return MockInfluencerService()


# --- Endpoints ---

@router.get("/influencers/{influencer_id}", response_model=InfluencerProfile, status_code=status.HTTP_200_OK)
async def get_influencer_profile(
    influencer_id: str,
    # Using the dependency from deps.py now (get_influencer_svc was defined there)
    svc: InfluencerService = Depends(deps.get_influencer_svc),
    user_id: str = Depends(deps.get_current_user_id)
):
    """
    Retrieves the detailed profile and metrics for a single influencer.
    """
    profile_data = await svc.get_profile(influencer_id, user_id)

    if not profile_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Influencer profile '{influencer_id}' not found."
        )

    return InfluencerProfile(**profile_data)

@router.put("/influencers/{influencer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_influencer_profile(
    influencer_id: str,
    update: ProfileUpdate,
    svc: InfluencerService = Depends(deps.get_influencer_svc),
    user_id: str = Depends(deps.get_current_user_id)
):
    """
    Updates specific, mutable fields (like niche tags or manual notes) on an influencer profile.
    """
    try:
        success = await svc.update_profile(influencer_id, user_id, update.model_dump(exclude_unset=True))
        if not success:
             raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Influencer profile '{influencer_id}' not found for update."
            )
        return
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile update failed: {e.__class__.__name__}"
        )