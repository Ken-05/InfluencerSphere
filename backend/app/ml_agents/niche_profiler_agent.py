import re
import os
import joblib
from typing import Dict, Any, List
# Mock imports for NLP dependencies
# from transformers import AutoTokenizer, AutoModel

# Define the absolute path to the project's root directory for model loading
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
MODEL_DIR = os.path.join(PROJECT_ROOT, 'models')

class NicheProfilerAgent:
    """
    Agent 1: Extracts text-based features (Niche, Sentiment, Readability)
    from a post caption for real-time feature orchestration.

    Loads a pre-trained text classification/feature extraction model.
    """
    MODEL_FILENAME = 'niche_classifier_model.joblib'

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
            print(f"SUCCESS: Agent 1 ({self.MODEL_FILENAME}) loaded.")
            return model
        except Exception as e:
            print(f"ERROR loading model {self.MODEL_FILENAME}: {e}. Running in mock mode.")
            return None

    def _mock_text_pipeline(self, caption: str) -> Dict[str, Any]:
        """Simulates the full NLP pipeline execution, including model inference."""
        # Initial Feature Engineering
        caption_len = len(caption)
        hashtag_count = len(re.findall(r'#\w+', caption))

        # NLP Model Inference (Simulated)
        if self.is_ready:
            # Assume the model provides a dense feature vector of size 10
            mock_input = [caption] ##### Later: pre-processed input features
            niche_score = self.model.predict(mock_input)[0] * 10
            sentiment_score = 0.5 + (niche_score / 20) # Mock derivative
        else:
            # Mock values when the model artifact is missing
            niche_score = 7.0 + (caption_len % 10)
            sentiment_score = 0.6

        # Niche Classification (Simulated Categorical Output)
        if 'food' in caption.lower() or 'recipe' in caption.lower():
            niche_label = 'Minimalist Cooking'
        elif 'workout' in caption.lower() or 'fitness' in caption.lower():
            niche_label = 'Home Fitness'
        else:
            niche_label = 'Lifestyle'

        # Returns the core features needed for the downstream models
        return {
            'Niche_Label': niche_label,
            'Niche_Score': niche_score,
            'Sentiment_Score': sentiment_score,
            'Caption_Length': caption_len,
            'Hashtag_Count': hashtag_count,
            'Readability_Score': 0.85 # Mock output
        }

    def extract_features(self, caption: str) -> Dict[str, Any]:
        """
        Extracts complex, text-based features from the influencer's caption.
        Used by the Feature Orchestrator.
        """
        try:
            return self._mock_text_pipeline(caption)
        except Exception as e:
            print(f"Error during NicheProfiler feature extraction: {e}")
            return {
                'Niche_Label': 'Unknown',
                'Niche_Score': 5.0,
                'Sentiment_Score': 0.5,
                'Caption_Length': 0,
                'Hashtag_Count': 0,
                'Readability_Score': 0.5
            }

    def predict(self, input_features: Dict[str, Any]) -> Any:
        """Agent 1 is a feature extractor; its direct prediction is the Niche Label."""
        return input_features.get('Niche_Label', 'Unknown')

    def get_diagnostics(self, input_features: Dict[str, Any]) -> Dict[str, Any]:
        """Returns diagnostic information on the content's niche and text features."""
        return {
            "Niche_Identified": input_features.get('Niche_Label', 'Unknown'),
            "Sentiment_Level": "High Positive" if input_features.get('Sentiment_Score', 0) > 0.75 else "Neutral/Mixed",
            "Text_Density_Indicator": "Concise" if input_features.get('Caption_Length', 0) < 150 else "Dense"
        }