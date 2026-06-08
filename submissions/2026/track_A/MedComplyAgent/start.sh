#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required. Install Docker Desktop, start it, then run ./start.sh again."
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "Docker Compose v2 is required. Install or update Docker Desktop, then run ./start.sh again."
  exit 1
fi

if [ ! -f backend/.env ]; then
  cp backend/.env.example backend/.env
  echo "Created backend/.env from backend/.env.example."
  echo "Set LLM_API_KEY in backend/.env if you want AI extraction to call the configured LLM provider."
fi

echo "Starting HEDIS AI Review with Docker Compose..."
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
docker compose up --build
