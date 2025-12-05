"""
image_utils.py
--------------
Contains utility functions for image preprocessing and manipulation.
Used by ML modules for image quality analysis or ML model input.
"""
import numpy as np
from typing import Any

def mock_image_path_to_array(image_path: str) -> np.ndarray:
    """
    Simulates loading an image from a local path into a NumPy array,
    mimicking the behavior of OpenCV's cv2.imread().

    Args:
        image_path: The local path to the image file (a mock file).

    Returns:
        A deterministic, mock 3D NumPy array (H, W, C) representing the image.
    """
    # Create a deterministic mock array based on the path hash
    # This simulates a successful image load for testing/mocking
    # Returns a 100x100 RGB image array (100, 100, 3)
    np.random.seed(hash(image_path) % (2**32 - 1))
    mock_array = np.random.randint(0, 256, size=(100, 100, 3), dtype=np.uint8)
    return mock_array

def mock_video_frame_capture(video_path: str) -> np.ndarray:
    """
    Simulates capturing a frame from a video file (e.g., using cv2.VideoCapture).
    """
    # Simply delegates to the image mock for consistency in array output
    return mock_image_path_to_array(video_path)