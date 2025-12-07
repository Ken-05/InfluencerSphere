"""
influencer_service.py
---------------------
Encapsulates all business logic related to influencer data management.
Handles fetching single profiles, executing complex search and filter queries,
and aggregating data for the API endpoints.
"""
from typing import Dict, Any, List, Optional
from functools import lru_cache

from .firestore_service import get_firestore_service, FirestoreService
from ..ml_agents.recommendation_agent import RecommendationAgent  # Used to calculate a derived metric
from ..core.config import get_settings


class InfluencerService:
    """
    Manages the lifecycle and querying of influencer profile data.
    """
    INFLUENCER_COLLECTION = 'influencers'

    def __init__(self, db: FirestoreService):
        self.db = db
        self.settings = get_settings()
        # Initialize the RecommendationAgent to use its ranking/scoring logic
        self.ranking_agent = RecommendationAgent()

    async def get_influencer_profile(self, influencer_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a single influencer profile by their unique ID.
        Influencer profiles are public data.
        """
        try:
            profile = await self.db.get_document(
                collection_name=self.INFLUENCER_COLLECTION,
                doc_id=influencer_id,
                is_private=False  # Public data path
            )
            if profile:
                # Augment the profile with a real-time market score from the agent
                augmented_data = self.ranking_agent.predict(profile)
                profile['market_score'] = augmented_data.get('Market_Value_Score')
                profile['market_tier'] = augmented_data.get('Market_Tier')

            return profile
        except Exception as e:
            print(f"Error fetching influencer profile {influencer_id}: {e}")
            return None

    async def search_and_filter_influencers(self, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Executes a complex search and filter operation on the public influencer data.

        Args:
            query_params: Dictionary containing search criteria (e.g., niche, min_engagement, follower_range).

        Returns:
            A list of filtered and scored influencer profiles.
        """
        print(f"Executing search with parameters: {query_params}")

        # Simulate fetching and then filter in memory for simplicity.

        raw_results = await self.db.get_collection(              # self self.db.get_collection(
            collection_name=self.INFLUENCER_COLLECTION,
            is_private=False
        )

        filtered_results = []
        for profile in raw_results:
            # --- Apply Filters ---

            # Niche Filter (e.g., niche_label = 'Home Fitness')
            niche_filter = query_params.get('niche')
            if niche_filter and profile.get('niche_label') != niche_filter:
                continue

            # Engagement Rate Filter (e.g., min_engagement = 3.0)
            min_engagement = query_params.get('min_engagement_rate')
            if min_engagement and profile.get('average_engagement_rate', 0) < min_engagement:
                continue

            # Follower Range Filter (Follower_Count between min/max)
            min_followers = query_params.get('min_followers', 0)
            max_followers = query_params.get('max_followers', float('inf'))
            follower_count = profile.get('follower_count', 0)
            if not (min_followers <= follower_count <= max_followers):
                continue

            # --- Augment and Score ---

            # Calculate a real-time market score for ranking purposes
            augmented_data = self.ranking_agent.predict(profile)
            profile['market_score'] = augmented_data.get('Market_Value_Score')
            profile['market_tier'] = augmented_data.get('Market_Tier')

            filtered_results.append(profile)

        # Sort by the market score (best matches first)
        sorted_results = sorted(
            filtered_results,
            key=lambda x: x.get('market_score', 0),
            reverse=True
        )

        # Apply limit/pagination if provided in query_params
        limit = query_params.get('limit', self.settings.DEFAULT_SEARCH_LIMIT)
        return sorted_results[:limit]


# Dependency Injection for Singleton Service
@lru_cache()
def get_influencer_service(db: FirestoreService = get_firestore_service()) -> InfluencerService:
    """Dependency for FastAPI to get a singleton instance of the service."""
    return InfluencerService(db)