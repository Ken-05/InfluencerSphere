import numpy as np
import pandas as pd
import os
import joblib
from typing import Dict, Any, List

# Define the absolute path to the project's root directory for model loading
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
MODEL_DIR = os.path.join(PROJECT_ROOT, 'models')


class RecommendationAgent:
    """
    Agent 4: Provides the Market Value Ranking and strategic recommendations.
    This model (Market Ranker) analyzes a creator's historical aggregated
    performance (growth, sustained engagement, niche scarcity) to assign a score.
    """
    MODEL_FILENAME = 'market_ranker_model.joblib'

    def __init__(self):
        self.model = self._load_model()
        self.is_ready = self.model is not None

    def _load_model(self) -> Any:
        """Loads the serialized model artifact from the models directory."""
        model_path = os.path.join(MODEL_DIR, self.MODEL_FILENAME)
        if not os.path.exists(model_path):
            print(f"WARNING: Model artifact not found at {model_path}. Agent will run in mock mode.")
            return None
        try:
            model = joblib.load(model_path)
            print(f"SUCCESS: Agent 4 ({self.MODEL_FILENAME}) loaded.")
            return model
        except Exception as e:
            print(f"ERROR loading model {self.MODEL_FILENAME}: {e}. Running in mock mode.")
            return None

    def _convert_features_to_df(self, features: Dict[str, Any]) -> pd.DataFrame:
        """Converts the aggregated feature dictionary into a model input format."""
        # Input features represent an influencer's historical profile, not a single post.
        df = pd.DataFrame([features])
        return df.select_dtypes(include=[np.number])

    def _mock_rank_score(self, features: Dict[str, Any]) -> float:
        """Provides a simple mock rank score based on proxy features."""
        # Assume 'Follower_Growth_Rate' and 'Average_Engagement_Rate' are in the input
        growth_rate = features.get('Follower_Growth_Rate', 0.05)
        avg_engagement = features.get('Average_Engagement_Rate', 3.0)

        # Simple weighted mock calculation
        return (growth_rate * 500) + (avg_engagement * 10) + 40  # Base score of 40

    def predict(self, influencer_profile_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predicts the Market Value Ranking and Estimated Value.
        """
        if not self.is_ready:
            rank_score = self._mock_rank_score(influencer_profile_features)
        else:
            try:
                df_input = self._convert_features_to_df(influencer_profile_features)
                # Prediction is typically a single rank score (0 to 100)
                rank_score = self.model.predict(df_input)[0]
            except Exception as e:
                print(f"Prediction Error in RecommendationAgent: {e}. Falling back to mock prediction.")
                rank_score = self._mock_rank_score(influencer_profile_features)

        # Ensure the score is bounded
        rank_score = float(np.clip(rank_score, 1, 100))

        # Translate score to value tiers (Mock logic for presentation)
        if rank_score >= 90:
            market_tier = "A-List Talent"
            est_value = 5000 + rank_score * 150
        elif rank_score >= 70:
            market_tier = "High-Growth Asset"
            est_value = 2000 + rank_score * 75
        else:
            market_tier = "Scouting Target"
            est_value = 500 + rank_score * 30

        return {
            "Market_Value_Score": round(rank_score, 2),
            "Market_Tier": market_tier,
            "Estimated_Post_Fee_USD": round(est_value, 0)
        }

    def get_diagnostics(self, influencer_profile_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provides strategic diagnostics based on the influencer's historical data (Niche Strategy Reports).
        """
        niche = influencer_profile_features.get('Niche_Label', 'Lifestyle')

        # Mock Niche Saturation Report data
        if niche == 'Minimalist Cooking':
            competition_density = "Low-Medium"
            strategic_pivot = "Expand into Food Photography Tutorials"
        elif niche == 'Home Fitness':
            competition_density = "High"
            strategic_pivot = "Target niche of 40+ Women's Health"
        else:
            competition_density = "Medium"
            strategic_pivot = "Focus on a clear sub-topic within Lifestyle"

        return {
            "Market_Analysis_Type": "Niche Strategy Report",
            "Niche_Focus": niche,
            "Competition_Density": competition_density,
            "Strategic_Recommendation": strategic_pivot,
        }