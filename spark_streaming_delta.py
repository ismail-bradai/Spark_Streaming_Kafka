# spark_streaming_delta.py
"""
Spark Structured Streaming Consumer: Kafka -> Delta Lake (Bronze)
Reads from Kafka topic, transforms data, and writes to Delta Lake Bronze table.
Features: watermarking, checkpointing, partitioning, monitoring.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    from_json, col, current_timestamp, substring, 
    to_timestamp, window
)
from pyspark.sql.types import (
    StructType, StructField, IntegerType, StringType, 
    DoubleType, TimestampType
)
import logging
import time

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
KAFKA_BROKERS = "localhost:9092"
KAFKA_TOPIC = "ventes_stream"
BRONZE_PATH = "/tmp/delta/bronze/ventes_stream"
CHECKPOINT_PATH = "/tmp/delta/checkpoints/ventes_bronze"
WATERMARK_DELAY = "10 minutes"  # Handle late-arriving data

# Initialize Spark Session with Delta Lake support
try:
    spark = SparkSession.builder \
        .appName("KafkaToDeltaStreaming") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.driver.memory", "2g") \
        .config("spark.sql.streaming.schemaInference", "true") \
        .config("spark.streaming.kafka.maxRatePerPartition", "1000") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    logger.info("✅ Spark Session initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize Spark: {e}")
    raise

# Define schema for incoming Kafka data
kafka_schema = StructType([
    StructField("vente_id", IntegerType(), True),
    StructField("client_id", IntegerType(), True),
    StructField("produit_id", IntegerType(), True),
    StructField("timestamp", StringType(), True),
    StructField("quantite", IntegerType(), True),
    StructField("montant", DoubleType(), True),
    StructField("client_nom", StringType(), True),
    StructField("produit_nom", StringType(), True),
    StructField("categorie", StringType(), True),
    StructField("pays", StringType(), True),
    StructField("segment", StringType(), True)
])

try:
    # Read from Kafka
    logger.info(f"Connecting to Kafka broker: {KAFKA_BROKERS}")
    df_kafka = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BROKERS) \
        .option("subscribe", KAFKA_TOPIC) \
        .option("startingOffsets", "latest") \
        .option("failOnDataLoss", "false") \
        .load()
    
    logger.info(f"✅ Connected to Kafka topic: {KAFKA_TOPIC}")

    # Parse JSON data
    df_parsed = df_kafka.select(
        from_json(col("value").cast("string"), kafka_schema).alias("data")
    ).select("data.*")

    # Enrich data with ingestion metadata
    df_enriched = df_parsed \
        .withColumn("timestamp_dt", to_timestamp(col("timestamp"))) \
        .withColumn("date_ingestion", current_timestamp()) \
        .withColumn("jour", substring(col("timestamp"), 1, 10)) \
        .select(
            col("vente_id"),
            col("client_id"),
            col("produit_id"),
            col("timestamp_dt").alias("timestamp"),
            col("quantite"),
            col("montant"),
            col("client_nom"),
            col("produit_nom"),
            col("categorie"),
            col("pays"),
            col("segment"),
            col("date_ingestion"),
            col("jour")
        )

    # Apply watermarking to handle late data
    df_watermarked = df_enriched.withWatermark("timestamp", WATERMARK_DELAY)

    # Write to Delta Lake (Bronze Layer)
    logger.info(f"Starting stream write to Delta Lake: {BRONZE_PATH}")
    query = df_watermarked.writeStream \
        .format("delta") \
        .outputMode("append") \
        .option("checkpointLocation", CHECKPOINT_PATH) \
        .partitionBy("jour") \
        .start(BRONZE_PATH)

    logger.info("✅ Streaming started. Writing to Delta Lake Bronze table...")
    logger.info(f"Checkpoint location: {CHECKPOINT_PATH}")
    logger.info(f"Bronze table location: {BRONZE_PATH}")
    logger.info(f"Watermark delay: {WATERMARK_DELAY}")

    # Monitor streaming query progress
    def print_metrics(query):
        """Print streaming metrics periodically"""
        while query.isActive:
            try:
                progress = query.recentProgress
                if progress:
                    latest = progress[-1]
                    input_rows = latest.get("numInputRows", 0)
                    output_rows = latest.get("numOutputRows", 0)
                    latency = latest.get("durationMs", {}).get("addBatch", 0)
                    
                    if input_rows > 0 or output_rows > 0:
                        logger.info(
                            f"📊 Metrics - Input: {input_rows} rows, "
                            f"Output: {output_rows} rows, "
                            f"Latency: {latency}ms"
                        )
                time.sleep(30)  # Update every 30 seconds
            except Exception as e:
                logger.warning(f"Error reading metrics: {e}")
                time.sleep(30)

    # Start metrics thread (optional)
    # import threading
    # metrics_thread = threading.Thread(target=print_metrics, args=(query,), daemon=True)
    # metrics_thread.start()

    # Keep the query running
    query.awaitTermination()

except Exception as e:
    logger.error(f"❌ Streaming pipeline error: {e}", exc_info=True)
    raise