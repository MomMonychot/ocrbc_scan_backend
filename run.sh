#!/bin/bash
set -e

# Load environment variables from .env if present
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

# Auto-activate local virtual environment (.venv) if present
if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

HOST="${HOST:-${host:-127.0.0.1}}"
PORT="${PORT:-${port:-8003}}"
echo "Starting District OCR FastAPI backend on http://${HOST}:${PORT}..."
uvicorn app.main:app --host "${HOST}" --port "${PORT}" --reload

