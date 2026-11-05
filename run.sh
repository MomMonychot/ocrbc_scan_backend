#!/bin/bash
set -e

# Load environment variables from .env if present
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

HOST="${HOST:-${host:-127.0.0.1}}"
PORT="${PORT:-${port:-8003}}"
echo "Starting District OCR FastAPI backend on http://${HOST}:${PORT}..."

if command -v uv &> /dev/null; then
  exec uv run uvicorn app.main:app --host "${HOST}" --port "${PORT}" --reload
elif [ -d ".venv" ]; then
  source .venv/bin/activate
  exec uvicorn app.main:app --host "${HOST}" --port "${PORT}" --reload
else
  exec uvicorn app.main:app --host "${HOST}" --port "${PORT}" --reload
fi

