"""
helpers.py
----------
Contains miscellaneous helper functions that do not fit into the core
configuration, security, or specific data cleaning modules.
"""
import math
from typing import Union, Dict, Any, List
import time


def format_large_number(number: Union[int, float]) -> str:
    """
    Formats large numbers into K, M, B format (e.g., 1234567 -> 1.23M).
    Useful for displaying follower counts or engagement scores.
    """
    magnitude = 0
    while abs(number) >= 1000:
        magnitude += 1
        number /= 1000.0

    if magnitude == 0:
        return str(int(number))

    # Use suffixes K, M, B
    suffix = ['', 'K', 'M', 'B', 'T'][magnitude]
    return f"{number:.2f}{suffix}".rstrip('0').rstrip('.')


def calculate_time_since(timestamp: float) -> str:
    """
    Calculates the time elapsed since a given Unix timestamp in a human-readable format.
    """
    diff = time.time() - timestamp
    if diff < 60:
        return f"{int(diff)} seconds ago"
    elif diff < 3600:
        return f"{int(diff // 60)} minutes ago"
    elif diff < 86400:
        return f"{int(diff // 3600)} hours ago"
    else:
        return f"{int(diff // 86400)} days ago"


def safe_dict_get(data: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
    """
    Safely retrieves a value from a nested dictionary using a list of keys.
    Returns the default value if any key in the path does not exist.
    """
    temp = data
    for key in keys:
        if isinstance(temp, dict) and key in temp:
            temp = temp[key]
        else:
            return default
    return temp


