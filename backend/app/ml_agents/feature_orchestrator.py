from typing import Dict, Any, Optional
import numpy as np
from .niche_profiler_agent import NicheProfilerAgent
from .content_visual_agent import ContentVisualAgent


class FeatureOrchestrator:
    """
    Combines the feature extraction capabilities of Agent 1 (Niche Profiler)
    and Agent 2 (Content Visual) to create a single, comprehensive feature vector
    in real-time for prediction by Agent 3 (PLEP) and Agent 4 (Ranking).
    """

    def __init__(self, niche_agent: NicheProfilerAgent, visual_agent: ContentVisualAgent):
        """Initializes the orchestrator with instances of the feature agents."""
        self.niche_agent = niche_agent
        self.visual_agent = visual_agent
        print("FeatureOrchestrator initialized with Agent 1 and Agent 2 instances.")

    def create_post_feature_vector(
            self,
            influencer_features: Dict[str, Any],
            caption: str,
            image_path: str,  # This is the local path to the file downloaded pre-orchestration
            is_video: bool = False
    ) -> Dict[str, Any]:
        """
        Generates the full feature vector for a single post prediction (PLEP).

        Args:
            influencer_features: Aggregated, historical features of the influencer (e.g., follower count, growth rate).
            caption: The text content of the post.
            image_path: Local path to the image/frame file.
            is_video: Flag indicating if the post is a video.

        Returns:
            A single dictionary containing all required features for Agent 3 (PLEP).
        """
        # Extract Text/Niche Features (Agent 1)
        text_features = self.niche_agent.extract_features(caption)

        # Extract Visual Features (Agent 2)
        visual_features = self.visual_agent.extract_features(image_path, caption, is_video)

        # Combine Features
        # Start with the influencer's historical features
        full_feature_vector = influencer_features.copy()

        # Merge real-time features
        full_feature_vector.update(text_features)
        full_feature_vector.update(visual_features)

        # Remove non-numerical features before passing to Agent 3
        numerical_vector = {k: v for k, v in full_feature_vector.items() if isinstance(v, (int, float, np.number))}

        return numerical_vector

    def get_influencer_diagnostics(self, influencer_profile_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gathers diagnostic reports from all feature agents for the Creator Dashboard.
        This is a helper to centralize the diagnostic data retrieval.
        """
        # For the ranking agent (Agent 4), the features are primarily aggregated historical metrics
        # The NicheProfiler Agent can provide basic text diagnostics if provided sample content

        # Mock aggregation of feature diagnostics
        niche_diag = self.niche_agent.get_diagnostics(influencer_profile_features)
        visual_diag = self.visual_agent.get_diagnostics(
            influencer_profile_features)  # Using profile features as proxy here

        return {
            "Niche_Diagnostics": niche_diag,
            "Visual_Diagnostics": visual_diag
        }