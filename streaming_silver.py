# streaming_silver.py
"""
Bronze -> Silver Pipeline
Aggregate and transform sales data from Bronze table and write to Silver table.
Features: client segmentation, loyalty detection, revenue analytics.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, sum, count, avg, desc, round, when, 
    max, min, countDistinct, current_timestamp
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
BRONZE_PATH = "/tmp/delta/bronze/ventes_stream"
SILVER_AGGREGATES_PATH = "/tmp/delta/silver/ventes_aggreges"
SILVER_COUNTRY_PATH = "/tmp/delta/silver/ventes_par_pays"
SILVER_SEGMENT_PATH = "/tmp/delta/silver/ventes_par_segment"

try:
    # Initialize Spark Session with Delta Lake support
    spark = SparkSession.builder \
        .appName("DeltaSilverLayer") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.driver.memory", "2g") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    logger.info("✅ Spark Session initialized")

    # Read Bronze table
    logger.info(f"Reading Bronze table from: {BRONZE_PATH}")
    df_bronze = spark.read.format("delta").load(BRONZE_PATH)
    logger.info(f"✅ Bronze table loaded: {df_bronze.count()} records")

    # ============================================================
    # AGGREGATION 1: Client-Level Aggregation (by day)
    # ============================================================
    logger.info("Creating client aggregation...")
    df_client_silver = df_bronze.groupBy(
        "client_id", "client_nom", "pays", "segment", "jour"
    ).agg(
        sum("quantite").alias("total_quantite"),
        sum("montant").alias("total_depense"),
        count("*").alias("nb_achats"),
        round(avg("montant"), 2).alias("panier_moyen"),
        min("montant").alias("achat_min"),
        max("montant").alias("achat_max"),
        countDistinct("produit_id").alias("nb_produits_distincts")
    ).withColumn(
        "est_client_fidele", 
        when(col("nb_achats") >= 2, True).otherwise(False)
    ).withColumn(
        "segment_depense",
        when(col("total_depense") >= 500, "Premium")
            .when(col("total_depense") >= 100, "Standard")
            .otherwise("Economy")
    ).withColumn(
        "processing_time", current_timestamp()
    )

    # Write client aggregation to Silver
    logger.info(f"Writing client aggregation to: {SILVER_AGGREGATES_PATH}")
    df_client_silver.write.format("delta") \
        .mode("overwrite") \
        .option("mergeSchema", "true") \
        .save(SILVER_AGGREGATES_PATH)
    logger.info(f"✅ Client aggregation saved: {df_client_silver.count()} records")

    # ============================================================
    # AGGREGATION 2: Country-Level Aggregation
    # ============================================================
    logger.info("Creating country-level aggregation...")
    df_country_silver = df_bronze.groupBy("pays").agg(
        count("*").alias("total_transactions"),
        sum("montant").alias("revenue_total"),
        round(avg("montant"), 2).alias("transaction_moyenne"),
        sum("quantite").alias("items_sold"),
        countDistinct("client_id").alias("unique_customers")
    ).orderBy(desc("revenue_total")).withColumn(
        "processing_time", current_timestamp()
    )

    # Write country aggregation to Silver
    logger.info(f"Writing country aggregation to: {SILVER_COUNTRY_PATH}")
    df_country_silver.write.format("delta") \
        .mode("overwrite") \
        .option("mergeSchema", "true") \
        .save(SILVER_COUNTRY_PATH)
    logger.info(f"✅ Country aggregation saved: {df_country_silver.count()} records")

    # ============================================================
    # AGGREGATION 3: Segment-Level Aggregation
    # ============================================================
    logger.info("Creating segment-level aggregation...")
    df_segment_silver = df_bronze.groupBy("segment").agg(
        count("*").alias("total_transactions"),
        sum("montant").alias("revenue_total"),
        round(avg("montant"), 2).alias("transaction_moyenne"),
        countDistinct("client_id").alias("unique_customers"),
        countDistinct("pays").alias("countries_count")
    ).orderBy(desc("revenue_total")).withColumn(
        "processing_time", current_timestamp()
    )

    # Write segment aggregation to Silver
    logger.info(f"Writing segment aggregation to: {SILVER_SEGMENT_PATH}")
    df_segment_silver.write.format("delta") \
        .mode("overwrite") \
        .option("mergeSchema", "true") \
        .save(SILVER_SEGMENT_PATH)
    logger.info(f"✅ Segment aggregation saved: {df_segment_silver.count()} records")

    # ============================================================
    # DASHBOARD ANALYTICS
    # ============================================================
    logger.info("\\n" + "="*60)
    logger.info("📊 SALES ANALYTICS DASHBOARD")
    logger.info("="*60)

    # Top clients by revenue
    logger.info("\\n🏆 Top 10 Clients by Revenue:")
    top_clients = df_client_silver.orderBy(desc("total_depense")).limit(10)
    top_clients.select(
        "client_nom", "pays", "segment_depense", "total_depense", 
        "nb_achats", "panier_moyen"
    ).show(truncate=False)

    # Revenue by country
    logger.info("\\n🌍 Revenue by Country:")
    df_country_silver.select(
        "pays", "revenue_total", "unique_customers", "total_transactions"
    ).show(truncate=False)

    # Revenue by segment
    logger.info("\\n👥 Revenue by Segment:")
    df_segment_silver.select(
        "segment", "revenue_total", "unique_customers", "transaction_moyenne"
    ).show(truncate=False)

    # Loyalty statistics
    logger.info("\\n💎 Loyalty Statistics:")
    loyalty_stats = df_client_silver.groupBy("est_client_fidele").agg(
        count("*").alias("customer_count"),
        round(sum("total_depense"), 2).alias("total_revenue")
    )
    loyalty_stats.show(truncate=False)

    # Overall metrics
    logger.info("\\n📈 Overall Metrics:")
    logger.info(f"Total Transactions: {df_bronze.count()}")
    logger.info(f"Total Revenue: €{df_bronze.agg(sum('montant')).collect()[0][0]:.2f}")
    logger.info(f"Unique Customers: {df_bronze.select('client_id').distinct().count()}")
    logger.info(f"Countries: {df_bronze.select('pays').distinct().count()}")
    logger.info(f"Average Transaction Value: €{df_bronze.agg(avg('montant')).collect()[0][0]:.2f}")

    logger.info("\\n" + "="*60)
    logger.info("✅ Silver layer processing completed successfully")
    logger.info("="*60)

except Exception as e:
    logger.error(f"❌ Error in Silver layer processing: {e}", exc_info=True)
    raise