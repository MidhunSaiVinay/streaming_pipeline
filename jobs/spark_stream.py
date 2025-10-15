import sys, argparse
from pyspark.sql import SparkSession, functions as F

parser = argparse.ArgumentParser()
parser.add_argument("--bootstrap", default="kafka:9092")
parser.add_argument("--topic", default="user_events")
parser.add_argument("--out", default="/opt/datalake/events")
parser.add_argument("--checkpoint", default="/opt/checkpoints/user_events")
parser.add_argument("--minutes", type=int, default=5)
args = parser.parse_args()

spark = (SparkSession.builder.appName("local-stream")
         .config("spark.sql.shuffle.partitions","2")
         .getOrCreate())

raw = (spark.readStream.format("kafka")
  .option("kafka.bootstrap.servers", args.bootstrap)
  .option("subscribe", args.topic)
  .option("startingOffsets","latest")
  .load())

events = (raw.selectExpr("CAST(value AS STRING) AS json")
  .select(F.from_json("json", """
    event_id STRING, user_id STRING, content_id STRING,
    event_type STRING, device STRING, region STRING, ts STRING
  """).alias("e")).select("e.*")
  .withColumn("event_time", F.to_timestamp("ts")))

query = (events
  .writeStream
  .format("parquet")
  .option("checkpointLocation", args.checkpoint)
  .option("path", args.out)
  .outputMode("append")
  .start())

# Run for N minutes then exit
query.awaitTermination(args.minutes * 60)
