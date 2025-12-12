#!/usr/bin/env python3
"""
Quick Reference and Testing Script
Includes utilities for monitoring and querying the streaming pipeline
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import desc, count, sum as spark_sum, avg as spark_avg
import sys

# Configuration
BRONZE_PATH = "/tmp/delta/bronze/ventes_stream"
SILVER_AGGREGATES_PATH = "/tmp/delta/silver/ventes_aggreges"
SILVER_COUNTRY_PATH = "/tmp/delta/silver/ventes_par_pays"
SILVER_SEGMENT_PATH = "/tmp/delta/silver/ventes_par_segment"

def init_spark():
    """Initialize Spark Session"""
    return SparkSession.builder \
        .appName("QuickReference") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()

def menu():
    """Display interactive menu"""
    print("""
╔════════════════════════════════════════════════════════════╗
║   Streaming Pipeline - Quick Reference Menu               ║
╚════════════════════════════════════════════════════════════╝

1.  View Bronze Table (Raw Data)
2.  View Client Aggregations (Silver)
3.  View Country Revenue (Silver)
4.  View Segment Analysis (Silver)
5.  Count Records in Each Table
6.  Top 5 Clients by Revenue
7.  Revenue Breakdown by Country
8.  Customer Loyalty Report
9.  Latest Records (last 10)
10. Overall Statistics
11. Exit

Select an option (1-11): """)

def view_bronze(spark):
    """View Bronze table"""
    print("\n📦 BRONZE TABLE (Raw Sales Data)\n")
    try:
        df = spark.read.format("delta").load(BRONZE_PATH)
        print(f"Total Records: {df.count()}\n")
        df.show(10, truncate=False)
    except Exception as e:
        print(f"❌ Error: {e}")

def view_client_silver(spark):
    """View Client Aggregations"""
    print("\n👤 CLIENT AGGREGATIONS (Silver)\n")
    try:
        df = spark.read.format("delta").load(SILVER_AGGREGATES_PATH)
        print(f"Total Clients: {df.count()}\n")
        df.show(10, truncate=False)
    except Exception as e:
        print(f"❌ Error: {e}")

def view_country_silver(spark):
    """View Country Revenue"""
    print("\n🌍 REVENUE BY COUNTRY (Silver)\n")
    try:
        df = spark.read.format("delta").load(SILVER_COUNTRY_PATH)
        df.show(truncate=False)
    except Exception as e:
        print(f"❌ Error: {e}")

def view_segment_silver(spark):
    """View Segment Analysis"""
    print("\n👥 REVENUE BY SEGMENT (Silver)\n")
    try:
        df = spark.read.format("delta").load(SILVER_SEGMENT_PATH)
        df.show(truncate=False)
    except Exception as e:
        print(f"❌ Error: {e}")

def count_records(spark):
    """Count records in each table"""
    print("\n📊 RECORD COUNTS\n")
    try:
        tables = {
            "Bronze": BRONZE_PATH,
            "Client Silver": SILVER_AGGREGATES_PATH,
            "Country Silver": SILVER_COUNTRY_PATH,
            "Segment Silver": SILVER_SEGMENT_PATH,
        }
        
        for name, path in tables.items():
            try:
                count = spark.read.format("delta").load(path).count()
                print(f"  {name:20s} : {count:,d} records")
            except:
                print(f"  {name:20s} : [Not available yet]")
    except Exception as e:
        print(f"❌ Error: {e}")

def top_clients(spark):
    """Top 5 clients by revenue"""
    print("\n🏆 TOP 5 CLIENTS BY REVENUE\n")
    try:
        df = spark.read.format("delta").load(SILVER_AGGREGATES_PATH)
        df.select("client_nom", "pays", "segment_depense", "total_depense", "nb_achats") \
            .orderBy(desc("total_depense")) \
            .limit(5) \
            .show(truncate=False)
    except Exception as e:
        print(f"❌ Error: {e}")

def revenue_by_country(spark):
    """Revenue breakdown by country"""
    print("\n💶 REVENUE BREAKDOWN BY COUNTRY\n")
    try:
        df = spark.read.format("delta").load(SILVER_COUNTRY_PATH)
        df.select("pays", "revenue_total", "unique_customers", "total_transactions") \
            .orderBy(desc("revenue_total")) \
            .show(truncate=False)
    except Exception as e:
        print(f"❌ Error: {e}")

def loyalty_report(spark):
    """Customer loyalty report"""
    print("\n💎 CUSTOMER LOYALTY REPORT\n")
    try:
        df = spark.read.format("delta").load(SILVER_AGGREGATES_PATH)
        
        # Loyalty breakdown
        loyalty = df.groupBy("est_client_fidele").agg(
            count("*").alias("customer_count"),
            spark_sum("total_depense").alias("total_revenue"),
            spark_avg("panier_moyen").alias("avg_transaction")
        )
        print("Loyalty Status:")
        loyalty.show(truncate=False)
        
        # Spending segments
        print("\nSpending Segments:")
        segments = df.groupBy("segment_depense").agg(
            count("*").alias("customer_count"),
            spark_sum("total_depense").alias("total_revenue")
        ).orderBy(desc("total_revenue"))
        segments.show(truncate=False)
        
    except Exception as e:
        print(f"❌ Error: {e}")

def latest_records(spark):
    """Show latest 10 records"""
    print("\n⏰ LATEST 10 TRANSACTIONS\n")
    try:
        df = spark.read.format("delta").load(BRONZE_PATH)
        df.orderBy(desc("timestamp")).limit(10).show(truncate=False)
    except Exception as e:
        print(f"❌ Error: {e}")

def statistics(spark):
    """Overall statistics"""
    print("\n📈 OVERALL STATISTICS\n")
    try:
        df = spark.read.format("delta").load(BRONZE_PATH)
        
        stats = df.agg(
            count("*").alias("total_transactions"),
            spark_sum("montant").alias("total_revenue"),
            spark_avg("montant").alias("avg_transaction"),
            spark_sum("quantite").alias("total_items"),
            df.select("client_id").distinct().count()
        )
        
        result = stats.collect()[0]
        print(f"  Total Transactions    : {result[0]:,d}")
        print(f"  Total Revenue         : €{result[1]:,.2f}")
        print(f"  Average Transaction   : €{result[2]:,.2f}")
        print(f"  Total Items Sold      : {result[3]:,d}")
        print(f"  Unique Customers      : {df.select('client_id').distinct().count():,d}")
        print(f"  Countries             : {df.select('pays').distinct().count():,d}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def interactive_menu():
    """Run interactive menu"""
    spark = init_spark()
    
    while True:
        print("\n" + "="*60)
        choice = input(menu()).strip()
        
        if choice == "1":
            view_bronze(spark)
        elif choice == "2":
            view_client_silver(spark)
        elif choice == "3":
            view_country_silver(spark)
        elif choice == "4":
            view_segment_silver(spark)
        elif choice == "5":
            count_records(spark)
        elif choice == "6":
            top_clients(spark)
        elif choice == "7":
            revenue_by_country(spark)
        elif choice == "8":
            loyalty_report(spark)
        elif choice == "9":
            latest_records(spark)
        elif choice == "10":
            statistics(spark)
        elif choice == "11":
            print("\n👋 Goodbye!\n")
            break
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--batch":
        # Run all reports in batch mode
        spark = init_spark()
        print("\n" + "="*60)
        print("Running all reports...")
        print("="*60)
        
        count_records(spark)
        print("\n" + "-"*60)
        top_clients(spark)
        print("\n" + "-"*60)
        statistics(spark)
    else:
        # Run interactive menu
        try:
            interactive_menu()
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!\n")
