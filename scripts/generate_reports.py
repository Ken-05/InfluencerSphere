"""
generate_reports.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
sys.path.append(PROJECT_ROOT)


DATA_ROOT = os.path.join(PROJECT_ROOT, 'data', 'processed')
RANKING_DATA_PATH = os.path.join(DATA_ROOT, 'ranking_data.csv')

try:
    df = pd.read_csv(RANKING_DATA_PATH)
    # Top 10 influencers by score
    top10 = df.sort_values("engagement_score", ascending=False).head(10)
    top10.to_csv("../data/processed/top10_influencers.csv", index=False)

    # Plot engagement distribution
    df['engagement_score'].hist(bins=50)
    plt.title("Engagement Score Distribution")
    plt.savefig("../data/processed/engagement_distribution.png")
    plt.show()
except Exception as e:
    print(f"Error loading CSV: {e}")