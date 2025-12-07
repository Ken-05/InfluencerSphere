from typing import Dict, Any, List
from functools import lru_cache

from ..ml_agents.niche_profiler_agent import NicheProfilerAgent
from ..ml_agents.content_visual_agent import ContentVisualAgent
from ..ml_agents.engagement_agent import EngagementAgent
from ..ml_agents.recommendation_agent import RecommendationAgent
from ..ml_agents.feature_orchestrator import FeatureOrchestrator


class MLPredictionService:
    """
    Orchestrates feature extraction and calls the Engagement (PLEP) and
    Recommendation (Ranking) Agents. This class is the core business logic
    for all real-time ML inference requests from the API.
    """

    def __init__(self):
        # Initialize all agents and the orchestrator.
        # This ensures model artifacts are loaded only ONCE upon service startup.
        print("Initializing MLPredictionService and loading all ML Agents...")
        self.niche_agent = NicheProfilerAgent()
        self.visual_agent = ContentVisualAgent()
        self.engagement_agent = EngagementAgent()
        self.recommendation_agent = RecommendationAgent()

        self.orchestrator = FeatureOrchestrator(
            niche_agent=self.niche_agent,
            visual_agent=self.visual_agent
        )
        print("ML Agents initialization complete.")

    def get_post_plep_prediction(
            self,
            influencer_profile: Dict[str, Any],
            caption: str,
            image_path: str,
            is_video: bool = False
    ) -> Dict[str, Any]:
        """
        Calculates the Post-Level Engagement Potential (PLEP) and diagnostics
        for a single, new piece of content.

        Args:
            influencer_profile: Historical and aggregated metrics of the creator.
            caption: Text content of the post.
            image_path: Local path to the content file (mocked/downloaded).

        Returns:
            Dictionary containing prediction score and detailed feature diagnostics.
        """
        # Orchestrate the full feature vector
        full_feature_vector = self.orchestrator.create_post_feature_vector(
            influencer_profile,
            caption,
            image_path,
            is_video
        )

        # Get the PLEP Prediction (Agent 3)
        plep_score = self.engagement_agent.predict(full_feature_vector)

        # Get Diagnostics for the Creator Dashboard
        plep_diagnostics = self.engagement_agent.get_diagnostics(full_feature_vector)

        return {
            "predicted_plep_percent": plep_score,
            "plep_diagnostics": plep_diagnostics,
            "feature_vector_size": len(full_feature_vector),
        }

    def get_influencer_market_ranking(
            self,
            influencer_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculates the Market Value Ranking and strategic recommendations for an
        influencer based on their historical profile.

        Args:
            influencer_profile: Aggregated profile features from Firestore.

        Returns:
            Dictionary containing the rank, market tier, and strategic report.
        """
        # Orchestrate the profile vector for Agent 4 (mostly historical data)
        # Assuming the niche label is already calculated and available in the profile
        profile_vector = self.orchestrator.create_influencer_profile_vector(
            historical_data=influencer_profile,
            current_niche_label=influencer_profile.get('Niche_Label', 'Unknown')
        )

        # Get the Market Rank Prediction (Agent 4)
        rank_result = self.recommendation_agent.predict(profile_vector)

        # Get Strategic Diagnostics for the Brand/Creator Dashboard
        strategic_report = self.recommendation_agent.get_diagnostics(profile_vector)

        return {
            "ranking": rank_result,
            "strategic_report": strategic_report
        }

    def get_feature_agent_diagnostics(self, influencer_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gathers diagnostic insights directly from the feature extraction agents.
        """
        # This gathers the reports on the Niche and Visual features themselves
        return self.orchestrator.get_influencer_diagnostics(influencer_profile)


# Dependency Injection for Singleton Service
@lru_cache()
def get_ml_prediction_service() -> MLPredictionService:
    """Dependency for FastAPI to get a singleton instance of the service."""
    return MLPredictionService()