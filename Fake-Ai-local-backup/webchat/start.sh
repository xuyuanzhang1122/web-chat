#!/bin/bash
# ── Dify AI WebChat Startup Script ──────────────────────────────────────────
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "==> Installing dependencies..."
pip install -r requirements.txt -q

echo "==> Initializing database..."
python -c "from app import init_db; init_db(); print('DB ready.')"

echo "==> Starting server on http://0.0.0.0:${PORT:-5000} ..."
exec python app.py
