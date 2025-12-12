# 🚀 Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies
```bash
# Install Python packages
pip install -r requirements.txt
```

### Step 2: Verify Setup
```bash
# Run setup validation
python setup_utils.py
```

## 6-Terminal Execution

Open 6 terminal windows and run these commands in order:

### Terminal 1: ZooKeeper
```bash
# macOS/Linux
zookeeper-server-start /usr/local/etc/kafka/zookeeper.properties

# Windows (if using WSL or Git Bash)
zookeeper-server-start.bat %KAFKA_HOME%\config\zookeeper.properties
```

### Terminal 2: Kafka Broker
```bash
# macOS/Linux
kafka-server-start /usr/local/etc/kafka/server.properties

# Windows
kafka-server-start.bat %KAFKA_HOME%\config\server.properties
```

### Terminal 3: Create Kafka Topic
```bash
kafka-topics --create \
  --topic ventes_stream \
  --bootstrap-server localhost:9092 \
  --partitions 1 \
  --replication-factor 1
```

### Terminal 4: Run Producer
```bash
python producer_ventes.py
```

Expected output every 2 seconds:
```
2024-12-12 10:15:25 - INFO - 📤 Sale #1: Jean Dupont - Ordinateur portable - €1799.98
```

### Terminal 5: Run Spark Streaming Consumer
```bash
spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,io.delta:delta-spark_2.12:3.2.0 \
  spark_streaming_delta.py
```

Expected output:
```
2024-12-12 10:15:30 - INFO - ✅ Connected to Kafka topic: ventes_stream
2024-12-12 10:15:32 - INFO - 📊 Metrics - Input: 2 rows, Output: 2 rows, Latency: 245ms
```

### Terminal 6: Run Analytics (Optional - run periodically)
```bash
spark-submit \
  --packages io.delta:delta-spark_2.12:3.2.0 \
  streaming_silver.py
```

## 📊 Query Results

After Terminal 6 runs, you'll see analytics:

```
🏆 Top 10 Clients by Revenue:
+----+----------+-------+---------------+----------+-----------+
|   |client_nom|pays   |segment_depense|total_dep |nb_achats  |
+----+----------+-------+---------------+----------+-----------+
|Jean|Jean Dupa |France |Premium        |1799.98   |3          |
```

## 🔍 Monitor Pipeline

Run the interactive query utility (in another terminal):
```bash
# Interactive menu
python query_utils.py

# Or batch report
python query_utils.py --batch
```

## 🛑 Stopping the Pipeline

1. **Terminal 4 (Producer)**: `Ctrl+C`
2. **Terminal 5 (Streaming)**: `Ctrl+C`
3. **Terminal 6 (Analytics)**: `Ctrl+C`
4. **Terminal 2 (Kafka)**: `Ctrl+C`
5. **Terminal 1 (ZooKeeper)**: `Ctrl+C`

## 📂 Data Locations

- **Raw Data (Bronze)**: `/tmp/delta/bronze/ventes_stream/`
- **Aggregations (Silver)**: `/tmp/delta/silver/`
- **Checkpoints**: `/tmp/delta/checkpoints/`

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Connection refused" | Start Kafka and ZooKeeper first |
| "Path does not exist" | Wait for first records to be written |
| "No data appearing" | Check producer is sending with Terminal 4 output |
| "Out of memory" | Increase Spark memory: `spark-submit --driver-memory 4g` |

## 📚 Next Steps

- Read [README.md](README.md) for detailed documentation
- Explore [query_utils.py](query_utils.py) for more analytics queries
- Check Spark logs: Look for patterns in Terminal 5 output
- View Delta Lake history: `kafka-console-consumer --bootstrap-server localhost:9092 --topic ventes_stream --from-beginning`

## 🎯 Key Metrics to Monitor

- **Input Rows**: Number of records read from Kafka
- **Output Rows**: Number written to Delta Lake
- **Latency**: Time taken per batch
- **Unique Customers**: Growing count of distinct clients
- **Total Revenue**: Cumulative sales amount

---

**Enjoy your real-time analytics pipeline! 🎉**
