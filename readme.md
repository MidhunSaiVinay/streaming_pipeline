# 🎬 Local Streaming Data Pipeline (Kafka → PySpark → Parquet)

End-to-end **Netflix-style user events pipeline** you can run on macOS with **Docker Compose** and a few **shell scripts**:

- **Producer** (Python) emits fake play/pause/seek/stop events to Kafka  
- **Spark Structured Streaming** reads from Kafka and writes **Parquet** into a local **datalake/**  
- **Scripts** (`start.sh`, `run.sh`, `shutdown.sh`) bring the stack **up → run for N minutes → down** cleanly

---

## ✨ Features

- Zero cloud, zero cost — fully local
- Reproducible containers (Kafka, ZooKeeper, Spark, Producer)
- Ephemeral runs with **automatic teardown**
- Data lands in `./datalake/events/` (Parquet), state in `./checkpoints/`

---

## 🧱 Architecture

```
[Producer (Python)]  -->  [Kafka]  -->  [Spark Structured Streaming]  -->  [Parquet Lake]
                                   \                                     datalake/events/
                                    \--> checkpoints/ (Spark state)
```

---

## 🧰 Tech Stack

- Docker & Docker Compose
- Kafka + ZooKeeper (Confluent images)
- Spark 3.5.1 (built locally via `spark/Dockerfile`)
- Python 3.11 producer (confluent-kafka, faker)
- Parquet on local filesystem

---

## ✅ Prerequisites

- **Docker Desktop** for Mac
- **Git** and **curl** (usually preinstalled on macOS)
- Terminal: zsh/bash

> Apple Silicon (M1/M2): works; if you later use external images that lack ARM builds, add `platform: linux/amd64` to that service in `docker-compose.yml`.

---

## 📦 Project Structure

```
.
├─ docker-compose.yml
├─ spark/                 # Spark image (local build)
│  └─ Dockerfile
├─ producer/              # Producer image
│  ├─ Dockerfile
│  ├─ requirements.txt
│  └─ app.py
├─ jobs/
│  └─ spark_stream.py     # Spark Structured Streaming job
├─ scripts/
│  ├─ start.sh            # start Kafka/ZK + create topic
│  ├─ run.sh              # run producer + spark for N minutes
│  └─ shutdown.sh         # stop everything; optional --clean
├─ datalake/              # (generated) Parquet output
└─ checkpoints/           # (generated) Spark checkpoints
```

---

## 🚀 Quick Start

From the repo root (where `docker-compose.yml` lives):

```bash
# 1) Build local images (Spark + Producer)
docker compose build

# 2) Start infra (Kafka/ZK) and ensure topic exists
./scripts/start.sh

# 3) Run the pipeline for 5 minutes (change 5 → any number)
./scripts/run.sh 5

# 4) Explore outputs
ls -lah ./datalake/events | head
du -sh ./datalake/events

# 5) Tear down (add --clean to wipe data/checkpoints)
./scripts/shutdown.sh --clean
```

---

## 🧪 Event Schema (Producer)

```json
{
  "event_id": "uuid",
  "user_id": "u_12345",
  "content_id": "m_550",
  "event_type": "play|pause|seek|stop|rate",
  "device": "web|tv|mobile",
  "region": "DE",
  "ts": "2025-10-15T19:22:31Z"
}
```

Events go to Kafka topic **`user_events`**.

---

## 🗂️ Data Locations

- **Parquet output:** `./datalake/events/`  
- **Spark checkpoints:** `./checkpoints/user_events/`

---

## 🧞 Scripts (How They Work)

- `start.sh`  
  - `docker compose up -d zookeeper kafka`  
  - Waits for Kafka  
  - Creates topic `user_events` (idempotent)

- `run.sh <minutes>`  
  - Starts **producer** (detached)  
  - Runs **spark-submit** inside the Spark container for `<minutes>`  
  - Stops producer after Spark exits

- `shutdown.sh [--clean]`  
  - `docker compose down -v --remove-orphans`  
  - If `--clean`, deletes `datalake/` and `checkpoints/`

---

## ⚙️ Configuration

- **Producer rate:** `EVENTS_PER_SEC` env var in `docker-compose.yml` → `producer` service
- **Topic name:** `KAFKA_TOPIC` (default `user_events`)
- **Kafka bootstrap:** `KAFKA_BOOTSTRAP` (container network: `kafka:9092`)

If you need to change output paths, edit arguments passed to `spark_stream.py` in `scripts/run.sh`.

---

## 🧱 Compose Notes

**Spark service** uses a locally built image:

```yaml
spark:
  build: ./spark
  image: spark-local:3.5.1
  user: "0:0"
  environment:
    SPARK_MODE: client
  volumes:
    - ./jobs:/opt/jobs
    - ./datalake:/opt/datalake
    - ./checkpoints:/opt/checkpoints
```

**Important:** The `jobs` folder must contain `spark_stream.py` (path is case-sensitive).  
Spark runs it as: `/opt/jobs/spark_stream.py`.

---

## 🧩 Maven/Firewall Environments (No Internet for JARs)

If your network blocks Maven downloads, pre-bundle the Kafka connector:

```bash
mkdir -p jars
curl -L -o jars/spark-sql-kafka-0-10_2.12-3.5.1.jar \
  https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.5.1/spark-sql-kafka-0-10_2.12-3.5.1.jar
curl -L -o jars/spark-token-provider-kafka-0-10_2.12-3.5.1.jar \
  https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.5.1/spark-token-provider-kafka-0-10_2.12-3.5.1.jar
curl -L -o jars/kafka-clients-3.5.1.jar \
  https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.5.1/kafka-clients-3.5.1.jar
```

Then:
- Mount `./jars:/opt/jars` under the `spark` service in `docker-compose.yml`
- In `scripts/run.sh`, switch `spark-submit` to use `--jars /opt/jars/...` (remove `--packages`)

---

## 🐞 Troubleshooting

**“no configuration file provided: not found”**  
You’re not in the folder with `docker-compose.yml`. `cd` to repo root.

**Compose warns about `version: "3.8"`**  
Remove the `version:` line; Compose v2 ignores it.

**Spark can’t open `/opt/jobs/spark_stream.py`**  
- Ensure the file exists: `test -f jobs/spark_stream.py`  
- Ensure you’re running commands from repo root so `./jobs:/opt/jobs` volume mounts  
- Inspect inside container:  
  `docker compose run --rm spark bash -lc 'ls -lah /opt/jobs'`

**No output in `datalake/events/`**  
- Confirm producer is running: `docker ps | grep producer`  
- Read a few events:  
  `docker compose exec -T kafka kafka-console-consumer --bootstrap-server kafka:9092 --topic user_events --from-beginning --timeout-ms 2000 | head`
- Check Spark logs printed by `run.sh`

**Apple Silicon pull issues**  
Add `platform: linux/amd64` to the problematic service.

---

## 🧽 .gitignore

Create `.gitignore` at repo root:

```
datalake/
checkpoints/
logs/
jars/
__pycache__/
*.pyc
.venv/
.env
.DS_Store
.vscode/
.idea/
```

If already tracked, untrack once:
```bash
git rm -r --cached datalake checkpoints logs jars 2>/dev/null || true
git add .gitignore
git commit -m "Ignore local data/checkpoints/logs/jars"
```



## 🗺️ Roadmap (Optional)

- Add **Airflow** service + DAG to schedule daily ephemeral runs
- Write aggregates to a **warehouse** (DuckDB/Redshift/Snowflake/Synapse)
- Add a **dashboard** (Superset/Power BI/Tableau) over Parquet or warehouse
- Swap local Kafka with **MSK/Event Hubs/Kinesis** for cloud parity


