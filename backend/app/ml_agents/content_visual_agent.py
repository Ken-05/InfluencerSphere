import numpy as np
import os
import joblib
from typing import Dict, Any
from ..utils.image_utils import mock_image_path_to_array  # Import the utility created above

# Mock imports for CV dependencies
# import cv2 # OpenCV for image loading/processing
# import torch # For CLIP/CNN models
# from PIL import Image # For image manipulation

# Define the absolute path to the project's root directory for model loading
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
MODEL_DIR = os.path.join(PROJECT_ROOT, 'models')


class ContentVisualAgent:
    """
    Agent 2: Extracts visual and multimodal features (Image Quality, Embeddings)
    from a post image/video frame using pre-trained CV models.
    """
    # This agent typically uses pre-trained visual models (not joblib), but using joblib
    # to mock the loading of a simple feature extraction pipe/scaler.
    MODEL_FILENAME = 'content_visual_model_artifact.joblib'
    MOCK_FEATURE_SIZE = 128  # The size of the simulated CLIP/CNN embedding vector

    def __init__(self):
        self.model = self._load_model()
        self.is_ready = self.model is not None

    def _load_model(self) -> Any:
        """Simulates loading a visual pipeline scaler or metadata file."""
        # Loads a tokenizer, preprocessor, or pipeline metadata
        model_path = os.path.join(MODEL_DIR, self.MODEL_FILENAME)
        if not os.path.exists(model_path):
            print(f"WARNING: Model artifact not found at {model_path}. Agent will run in mock mode.")
            return None
        try:
            # Assuming a mock model file exists here for consistency
            # If not, the agent just runs the feature extraction logic directly on the array
            model = joblib.load(model_path)
            print(f"SUCCESS: Agent 2 ({self.MODEL_FILENAME}) loaded.")
            return model
        except Exception as e:
            print(f"ERROR loading model {self.MODEL_FILENAME}: {e}. Running in mock mode.")
            return None

    def _extract_low_level_features(self, image_array: np.ndarray) -> Dict[str, float]:
        """
        Uses OpenCV/Numpy operations (simulated by array operations) to extract
        low-level features like brightness, contrast, and basic edge detection scores.
        """
        # Mock calculation of simple features
        height, width, _ = image_array.shape
        # Convert to float for calculation
        image_float = image_array.astype(np.float32) / 255.0

        avg_brightness = np.mean(image_float)
        contrast_score = np.std(image_float)

        return {
            'Image_Aspect_Ratio': width / height,
            'Image_Brightness': round(avg_brightness, 4),
            'Image_Contrast': round(contrast_score, 4),
            'Image_Sharpness_Score': round(0.5 + contrast_score, 4)  # Mock: higher contrast = higher sharpness
        }

    def _extract_deep_features(self, image_array: np.ndarray, caption: str) -> np.ndarray:
        """
        Simulates the output of a high-dimensional model like CLIP (for multimodal) or a CNN (for object classification).
        This provides the dense feature embedding for the PLEP model.
        """
        if self.is_ready:
            # Placeholder for actual model inference, Preprocessing (e.g., resize using cv2, normalize)
            # CLIP/CNN Model forward pass: model.predict(preprocessed_image)
            pass

        # Mocking the output: a dense, 128-dimensional feature vector, deterministically
        np.random.seed(hash(image_array.tobytes()) % (2 ** 32 - 1))
        # Deep features are typically normalized
        return np.random.rand(self.MOCK_FEATURE_SIZE).astype(np.float32)

    def extract_features(self, image_path: str, caption: str, is_video: bool = False) -> Dict[str, Any]:
        """
        Extracts visual features from the image/video frame path.
        """
        if is_video:
            ###### Later: call mock_video_frame_capture
            return self._extract_mock_features(is_video=True)

        try:
            # Image loading via mock utility
            image_array = mock_image_path_to_array(image_path)

            # Low-level features
            low_level_features = self._extract_low_level_features(image_array)

            # Deep features (Embeddings)
            deep_embedding = self._extract_deep_features(image_array, caption)

            # Combine all features
            feature_dict = low_level_features
            # Convert the deep embedding array into labeled features (Deep_Feature_0, Deep_Feature_1, ...)
            for i, val in enumerate(deep_embedding):
                feature_dict[f'Clip_Feature_{i}'] = float(val)

            feature_dict['is_video_post'] = int(is_video)
            return feature_dict

        except Exception as e:
            print(f"Error during ContentVisualAgent feature extraction: {e}")
            return self._extract_mock_features(is_video=is_video)

    def _extract_mock_features(self, is_video: bool) -> Dict[str, Any]:
        """Returns safe mock features on failure or for video posts."""
        feature_dict = {
            'Image_Aspect_Ratio': 1.0,
            'Image_Brightness': 0.5,
            'Image_Contrast': 0.5,
            'Image_Sharpness_Score': 0.5,
            'is_video_post': int(is_video)
        }
        # Add mock deep features
        for i in range(self.MOCK_FEATURE_SIZE):
            feature_dict[f'Clip_Feature_{i}'] = 0.0

        return feature_dict

    def predict(self, input_features: Dict[str, Any]) -> Any:
        """Agent 2 is purely for feature extraction."""
        return "Visual Features Extracted"

    def get_diagnostics(self, input_features: Dict[str, Any]) -> Dict[str, Any]:
        """Returns diagnostic information on the visual quality."""
        sharpness = input_features.get('Image_Sharpness_Score', 0)
        return {
            "Visual_Quality": "High" if sharpness > 0.7 else "Standard",
            "Contrast_Indicator": "Good" if input_features.get('Image_Contrast', 0) > 0.4 else "Low",
            "Key_Visual_Input": "CLIP/CNN Embeddings Calculated"
        }