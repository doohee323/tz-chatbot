#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# Use venv if present (run: python -m venv .venv && .venv/bin/pip install -r requirements.txt)
if [[ -d .venv ]]; then
  source .venv/bin/activate
fi

if [[ ! -f .env ]]; then
  echo "Warning: .env not found. Copy .env.example to .env and set GEMINI_API_KEY, RAG_BACKEND_URL."
fi

export PYTHONPATH="$DIR"
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8088 --reload
