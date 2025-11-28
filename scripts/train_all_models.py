"""
scripts/train_all_models.py
"""

import os
import sys
import time
import shutil
from typing import Dict, Any

# Adjust path to enable imports from backend modules
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
sys.path.append(PROJECT_ROOT)

from backend.app.ml_agents.niche_profiler_agent import NicheProfilerAgent
from backend.app.ml_agents.content_visual_agent import ContentVisualAgent
from backend.app.ml_agents.engagement_agent import EngagementAgent
from backend.app.ml_agents.recommendation_agent import RecommendationAgent

# Configuration paths
MODEL_SAVE_PATH = os.path.join(PROJECT_ROOT, 'models')
os.makedirs(MODEL_SAVE_PATH, exist_ok=True)

# MAPPING: Agent Name -> The exact filename Agent class expects
ARTIFACT_MAPPING = {
    "NicheProfilerAgent": "niche_classifier_model.joblib",
    "ContentVisualAgent": "content_visual_model_artifact.joblib",
    "EngagementAgent": "engagement_predictor_model.joblib",
    "RecommendationAgent": "market_ranker_model.joblib"
}

def mock_train_model(agent_name: str, training_data_path: str) -> Dict[str, Any]:
    """
    Simulates the full training process for a given ML Agent.
    """
    print(f"--- Starting Training for {agent_name} ---")
    print(f"Loading data from: {training_data_path}...")
    time.sleep(1.0) # Simulate time taken to load data

    # Generate a timestamped version first (good practice for versioning)
    timestamp = time.strftime('%Y%m%d%H%M%S')
    versioned_filename = f"{agent_name}_v{timestamp}.joblib"
    versioned_path = os.path.join(MODEL_SAVE_PATH, versioned_filename)

    # Simulate saving the model artifact
    print(f"Training complete. Model metrics: {{'loss': 0.05, 'accuracy': 0.92}}")
    with open(versioned_path, 'w') as f:
        f.write(f"Mock artifact for {agent_name} trained on {time.ctime()}")

    # Create the 'Latest' copy that the Agents will actually load
    target_filename = ARTIFACT_MAPPING.get(agent_name)
    if target_filename:
        target_path = os.path.join(MODEL_SAVE_PATH, target_filename)
        shutil.copy(versioned_path, target_path)
        print(f" Updated production artifact: {target_filename}")

    return {
        "agent_name": agent_name,
        "status": "SUCCESS",
        "model_path": target_path,
        "timestamp": time.time()
    }

def main():
    """Orchestrates the training of all machine learning models."""
    print("==============================================")
    print("InfluencerSphere: Full Model Training Run")
    print("==============================================")

    DATA_ROOT = os.path.join(PROJECT_ROOT, 'data', 'processed')

    results = []

    # 1. Niche Profiler Agent
    results.append(mock_train_model(
        "NicheProfilerAgent",
        os.path.join(DATA_ROOT, 'niche_supplement_data.csv')
    ))

    # 2. Content Visual Agent
    results.append(mock_train_model(
        "ContentVisualAgent",
        os.path.join(DATA_ROOT, 'plep_train_data.csv')
    ))

    # 3. Engagement Agent (PLEP)
    results.append(mock_train_model(
        "EngagementAgent",
        os.path.join(DATA_ROOT, 'plep_train_data.csv')
    ))

    # 4. Recommendation Agent (Ranking)
    results.append(mock_train_model(
        "RecommendationAgent",
        os.path.join(DATA_ROOT, 'ranking_data.csv')
    ))

    print("\n==============================================")
    print("ALL MODEL TRAINING COMPLETE")
    print("==============================================")
    for res in results:
        print(f"- {res['agent_name']}: Ready at {os.path.basename(res['model_path'])}")

if __name__ == '__main__':
    main()