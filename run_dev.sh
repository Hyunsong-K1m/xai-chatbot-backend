#!/usr/bin/env bash
set -e
source .venv/bin/activate
export $(grep -v '^#' .env 2>/dev/null | xargs || true)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
