"""
scripts/data/preprocess_images.py
"""
import cv2
import numpy as np
from PIL import Image
from torchvision import transforms
from typing import Tuple, Any

# Define the standard size required by the Content Visual Agent's underlying CNN/CLIP model
TARGET_SIZE = (224, 224)


def resize_image(image_path: str, size: Tuple[int, int] = TARGET_SIZE) -> Image.Image:
    """
    Loads an image using OpenCV, converts color space, and resizes it using PIL.
    This prepares the image for feature extraction in the training pipeline.
    """
    try:
        # Load image using OpenCV (OpenCV is often faster for large batch reads)
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"Image not found at path: {image_path}")

        # Convert BGR (OpenCV default) to RGB (standard for PIL/PyTorch)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Convert to PIL Image for standard resizing
        pil_img = Image.fromarray(img)
        return pil_img.resize(size)
    except Exception as e:
        print(f"Error processing image {image_path} with OpenCV/PIL: {e}")
        # Return a black placeholder image on failure
        return Image.fromarray(np.zeros((*size, 3), dtype=np.uint8))


def normalize_image(image: np.ndarray) -> np.ndarray:
    """Normalizes pixel values of a NumPy array to range [0,1]."""
    return image.astype(np.float32) / 255.0


def load_image_as_tensor(image_path: str) -> Any:
    """
    Loads the image, resizes, and converts it to a normalized PyTorch tensor (C,H,W).
    This output is directly fed into the CNN/CLIP feature extraction models.
    """
    pil_img = resize_image(image_path)

    # Standard normalization for pre-trained models (e.g., ImageNet mean/std)
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])
    # Returns a tensor with shape (1, C, H, W)
    return transform(pil_img).unsqueeze(0)