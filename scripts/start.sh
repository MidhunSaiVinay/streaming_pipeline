#!/usr/bin/env bash
set -euo pipefail

echo "➡️  Starting Kafka & ZooKeeper…"
docker compose up -d zookeeper kafka

echo "⏳ Waiting for Kafka to be ready…"
# Try listing topics until broker responds
for i in {1..30}; do
  if docker compose exec -T kafka kafka-topics --bootstrap-server kafka:9092 --list >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

echo "📌 Creating topic (idempotent)…"
docker compose exec -T kafka kafka-topics \
  --bootstrap-server kafka:9092 \
  --create --if-not-exists --topic user_events \
  --replication-factor 1 --partitions 1

echo "✅ Kafka is up and topic ready."
