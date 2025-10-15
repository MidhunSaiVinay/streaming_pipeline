import json, time, random, uuid
from datetime import datetime, timezone
from faker import Faker
from confluent_kafka import Producer
import os

bootstrap = os.getenv("KAFKA_BOOTSTRAP","kafka:9092")
topic = os.getenv("KAFKA_TOPIC","user_events")
eps = float(os.getenv("EVENTS_PER_SEC","50"))

p = Producer({"bootstrap.servers": bootstrap})
fake = Faker()
content = [f"m_{i}" for i in range(200)]
devices = ["tv","mobile","web"]
events = ["play","pause","seek","stop","rate"]

def emit():
    e = {
        "event_id": str(uuid.uuid4()),
        "user_id": f"u_{random.randint(1,5000)}",
        "content_id": random.choice(content),
        "event_type": random.choices(events, weights=[50,15,10,20,5])[0],
        "device": random.choice(devices),
        "region": fake.country_code(),
        "ts": datetime.now(timezone.utc).isoformat()
    }
    p.produce(topic, json.dumps(e).encode("utf-8"))
    p.poll(0)

interval = 1.0/eps
while True:
    emit()
    time.sleep(interval)
