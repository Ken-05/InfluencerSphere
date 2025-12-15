#!/bin/bash
# uvicorn_start.sh
# Starts the FastAPI backend using uvicorn

export ENV_FILE=.env
export DATABASE_URL=${DATABASE_URL:-"sqlite:///./influencers.db"}
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
