#!/bin/sh
set -e

echo "→ Applying database migrations..."
alembic upgrade head

echo "→ Seeding baseline accounts (idempotent)..."
python -m app.seed

echo "→ Importing cases (idempotent)..."
python -m app.import_cases

echo "→ Starting API on :8000"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
