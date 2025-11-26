"""
scripts/data/utils_data.py

Common helpers used by ingestion/preprocessing scripts:
- safe_read_csv: try multiple encodings and delimiters
- ensure_dirs
- clean caption & extract hashtags
- generate_post_id
"""

import os
import pandas as pd
import re
import uuid
from pathlib import Path
from typing import List, Any

def ensure_dirs(*dirs):
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)

def safe_read_csv(path: str) -> pd.DataFrame:
    """Try reading CSV with common options; returns empty df on failure."""
    for enc in (None, "utf-8", "latin1"):
        for sep in (",", "\t", ";"):
            try:
                return pd.read_csv(path, encoding=enc, sep=sep, low_memory=False)
            except Exception:
                continue
    # last resort: pandas read_csv default (may raise)
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()

def clean_caption(text: Any) -> str:
    """Normalize caption strings: remove urls/mentions, collapse whitespace."""
    if pd.isna(text) or text is None:
        return ""
    s = str(text)
    s = re.sub(r"http\S+", "", s)       # urls
    s = re.sub(r"@\w+", "", s)          # mentions
    s = re.sub(r"#[A-Za-z0-9_]+", "", s) # hashtags removed here because it is also stored
    s = re.sub(r"[^A-Za-z0-9\s\.,!?'\"]+", " ", s)  # remove weird chars
    s = re.sub(r"\s+", " ", s).strip()
    return s

def extract_hashtags(text: Any) -> List[str]:
    """Extract hashtags from text; returns list of lowercased tags without #."""
    if pd.isna(text) or text is None:
        return []
    s = str(text)
    tags = re.findall(r"#([A-Za-z0-9_]+)", s)
    return [t.lower() for t in tags]

def generate_post_id(prefix: str = "p") -> str:
    """Create a stable unique post id."""
    return f"{prefix}_{uuid.uuid4().hex[:12]}"
