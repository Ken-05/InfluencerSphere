"""
data_ingestion_service.py
-------------------------
Manages the process of receiving raw data, validating, cleaning, transforming,
and storing it into the appropriate Firestore collections.
This simulates the ETL (Extract, Transform, Load) pipeline for influencer data.
"""
from typing import Dict, Any, List
from functools import lru_cache
import time

from .firestore_service import get_firestore_service, FirestoreService
from ..ml_agents.niche_profiler_agent import NicheProfilerAgent
from ..core.config import get_settings, Settings
from ..utils.decorators import log_calls


class DataIngestionService:
    """
    Handles data flow from external sources (simulated) into the application's
    persisted data model in Firestore.
    """
    INFLUENCER_COLLECTION = 'influencers'
    RAW_DATA_LOG_COLLECTION = 'raw_ingestion_logs'  # Private collection for audit

    def __init__(self, db: FirestoreService, settings: Settings):
        self.db = db
        self.settings = settings
        # The NicheProfilerAgent is used here to transform raw text/image inputs
        # into a categorized Niche Label before persistence.
        self.niche_agent = NicheProfilerAgent()

    async def _validate_raw_data(self, raw_data: Dict[str, Any]) -> bool:
        """
        Performs basic validation on the raw incoming data payload.
        (e.g., checks for mandatory fields like 'username', 'follower_count').
        """
        required_fields = ['username', 'platform', 'follower_count', 'recent_post_captions']
        for field in required_fields:
            if field not in raw_data:
                print(f"VALIDATION ERROR: Missing required field '{field}'")
                return False
        if not isinstance(raw_data.get('recent_post_captions'), list):
            print("VALIDATION ERROR: 'recent_post_captions' must be a list.")
            return False
        return True

    @log_calls
    async def process_raw_influencer_data(self, raw_data: Dict[str, Any]) -> str:
        """
        Takes raw scraped data, validates it, enriches it using ML agents,
        and updates the final influencer profile in the public collection.

        Args:
            raw_data: Dictionary representing the latest scraped data for an influencer.

        Returns:
            The ID of the processed influencer profile.
        """
        if not self._validate_raw_data(raw_data):
            # Log the invalid data but prevent processing
            await self._log_raw_data(raw_data, status="INVALID")
            raise ValueError("Raw data failed validation. See logs for details.")

        # Enrichment: Use ML Agent to categorize the Niche
        print(f"INFO: Running Niche Profiler Agent for {raw_data['username']}...")

        # The niche agent takes the influencer's text inputs (captions/bio)
        niche_label = self.niche_agent.predict(
            influencer_bio=raw_data.get('bio', ''),
            recent_post_texts=raw_data['recent_post_captions']
        )

        # Transformation: Create the final structured document
        # simulate calculation of an average engagement rate based on raw data

        # Calculate a mock average engagement rate (e.g., based on follower count)
        # Later: should involve complex aggregation logic.
        follower_count = raw_data['follower_count']
        mock_engagement_rate = (raw_data.get('recent_likes', 0) / follower_count) * 100 if follower_count > 0 else 0.0

        profile_id = f"{raw_data['platform']}_{raw_data['username']}".lower()

        processed_profile = {
            "id": profile_id,
            "username": raw_data['username'],
            "platform": raw_data['platform'],
            "follower_count": follower_count,
            "average_engagement_rate": round(mock_engagement_rate, 2),
            "niche_label": niche_label,
            "last_updated": time.time(),
            # Copy other cleaned/transformed fields
            "bio_summary": raw_data.get('bio', '').split('\n')[0],
            "historical_data_link": f"/data/{profile_id}/history"  # Link to deeper data ( in Google Cloud Storage)
        }

        # Load: Update the processed profile in the public collection
        await self.db.set_document(
            collection_name=self.INFLUENCER_COLLECTION,
            doc_id=profile_id,
            data=processed_profile,
            is_private=False,  # public influencer database
            merge=True  # Ensure existing profiles is updated
        )

        # Audit: Log the successful ingestion of the raw data (Private log)
        await self._log_raw_data(raw_data, status="SUCCESS", profile_id=profile_id)

        print(f"SUCCESS: Profile {profile_id} ingested and updated.")
        return profile_id

    async def _log_raw_data(self, raw_data: Dict[str, Any], status: str, profile_id: Optional[str] = None):
        """
        Logs the raw incoming data payload and its processing status for audit purposes.
        This data is saved to a private collection under the service user's path.
        """
        log_entry = {
            "timestamp": time.time(),
            "status": status,
            "payload": raw_data,
            "processed_profile_id": profile_id
        }

        # Log data is always stored privately under the service's current_user_id
        await self.db.add_document(
            collection_name=self.RAW_DATA_LOG_COLLECTION,
            data=log_entry,
            is_private=True
        )


# Dependency Injection for Singleton Service
@lru_cache()
def get_data_ingestion_service(
        db: FirestoreService = get_firestore_service(),
        settings: Settings = get_settings()
) -> DataIngestionService:
    """Dependency for FastAPI to get a singleton instance of the service."""
    return DataIngestionService(db, settings)