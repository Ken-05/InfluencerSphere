"""
populate_db.py
"""
import os
import sys
import pandas as pd
import asyncio
from typing import Dict, Any, List

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
sys.path.append(PROJECT_ROOT)

from backend.app.services.data_ingestion_service import get_data_ingestion_service
from backend.app.services.firestore_service import get_firestore_service

DATA_ROOT = os.path.join(PROJECT_ROOT, 'data', 'processed')
RANKING_DATA_PATH = os.path.join(DATA_ROOT, 'ranking_data.csv')

def load_data() -> List[Dict[str, Any]]:
    print("Loading data for population...")
    try:
        df = pd.read_csv(RANKING_DATA_PATH)
        # Rename cols to match schema
        df = df.rename(columns={
            'username': 'username',
            'Followers': 'follower_count',
            'engagement_rate_60d': 'engagement_rate',
            'market_influence_score': 'market_score'
        })
        # Take top 20 for demo
        profiles = df[['username', 'follower_count', 'engagement_rate', 'market_score']].head(20).to_dict('records')

        for p in profiles:
            p['platform'] = "Instagram"
            p['niche_tags'] = ["General"] # Will be updated by NicheAgent during ingestion

        return profiles
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return []

async def main():
    print("==============================================")
    print("InfluencerSphere: Populating Firestore DB")
    print("==============================================")

    ingestion_service = get_data_ingestion_service()
    # Initialize DB (singleton)
    get_firestore_service()

    profiles = load_data()
    for i, p in enumerate(profiles):
        print(f"[{i+1}/{len(profiles)}] Ingesting {p['username']}...")
        try:
            # This triggers the full pipeline: Validation -> Niche Agent -> Firestore
            await ingestion_service.process_raw_influencer_data(p)
        except Exception as e:
            print(f"  -> Failed: {e}")

    print("DB POPULATION COMPLETE")

if __name__ == '__main__':
    asyncio.run(main())