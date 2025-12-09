"""
search.py
---------
Defines endpoints for querying, searching, and filtering the influencer database.
- GET /search/influencers: Primary endpoint for dynamic search queries.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import List, Optional

# Relying on InfluencerService for search logic
from ....services.influencer_service import InfluencerService
from ....api import deps
# Import the InfluencerProfile schema for search results
from .influencers import InfluencerProfile

router = APIRouter()

# --- Pydantic Schemas ---

class SearchResult(BaseModel):
    """A paginated list of influencer profiles."""
    count: int = Field(..., description="Total number of results matching the query.")
    page_size: int
    page: int
    results: List[InfluencerProfile] = Field(default_factory=list, description="The list of profiles for the current page.")

# --- Endpoints ---

@router.get("/search/influencers", response_model=SearchResult, status_code=status.HTTP_200_OK)
async def search_influencers(
    q: Optional[str] = Query(None, description="Free text search query (e.g., username, bio keywords)."),
    niche: Optional[str] = Query(None, description="Filter by primary niche tag (e.g., 'Gaming', 'Fitness')."),
    min_engagement: float = Query(0.0, ge=0.0, le=100.0, description="Minimum engagement rate (%)."),
    min_followers: int = Query(0, ge=0, description="Minimum follower count."),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    # DEPENDS ON THE CORRECT SERVICE
    svc: InfluencerService = Depends(deps.get_influencer_svc),
    user_id: str = Depends(deps.get_current_user_id)
):
    """
    Performs a dynamic search and filter query across the influencer database.
    Supports text search, niche filtering, and metric thresholds (followers, score).
    """
    # Map API query parameters to Service method parameters
    search_params = {
        # Note: The underlying service handles free-text (q) filtering in-memory
        "q": q,
        "niche": niche,
        "min_engagement_rate": min_engagement,
        "min_followers": min_followers,
        # Pagination is handled by the service using limit/offset
        "limit": limit,
        "page": page
    }

    try:
        # The service returns the final, sorted, and paginated list
        all_results = await svc.search_and_filter_influencers(search_params)

        # Since the service returns the full list (sorted and limited),
        # we can mock a total count for demonstration purposes.
        # Later: return the total count before pagination.
        total_mock_count = len(all_results) * 2 # Mocking a larger total

        # Apply in-memory pagination to match the simple service implementation
        start_index = (page - 1) * limit
        paginated_results = all_results[start_index:start_index + limit]

        return SearchResult(
            count=total_mock_count,
            page_size=limit,
            page=page,
            results=paginated_results
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search operation failed: {e.__class__.__name__}"
        )