#!/usr/bin/env bash
set -euo pipefail

MINUTES="${1:-5}"
echo "▶️  Launching producer (background)…"
docker compose run -d --name producer_run --rm producer

echo "🔥 Running Spark job for ${MINUTES} minute(s)…"
docker compose run --rm spark spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 \
  /opt/jobs/spark_stream.py \
  --bootstrap kafka:9092 \
  --topic user_events \
  --out /opt/datalake/events \
  --checkpoint /opt/checkpoints/user_events \
  --minutes "${MINUTES}"

echo "🧹 Stopping producer…"
docker stop producer_run >/dev/null || true

echo "📦 Output written under ./datalake/events (partitioned Parquet)."
