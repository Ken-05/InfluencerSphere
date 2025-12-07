"""
alert_service.py
----------------
Manages logic for creating, evaluating, and triggering user alerts based on
market conditions, influencer metrics, and custom user thresholds.
"""
from typing import Dict, Any, List, Optional
from functools import lru_cache
import time  # for simulating check time

from .firestore_service import get_firestore_service, FirestoreService
from .influencer_service import get_influencer_service, InfluencerService
from ..core.config import get_settings, Settings
from ..utils.decorators import log_calls


class AlertService:
    """
    Handles persistence and evaluation of user-defined alert thresholds.
    Alerts are stored as private data, scoped to the user ID.
    """
    ALERT_COLLECTION = 'user_alerts'

    def __init__(self, db: FirestoreService, settings: Settings, influencer_service: InfluencerService):
        self.db = db
        self.settings = settings
        self.influencer_service = influencer_service
        # This is a mock mechanism for tracking last check time
        self._last_check_time = time.time() - self.settings.ALERT_CHECK_INTERVAL_SECONDS - 60

    async def create_alert(self, user_id: str, alert_data: Dict[str, Any]) -> str:
        """Creates a new private alert document for the authenticated user."""
        if not user_id:
            raise ValueError("User ID must be provided to create a private alert.")

        # Add metadata and save
        alert_data['user_id'] = user_id
        alert_data['created_at'] = time.time()

        # Alerts are stored privately
        doc_id = await self.db.add_document(
            collection_name=self.ALERT_COLLECTION,
            data=alert_data,
            is_private=True
        )
        return doc_id

    async def get_alerts_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Retrieves all active alerts for a specific user."""
        # Note: The FirestoreService handles scoping the query to the user's private path
        try:
            alerts = await self.db.get_collection(
                collection_name=self.ALERT_COLLECTION,
                is_private=True
            )
            return alerts
        except Exception as e:
            print(f"Error fetching alerts for user {user_id}: {e}")
            return []

    async def update_alert(self, alert_id: str, update_data: Dict[str, Any], user_id: str):
        """Updates an existing alert document."""
        # Ensure only the authenticated user can update their private alert
        await self.db.set_document(
            collection_name=self.ALERT_COLLECTION,
            doc_id=alert_id,
            data=update_data,
            is_private=True,
            merge=True
        )

    async def delete_alert(self, alert_id: str, user_id: str):
        """Deletes an alert document."""
        await self.db.delete_document(
            collection_name=self.ALERT_COLLECTION,
            doc_id=alert_id,
            is_private=True
        )

    # --- Core Evaluation Logic ---

    @log_calls
    async def evaluate_all_alerts(self) -> List[Dict[str, Any]]:
        """
        Simulates the scheduled process of checking all active alerts against
        current market data and triggers any matching alerts.
        """
        current_time = time.time()
        if (current_time - self._last_check_time) < self.settings.ALERT_CHECK_INTERVAL_SECONDS:
            print(f"INFO: Skipping alert evaluation. Last run was too recent.")
            return []

        print("INFO: Starting scheduled alert evaluation process.")
        self._last_check_time = current_time
        triggered_alerts = []

        # Fetch relevant market data (Influencer profiles)
        # fetch all influencers to evaluate alerts against
        market_data = await self.influencer_service.search_and_filter_influencers({})
        influencer_map = {p['id']: p for p in market_data}

        # Fetch all unique alerts for all users (in a real system, this would be complex)
        # Since it is mock, retrieve ALL private documents accessible to the service user
        all_alerts = await self.db.get_collection(
            collection_name=self.ALERT_COLLECTION,
            is_private=True  # Since the service runs as an admin/authenticated user, it can see all its own documents
        )

        # Evaluate each alert
        for alert in all_alerts:
            # Initial alert structure example:
            # { "condition_type": "min_engagement_rate", "value": 5.0, "niche": "Home Fitness" }

            condition_type = alert.get("condition_type")
            target_value = alert.get("value")
            target_niche = alert.get("niche")

            if not condition_type or not target_value:
                continue

            for influencer_id, profile in influencer_map.items():

                # Check Niche Match
                if target_niche and profile.get('niche_label') != target_niche:
                    continue

                # Check Condition Match
                is_triggered = False

                if condition_type == "min_engagement_rate" and profile.get('average_engagement_rate',
                                                                           0) >= target_value:
                    is_triggered = True

                elif condition_type == "min_market_score" and profile.get('market_score', 0) >= target_value:
                    is_triggered = True

                # If an influencer matches the alert, record it
                if is_triggered:
                    triggered_alerts.append({
                        "alert_id": alert.get("id"),
                        "user_id": alert.get("user_id"),
                        "message": f"Market alert triggered! Influencer {profile.get('username')} meets your criteria ({condition_type} >= {target_value}).",
                        "triggered_on": profile.get("username"),
                        "profile_link": f"/influencers/{influencer_id}"
                    })
                    # Break after first match per alert rule to avoid redundant triggers
                    break

        print(f"INFO: Alert evaluation complete. Found {len(triggered_alerts)} triggered alerts.")
        return triggered_alerts


# Dependency Injection for Singleton Service
@lru_cache()
def get_alert_service(
        db: FirestoreService = get_firestore_service(),
        settings: Settings = get_settings(),
        influencer_service: InfluencerService = get_influencer_service()
) -> AlertService:
    """Dependency for FastAPI to get a singleton instance of the service."""
    return AlertService(db, settings, influencer_service)