"""
scripts/data/ingest_public_data.py
"""
import pandas as pd
import numpy as np
import os
import kagglehub
import glob
from sklearn.model_selection import train_test_split
from typing import List

# --- Configuration and Setup ---
# Calculate the project root directory path from the script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))  # Go up two levels from scripts/data/

# Define data directories relative to the project root
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')

# Ensure processed directory exists
os.makedirs(PROCESSED_DIR, exist_ok=True)
print(f"Data will be processed and saved in: {PROCESSED_DIR}")

# Kaggle Dataset IDs
KAGGLE_DATASETS = {
    "plep_data": "propriyam/instagram-data",  # 8k Posts with Likes/Comments
    "niche_supplement": "prithvijaunjale/instagram-images-with-captions",  # 14k Captions/Images
    "ranking_data": "whenamancodes/top-200-influencers-crushing-on-instagram"  # 200 Influencers
}


# --- Utility Functions for Kaggle Loading ---

def find_csv_in_path(path: str) -> str:
    """Finds the first CSV file in the downloaded Kaggle path."""
    # Search recursively for CSV files
    csv_files = glob.glob(os.path.join(path, '**', '*.csv'), recursive=True)
    if not csv_files:
        raise FileNotFoundError(f"No CSV file found in the downloaded path: {path}")

    # Simple heuristic: take the first one found
    print(f"Found CSV file: {os.path.basename(csv_files[0])}")
    return csv_files[0]


def download_and_load(dataset_name: str) -> pd.DataFrame:
    """Downloads a Kaggle dataset and loads the primary CSV file."""
    dataset_id = KAGGLE_DATASETS[dataset_name]
    print(f"\n--- Starting Download: {dataset_id} ---")

    # Download the latest version to a local path (handled by kagglehub caching)
    download_path = kagglehub.dataset_download(dataset_id)
    print(f"Downloaded files located at: {download_path}")

    # Locate the CSV file within the downloaded directory structure
    csv_file_path = find_csv_in_path(download_path)

    # Load the data
    df = pd.read_csv(csv_file_path, low_memory=False)
    print(f"Loaded {len(df)} records for {dataset_name}.")

    return df

def normalize_metric_value(val):
    """
    Convert Instagram-style metric values to integers.
    Handles: 930k, 1.7m, 12.4K, 900, 1,200, 3.2B, etc.
    Returns np.nan for invalid or empty values.
    """
    if pd.isna(val):
        return np.nan

    # Convert to string
    s = str(val).strip().lower()

    # Remove commas
    s = s.replace(",", "")

    # Case 1: Pure numeric digits
    if s.replace('.', '', 1).isdigit():
        return float(s)

    # Case 2: Ends with k/m/b suffix
    multiplier = 1
    if s.endswith("k"):
        multiplier = 1e3
        s = s[:-1]
    elif s.endswith("m"):
        multiplier = 1e6
        s = s[:-1]
    elif s.endswith("b"):
        multiplier = 1e9
        s = s[:-1]

    # If the remaining part is not numeric, return NaN
    try:
        return float(s) * multiplier
    except:
        return np.nan


# --- Cleaning and Feature Engineering Functions ---

def clean_plep_data(df: pd.DataFrame) -> pd.DataFrame:
    """Performs cleaning and feature engineering on the 8k PLEP dataset."""
    print("\n--- Cleaning 8k PLEP Data ---")

    # 1. Drop unnecessary columns
    df = df.drop(columns=['shortcode', 'location', 'multiple_images'], errors='ignore')

    # 2. Rename columns for consistency
    df = df.rename(columns={'owner_username': 'username', 'imageUrl': 'image_url'})

    # 3. Handle missing values
    df = df.dropna(subset=['caption', 'image_url', 'followers', 'likes', 'comments'])

    # 4. Convert data types
    df['is_video'] = df['is_video'].astype(bool)
    # Convert Unix timestamp to datetime object
    df['created_at'] = pd.to_datetime(df['created_at'], unit='s')

    # Data type conversion for engagement calculation
    for col in ['likes', 'comments']:
        # Remove commas, dollar signs, or other non-numeric chars
        df[col] = df[col].str.replace(r'[^\d.-]', '', regex=True)
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 5. Feature Engineering: Create the Target Variable (Engagement Rate)

    # --- Conditional Engagement Rate Calculation based on Follower Tiers ---
    # Define conditions for like and comment weighting
    conditions = [
        (df['followers'] >= 10000),
        (df['followers'] >= 7500) & (df['followers'] < 10000),
        (df['followers'] >= 5000) & (df['followers'] < 7500),
        (df['followers'] >= 2000) & (df['followers'] < 5000),
        (df['followers'] >= 1000) & (df['followers'] < 2000),
    ]
    # Define corresponding like and comment weights
    comment_weights = [8, 7.5, 5, 0.005, 0.0005]
    like_weights = [3, 2.5, 1.5, 0.0005, 0.00005]

    # Initialize a new column for the comment weight for each row
    df['comment_weight'] = np.select(conditions, comment_weights, default=0)  # Default=0 for followers < 1000
    df['like_weight'] = np.select(conditions, like_weights, default=0)  # Default=0 for followers < 1000

    # Calculate weighted engagement rate using the chosen weight
    # If followers < 1000 (weight=0), the calculated ER will be 0
    df['engagement_rate'] = np.where(
        df['followers'] >= 1000,  # Only calculate ER if account is relevant (> 1000 followers)
        ((df['likes'] * df['like_weight'] + df['comments'] * df['comment_weight']) / df['followers']) * 100,
        0.0  # Assign 0.0 for accounts with < 1000 followers (micro-accounts are not target)
    )

    # Drop the temporary columns
    df = df.drop(columns=['comment_weight'])
    df = df.drop(columns=['like_weight'])

    # Clip outliers at 30% (to allow for high engagement with high comment weights)
    df['engagement_rate'] = df['engagement_rate'].clip(upper=30)
    df = df.dropna(subset=['engagement_rate'])

    # 6. Temporal Feature Engineering
    df['hour_of_day'] = df['created_at'].dt.hour
    df['day_of_week'] = df['created_at'].dt.dayofweek  # Monday=0, Sunday=6

    # 7. Basic Content Feature Engineering
    df['caption_length'] = df['caption'].str.len()

    print(f"Cleaned PLEP data shape: {df.shape}")
    return df


def clean_ranking_data(df: pd.DataFrame) -> pd.DataFrame:
    """Performs cleaning on the 200 Influencer Ranking dataset."""
    print("\n--- Cleaning 200 Influencer Ranking Data ---")

    # 1. Rename columns to be consistent and readable
    df = df.rename(columns={
        'Channel Info': 'username',
        'Influence Score': 'market_influence_score',
        'Posts': 'total_posts_count',
        'Avg. Likes': 'account_avg_likes',
        '60-Day Eng Rate': 'engagement_rate_60d'
    })

    # 2. Normalize and correct value types - data types
    # Correct username string values
    df['username'] = df['username'].astype(str).str.replace(r'[\n\r\t]', '', regex=True).str.strip()

    # Normalize the metric values
    for col in ['Total Likes', 'Followers', 'total_posts_count', 'market_influence_score', 'account_avg_likes',
                'engagement_rate_60d', 'New Post Avg. Likes']:
        df[col] = df[col].apply(normalize_metric_value)


    # 3. Drop the original 'rank' as it's often arbitrary, and 'country' for simplicity
    df = df.drop(columns=['Rank', 'Country Or Region'], errors='ignore')
    df = df.dropna(subset=['market_influence_score', 'Followers'])

    print(f"Cleaned Ranking data shape: {df.shape}")
    return df


def process_niche_supplement_data(df: pd.DataFrame) -> pd.DataFrame:
    """Prepares the 14k Niche Supplement data."""
    print("\n--- Processing 14k Niche Supplement Data ---")

    # Rename columns to standard format
    df = df.rename(columns={'Caption': 'caption', 'Image File': 'image_file_name'})
    df = df.dropna(subset=['caption', 'image_file_name'])

    # Will need to add a 'post_id' or 'row_id' later for merging, but for now
    # the raw caption and image file name are sufficient for the Niche Agent.

    print(f"Processed Niche Supplement data shape: {df.shape}")
    return df


# --- Main Execution Block ---

def run_ingestion_pipeline():
    """Executes the full data ingestion, cleaning, and splitting process."""

    # --- Step 1: Download and Load Raw Data ---
    try:
        plep_df = download_and_load("plep_data")
        niche_df = download_and_load("niche_supplement")
        ranking_df = download_and_load("ranking_data")
    except Exception as e:
        print(f"\nFATAL ERROR during data download/loading. Ensure 'kagglehub' is installed and configured.")
        print(f"Error details: {e}")
        return

    # --- Step 2: Clean and Engineer Features ---
    plep_df_cleaned = clean_plep_data(plep_df.copy())
    niche_df_processed = process_niche_supplement_data(niche_df.copy())
    ranking_df_cleaned = clean_ranking_data(ranking_df.copy())

    # --- Step 3: Split PLEP Data for Training/Testing (Core Model) ---

    # Define features (X) and target (y)
    X = plep_df_cleaned.drop(columns=['engagement_rate', 'likes', 'comments'])
    y = plep_df_cleaned['engagement_rate']

    # Stratify by engagement_rate bucket so that the model trains on a balanced distribution of low to high engagement
    # posts so it won’t be biased toward the common ranges, and it balances the outcome of prediction.
    y_bucket = pd.qcut(
        y.astype(float),
        q=10,  # 10 buckets for engagement levels
        duplicates="drop"
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y_bucket
    )

    # Recombine to save the full feature set for the next agent
    train_df = pd.concat([X_train, y_train], axis=1)
    test_df = pd.concat([X_test, y_test], axis=1)

    print(f"\n--- Data Split Summary ---")
    print(f"PLEP Training Set Size: {len(train_df)} records")
    print(f"PLEP Test Set Size: {len(test_df)} records")

    # --- Step 4: Save Processed DataFrames ---

    train_df_path = os.path.join(PROCESSED_DIR, 'plep_train_data.csv')
    test_df_path = os.path.join(PROCESSED_DIR, 'plep_test_data.csv')
    niche_df_path = os.path.join(PROCESSED_DIR, 'niche_supplement_data.csv')
    ranking_df_path = os.path.join(PROCESSED_DIR, 'ranking_data.csv')

    train_df.to_csv(train_df_path, index=False)
    test_df.to_csv(test_df_path, index=False)
    niche_df_processed.to_csv(niche_df_path, index=False)
    ranking_df_cleaned.to_csv(ranking_df_path, index=False)

    print("\n--- Data Ingestion Pipeline Complete ---")
    print(f"All processed data saved to the '{PROCESSED_DIR}' directory.")


if __name__ == '__main__':
    # Execute the data pipeline when the script is run directly.
    run_ingestion_pipeline()