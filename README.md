# Real-Time Sales Streaming with Kafka + Spark + Delta Lake

A complete **Lakehouse architecture** for real-time sales data processing using Apache Kafka, Spark Structured Streaming, and Delta Lake.

## 🏗️ Architecture

```
┌─────────────────┐
│  Sales Producer │ (Kafka)
│                 │
└────────┬────────┘
         │ ventes_stream topic
         │
    ┌────▼────────────────┐
    │  Kafka Broker       │
    │  (localhost:9092)   │
    └────┬────────────────┘
         │
    ┌────▼──────────────────────┐
    │  Spark Streaming Consumer  │
    │  (Bronze Layer - Raw Data) │
    │  ✓ Watermarking           │
    │  ✓ Checkpointing          │
    │  ✓ Partitioning by date   │
    └────┬──────────────────────┘
         │ /tmp/delta/bronze/ventes_stream
         │
    ┌────▼──────────────────────────┐
    │  Silver Layer (Aggregations)   │
    │  ✓ Client Analytics           │
    │  ✓ Country Revenue            │
    │  ✓ Segment Analysis           │
    │  ✓ Loyalty Detection          │
    └────────────────────────────────┘
         │
         └─► Dashboard & Insights
```

## 📋 Project Components

### 1. **producer_ventes.py** - Kafka Sales Simulator
- Generates realistic sales data every 2 seconds
- Sends to Kafka topic: `ventes_stream`
- Features:
  - Multiple products and clients
  - Random quantity and amount generation
  - Error handling and delivery callbacks
  - Structured logging

### 2. **spark_streaming_delta.py** - Streaming Consumer (Bronze Layer)
- Reads Kafka stream in real-time
- Transforms and enriches data
- Writes to Delta Lake Bronze table
- Key features:
  - **Watermarking**: Handles late-arriving data (10 minutes delay tolerance)
  - **Checkpointing**: Fault tolerance and recovery
  - **Partitioning**: Data organized by date for efficient querying
  - **Metrics Monitoring**: Tracks throughput and latency
  - Automatic schema inference

### 3. **streaming_silver.py** - Analytics Pipeline (Silver Layer)
- Reads Bronze table and creates aggregations
- Multiple analytical views:
  - **Client Aggregation**: Revenue, purchase count, loyalty metrics per client
  - **Country Analysis**: Revenue and transaction metrics by country
  - **Segment Analysis**: Business vs Consumer segment breakdown
- Features:
  - Customer segmentation by spending
  - Loyalty detection (repeat customers)
  - Comprehensive dashboard analytics
  - Metrics and KPI reporting

## 🚀 Quick Start

### Prerequisites

Ensure you have installed:
```bash
# Python packages
pip install pyspark delta-spark kafka-python

# Apache Spark 3.5+
# Apache Kafka with ZooKeeper
# Java 8 or higher
```

### Local Setup - Terminal by Terminal

**Terminal 1: Start ZooKeeper**
```bash
zookeeper-server-start /usr/local/etc/kafka/zookeeper.properties
# Or Windows:
zookeeper-server-start.bat %KAFKA_HOME%\config\zookeeper.properties
```

**Terminal 2: Start Kafka Broker**
```bash
kafka-server-start /usr/local/etc/kafka/server.properties
# Or Windows:
kafka-server-start.bat %KAFKA_HOME%\config\server.properties
```

**Terminal 3: Create Kafka Topic**
```bash
kafka-topics --create \
  --topic ventes_stream \
  --bootstrap-server localhost:9092 \
  --partitions 1 \
  --replication-factor 1
```

**Terminal 4: Run Sales Producer**
```bash
python producer_ventes.py
```

Expected output:
```
2024-12-12 10:15:23 - INFO - ✅ Connected to Kafka broker: localhost:9092
2024-12-12 10:15:23 - INFO - 🚀 Sales Producer started. Sending records every 2 seconds...
2024-12-12 10:15:25 - INFO - 📤 Sale #1: Jean Dupont - Ordinateur portable - €1799.98
2024-12-12 10:15:27 - INFO - 📤 Sale #2: Maria Garcia - Clavier mécanique - €75.00
```

**Terminal 5: Run Spark Streaming Consumer**
```bash
spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,io.delta:delta-spark_2.12:3.2.0 \
  spark_streaming_delta.py
```

Expected output:
```
2024-12-12 10:15:30 - INFO - ✅ Spark Session initialized successfully
2024-12-12 10:15:30 - INFO - ✅ Connected to Kafka topic: ventes_stream
2024-12-12 10:15:30 - INFO - ✅ Streaming started. Writing to Delta Lake Bronze table...
2024-12-12 10:15:32 - INFO - 📊 Metrics - Input: 2 rows, Output: 2 rows, Latency: 245ms
```

**Terminal 6 (Optional): Run Silver Layer Analytics**
```bash
spark-submit \
  --packages io.delta:delta-spark_2.12:3.2.0 \
  streaming_silver.py
```

Expected output:
```
2024-12-12 10:15:45 - INFO - ✅ Spark Session initialized
2024-12-12 10:15:50 - INFO - ✅ Bronze table loaded: 15 records
2024-12-12 10:15:52 - INFO - Creating client aggregation...
2024-12-12 10:15:55 - INFO - ✅ Client aggregation saved: 5 records

📊 SALES ANALYTICS DASHBOARD
============================================================

🏆 Top 10 Clients by Revenue:
+----+----------+-------+-----------+-----------+--------+---+
|... |client_nom|pays   |segment...|total_...|nb_achats|...|
```

## 📊 Data Schema

### Bronze Table (Raw Data)
```python
{
  "vente_id": int,
  "client_id": int,
  "produit_id": int,
  "timestamp": timestamp,
  "quantite": int,
  "montant": double,
  "client_nom": string,
  "produit_nom": string,
  "categorie": string,
  "pays": string,
  "segment": string,
  "date_ingestion": timestamp,
  "jour": string (YYYY-MM-DD)
}
```

### Silver Tables (Aggregated)

**Client Aggregation:**
```python
{
  "client_id", "client_nom", "pays", "segment", "jour",
  "total_quantite", "total_depense", "nb_achats", "panier_moyen",
  "achat_min", "achat_max", "nb_produits_distincts",
  "est_client_fidele": boolean,
  "segment_depense": "Premium" | "Standard" | "Economy"
}
```

**Country Aggregation:**
```python
{
  "pays",
  "total_transactions", "revenue_total", "transaction_moyenne",
  "items_sold", "unique_customers"
}
```

**Segment Aggregation:**
```python
{
  "segment",
  "total_transactions", "revenue_total", "transaction_moyenne",
  "unique_customers", "countries_count"
}
```

## 🎯 Key Features

### Watermarking ⏰
- **10-minute tolerance** for late-arriving data
- Prevents data loss from delayed Kafka messages
- Configurable via `WATERMARK_DELAY`

### Checkpointing 💾
- Fault-tolerant streaming with state recovery
- Prevents data duplication on restart
- Location: `/tmp/delta/checkpoints/ventes_bronze`

### Partitioning 📂
- Data organized by `jour` (date) in Bronze layer
- Enables efficient date-based queries
- Reduces query latency on large datasets

### Monitoring 📈
- Real-time metrics: input rows, output rows, latency
- Recent progress tracking via `query.recentProgress`
- Detailed logging at each step

### Analytics 📊
- Client lifetime value calculation
- Loyalty detection (repeat purchasers)
- Revenue segmentation (Premium/Standard/Economy)
- Country and segment performance analysis
- KPI dashboard with key metrics

## 🔧 Configuration

Edit these variables in each file to customize:

**producer_ventes.py:**
- `KAFKA_TOPIC = "ventes_stream"` - Topic name
- `KAFKA_SERVER = "localhost:9092"` - Broker address
- `BATCH_INTERVAL = 2` - Seconds between sales (increase for fewer records)

**spark_streaming_delta.py:**
- `KAFKA_BROKERS = "localhost:9092"` - Broker address
- `WATERMARK_DELAY = "10 minutes"` - Late data tolerance
- `BRONZE_PATH = "/tmp/delta/bronze/..."` - Storage location

**streaming_silver.py:**
- All paths and aggregation rules are configurable
- Modify `segment_depense` thresholds for spending brackets

## 📁 Data Storage

```
/tmp/delta/
├── bronze/
│   └── ventes_stream/
│       ├── jour=2024-12-12/
│       ├── jour=2024-12-13/
│       └── _delta_log/
├── silver/
│   ├── ventes_aggreges/
│   ├── ventes_par_pays/
│   ├── ventes_par_segment/
│   └── _delta_log/
└── checkpoints/
    └── ventes_bronze/
        └── (offset tracking for streaming)
```

## 🔍 Querying Data with SQL

```sql
-- Read Bronze table
SELECT * FROM delta.`/tmp/delta/bronze/ventes_stream` 
WHERE jour = '2024-12-12'
LIMIT 10;

-- Top revenue clients
SELECT * FROM delta.`/tmp/delta/silver/ventes_aggreges`
ORDER BY total_depense DESC
LIMIT 5;

-- Revenue by country
SELECT * FROM delta.`/tmp/delta/silver/ventes_par_pays`
ORDER BY revenue_total DESC;
```

## ⚠️ Troubleshooting

### Kafka Connection Error
```
❌ Failed to connect to Kafka: Connection refused
```
**Solution:** Ensure ZooKeeper and Kafka broker are running
```bash
jps | grep Kafka  # Check if running
```

### Delta Table Not Found
```
❌ Path does not exist: /tmp/delta/bronze/...
```
**Solution:** Wait for first records to be written, or run producer first

### Out of Memory
```
java.lang.OutOfMemoryError: Java heap space
```
**Solution:** Increase Spark memory
```bash
spark-submit --driver-memory 4g --executor-memory 2g script.py
```

### No Data Appearing
- Check producer is sending: `tail producer log output`
- Verify Kafka topic has data: 
  ```bash
  kafka-console-consumer --bootstrap-server localhost:9092 \
    --topic ventes_stream --from-beginning
  ```
- Check checkpoint exists: `ls -la /tmp/delta/checkpoints/`

## 📚 Further Enhancements

- ✅ Add real Kafka authentication (SASL/SSL)
- ✅ Implement schema registry for evolved schemas
- ✅ Add ACID transactions for critical operations
- ✅ Build real-time dashboard (Databricks SQL, Power BI)
- ✅ Add data quality validation rules
- ✅ Implement slowly changing dimensions (SCD Type 2)
- ✅ Add ML features for customer segmentation
- ✅ Export to cloud data warehouse (Snowflake, BigQuery)

## 📞 Support

For issues or questions:
1. Check logs: `grep ERROR *.log`
2. Verify Kafka connectivity
3. Ensure Delta Lake package versions match
4. Check disk space for `/tmp/delta/`

---

**Happy Streaming! 🚀**
