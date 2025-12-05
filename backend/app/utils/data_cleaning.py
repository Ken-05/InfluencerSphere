"""
data_cleaning.py
----------------
Contains helper functions for sanitizing, standardizing, and performing
low-level transformations on raw input data before it is persisted or used
by the ML agents.
"""
import re
from typing import Union, List, Dict, Any


def normalize_text(text: str) -> str:
    """
    Performs standard text cleaning: lowercase, removes extra whitespace,
    and removes common non-alphanumeric characters (keeps spaces and dots).
    """
    text = text.lower()
    # Remove emojis and certain symbols (keeping basic punctuation)
    text = re.sub(r'[^\w\s\.\,\!\?]', '', text, flags=re.UNICODE)
    # Standardize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def safe_float_conversion(value: Any, default: float = 0.0) -> float:
    """
    Attempts to convert a value to a float, returning a default value on failure.
    Prevents crashes when parsing numerical metrics from raw data.
    """
    if isinstance(value, (int, float)):
        return float(value)
    try:
        # Tries to remove commas if present
        if isinstance(value, str):
            value = value.replace(',', '')
        return float(value)
    except (ValueError, TypeError):
        return default


def standardize_niche_label(label: str) -> str:
    """
    Converts a machine-generated niche label into a standardized, display-ready format.
    (e.g., 'home_fitness' -> 'Home Fitness').
    """
    if not label:
        return "Unclassified"

    label = label.replace('_', ' ').title()
    return label


def clean_influencer_profile(raw_profile: Dict[str, Any]) -> Dict[str, Any]:
    """
    Applies various cleaning functions to a raw influencer profile dictionary.
    """
    cleaned_profile = raw_profile.copy()

    # Clean and convert follower count
    cleaned_profile['follower_count'] = safe_float_conversion(
        cleaned_profile.get('follower_count')
    )

    # Clean and normalize bio text
    if 'bio' in cleaned_profile:
        cleaned_profile['bio'] = normalize_text(cleaned_profile['bio'])

    # Standardize the niche label if present
    if 'niche_label' in cleaned_profile:
        cleaned_profile['niche_label'] = standardize_niche_label(cleaned_profile['niche_label'])

    return cleaned_profile