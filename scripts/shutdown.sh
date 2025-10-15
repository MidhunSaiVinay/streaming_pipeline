#!/usr/bin/env bash
set -euo pipefail

CLEAN="${1:-}"

echo "⏹️  Stopping and removing containers…"
docker compose down -v --remove-orphans

if [[ "$CLEAN" == "--clean" ]]; then
  echo "🗑️  Removing local data/checkpoints…"
  rm -rf ./datalake ./checkpoints
fi

echo "✅ Shutdown complete."
