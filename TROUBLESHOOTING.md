# 🔧 Troubleshooting Guide

## Common Issues & Solutions

### 1. Kafka Connection Issues

#### Error: "Connection refused"
```
❌ Failed to connect to Kafka: [Errno 61] Connection refused
```

**Causes**:
- ZooKeeper not running
- Kafka broker not started
- Wrong bootstrap server address

**Solutions**:
```bash
# Check if processes are running
jps | grep -E "Kafka|Zookeeper"

# Start ZooKeeper
zookeeper-server-start /usr/local/etc/kafka/zookeeper.properties

# Start Kafka (in separate terminal)
kafka-server-start /usr/local/etc/kafka/server.properties

# Verify connectivity
kafka-broker-api-versions --bootstrap-server localhost:9092
```

---

#### Error: "Topic not found"
```
❌ Exception: Topic ventes_stream does not exist
```

**Solution**:
```bash
# Create the topic
kafka-topics --create \
  --topic ventes_stream \
  --bootstrap-server localhost:9092 \
  --partitions 1 \
  --replication-factor 1

# Verify creation
kafka-topics --list --bootstrap-server localhost:9092
```

---

#### Error: "Consumer lag growing"
```
⚠️  Consumer lag: 1000+ messages behind
```

**Causes**:
- Spark consumer slower than producer
- Insufficient memory
- Network bottleneck

**Solutions**:
```bash
# Increase Spark memory
spark-submit --driver-memory 4g --executor-memory 2g script.py

# Check consumer lag
kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe \
  --group spark-executor

# Reduce producer rate (in producer_ventes.py)
BATCH_INTERVAL = 5  # Increase from 2 to 5 seconds
```

---

### 2. Spark Streaming Issues

#### Error: "OutOfMemoryError: Java heap space"
```
Exception in thread "main" java.lang.OutOfMemoryError: Java heap space
```

**Solutions**:
```bash
# Increase driver memory
spark-submit --driver-memory 4g script.py

# Increase executor memory
spark-submit --executor-memory 2g script.py

# Combine both
spark-submit --driver-memory 4g --executor-memory 2g script.py

# Run in local mode with all cores
spark-submit --master local[*] script.py
```

---

#### Error: "Checkpointing failed"
```
❌ Error: Could not write to checkpoint location
```

**Causes**:
- Checkpoint directory permissions
- Insufficient disk space
- Corrupted checkpoint

**Solutions**:
```bash
# Check disk space
df -h /tmp

# Fix permissions
chmod 777 /tmp/delta/checkpoints/

# Remove corrupted checkpoint (data loss risk!)
rm -rf /tmp/delta/checkpoints/ventes_bronze/*

# Restart consumer (will resume from latest offset)
# Can be configured with "startingOffsets"
```

---

#### Error: "No data appearing in Delta Lake"
```
✅ Streaming started...
❌ But /tmp/delta/bronze/ventes_stream is empty
```

**Debugging**:
```bash
# 1. Check producer is sending
tail -f producer.log
# Should show: "📤 Sale #1: ..."

# 2. Check Kafka has messages
kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic ventes_stream \
  --from-beginning

# 3. Check Spark logs
# Look for "Input: X rows, Output: Y rows"

# 4. Verify Delta path exists
ls -la /tmp/delta/bronze/

# 5. Check if data is written
spark-shell --packages io.delta:delta-spark_2.12:3.2.0
scala> spark.read.format("delta").load("/tmp/delta/bronze/ventes_stream").count()
```

---

### 3. Delta Lake Issues

#### Error: "Table not found"
```
FileNotFoundError: Path does not exist: /tmp/delta/bronze/ventes_stream
```

**Solution**:
```bash
# Wait for first records (Bronze needs initial write)
# After 10-20 seconds, table should be created

# Or create manually
mkdir -p /tmp/delta/bronze/ventes_stream

# Restart consumer
```

---

#### Error: "Schema mismatch"
```
❌ AnalysisException: Schema mismatch when appending
```

**Causes**:
- Field added to producer without schema update
- Data type changed
- Null value in non-nullable field

**Solution**:
```bash
# Update spark_streaming_delta.py with correct schema

# Or enable schema evolution (not recommended)
.option("mergeSchema", "true") \

# Or drop existing table
rm -rf /tmp/delta/bronze/ventes_stream/*
rm -rf /tmp/delta/checkpoints/ventes_bronze/*
# Restart consumer
```

---

#### Error: "Cannot overwrite Delta table"
```
❌ ConcurrentAppendException: Conflict while writing to Delta table
```

**Cause**: Multiple writers to same table

**Solution**:
```bash
# Use single writer at a time
# OR use MERGE operations for concurrent writes
# OR partition data differently
```

---

### 4. Data Quality Issues

#### "NaN or null values in aggregation"
```
average_transaction: null
total_revenue: null
```

**Causes**:
- No data in Bronze yet
- All records filtered out
- Schema mismatch

**Solution**:
```python
# In streaming_silver.py, add:
if df_bronze.count() == 0:
    print("❌ No data in Bronze table yet")
    sys.exit(1)

# Add null checks
df_silver = df_silver.filter(col("total_depense").isNotNull())
```

---

#### "Duplicate records in aggregation"
```
Client Jean Dupont appears twice with same metrics
```

**Cause**: Multiple aggregation runs without overwrite

**Solution**:
```python
# Use correct mode in silver layer
.mode("overwrite") \  # Replaces entire table
# Instead of
.mode("append") \     # Adds duplicates
```

---

### 5. Performance Issues

#### "Latency growing over time"
```
Latency: 245ms → 500ms → 1000ms
```

**Causes**:
- Accumulating state in memory
- Disk filling up
- Network degradation

**Solutions**:
```bash
# Monitor system resources
top -p <spark_pid>
df -h /tmp

# Clean up old checkpoints
rm -rf /tmp/delta/checkpoints/*/
# Note: Will lose recovery state

# Increase batch interval
BATCH_INTERVAL = 5  # Instead of 2

# Reduce data retention
# In streaming_silver.py - run vacuum
dt = DeltaTable.forPath(spark, "/tmp/delta/bronze/...")
dt.vacuum(1)  # Keep only 1 hour of history
```

---

#### "Producer falling behind (lag increasing)"
```
Consumer lag: Increasing by 100 records/batch
```

**Solutions**:
```bash
# Speed up producer rate
BATCH_INTERVAL = 1  # Decrease from 2

# OR slow down producer
BATCH_INTERVAL = 5  # Increase from 2

# Check Spark parallelism
spark-submit --conf spark.sql.shuffle.partitions=4 script.py

# Check network bandwidth
iftop -i eth0  # Monitor network usage
```

---

### 6. Permission Issues

#### "Permission denied: /tmp/delta"
```
PermissionError: [Errno 13] Permission denied
```

**Solution**:
```bash
# Fix directory permissions
chmod 777 /tmp/delta
chmod -R 777 /tmp/delta/*

# Or run as same user who created directories
sudo chown -R $USER /tmp/delta
```

---

#### "Cannot write to checkpoint"
```
AccessDeniedException: Path is read-only
```

**Solution**:
```bash
# Ensure Spark user can write
chmod 755 /tmp/delta/checkpoints/

# Or run Spark with write permissions
sudo spark-submit --user=$USER script.py
```

---

### 7. Network Issues

#### "Timeout connecting to Kafka"
```
org.apache.kafka.common.errors.TimeoutException: Failed to update metadata
```

**Causes**:
- Network firewall blocking port 9092
- DNS resolution issues
- Kafka broker not responsive

**Solutions**:
```bash
# Test port connectivity
telnet localhost 9092

# Check firewall
sudo iptables -L -n | grep 9092

# Test DNS resolution
nslookup localhost

# Increase timeout
# In producer_ventes.py:
KafkaProducer(
    ...
    request_timeout_ms=30000  # Increase from default
)
```

---

### 8. Diagnostic Commands

#### Monitor Kafka Topics
```bash
# Watch topic in real-time
kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic ventes_stream \
  --from-beginning \
  --max-messages 10

# Get topic statistics
kafka-topics --describe \
  --topic ventes_stream \
  --bootstrap-server localhost:9092
```

#### Monitor Spark Application
```bash
# View Spark UI (if running locally)
# Open browser: http://localhost:4040

# Check application logs
grep "ERROR" stderr.log | head -20

# Monitor JVM memory
jconsole <spark_driver_pid>
```

#### Monitor Delta Lake
```bash
# List Delta versions
spark-shell --packages io.delta:delta-spark_2.12:3.2.0
scala> val dt = DeltaTable.forPath(spark, "/tmp/delta/bronze/...")
scala> dt.history().show()

# Check table size
du -sh /tmp/delta/bronze/ventes_stream

# Vacuum old versions
scala> dt.vacuum(24)  # Keep 24 hours
```

#### System Resource Monitoring
```bash
# CPU and Memory
top -b -n 1 | head -20

# Disk space
df -h /tmp
du -sh /tmp/delta/*

# Network connections
netstat -an | grep 9092

# Process info
ps aux | grep -E "kafka|spark|java"
```

---

### 9. Recovery Procedures

#### Complete Pipeline Failure

```bash
# 1. Stop all processes
killall java

# 2. Clean checkpoint (lose recovery state)
rm -rf /tmp/delta/checkpoints/ventes_bronze/*

# 3. Verify Kafka still has data (offset tracking)
kafka-consumer-groups --list --bootstrap-server localhost:9092

# 4. Restart services in order:
# Terminal 1: ZooKeeper
# Terminal 2: Kafka
# Terminal 3: Producer
# Terminal 4: Consumer
# Terminal 5: Analytics

# 5. Monitor recovery
kafka-consumer-groups --describe \
  --group spark-executor \
  --bootstrap-server localhost:9092
```

#### Data Corruption Recovery

```bash
# 1. Identify corrupted partition
ls -la /tmp/delta/bronze/ventes_stream/jour=2024-12-12/

# 2. Restore from backup (if available)
cp -r /backups/delta_bronze_20241212/* /tmp/delta/bronze/

# 3. Or remove corrupted data and replay
rm -rf /tmp/delta/bronze/ventes_stream/jour=2024-12-12/

# 4. Restart consumer with checkpoint reset
rm -rf /tmp/delta/checkpoints/ventes_bronze/*
```

---

### 10. Getting Help

#### Collect Debug Information

```bash
# Create debug bundle
mkdir debug_info
cp /tmp/delta/checkpoints/*/00000000000000000000.json debug_info/
ps aux | grep -E "kafka|spark|java" > debug_info/processes.txt
df -h > debug_info/disk.txt
jps > debug_info/jps.txt
tail -100 producer.log > debug_info/producer.log
tail -100 consumer.log > debug_info/consumer.log

# Zip for sharing
tar -czf debug_info.tar.gz debug_info/
```

#### Common Log Locations
```bash
# Producer logs
tail -f /var/log/producer_ventes.log

# Spark driver logs
tail -f /tmp/spark-*-driver.log

# Kafka logs
tail -f /opt/kafka/logs/server.log

# System logs (macOS)
log stream --level debug --source MESSAGE | grep -i "kafka|spark"

# System logs (Linux)
journalctl -u kafka -f
```

---

## Quick Reference Table

| Error | Cause | Solution |
|-------|-------|----------|
| Connection refused | Service not running | Start ZooKeeper & Kafka |
| Topic not found | Topic not created | Create topic with kafka-topics |
| OutOfMemory | Insufficient heap | Increase --driver-memory |
| No data | Producer not sending | Check producer logs |
| Schema mismatch | Field added | Update schema or enable evolution |
| Permission denied | File access issue | chmod 777 /tmp/delta |
| High latency | System overload | Increase resources or reduce rate |
| Duplicate data | Incorrect write mode | Use mode("overwrite") |

---

**Last Updated**: December 2024  
**For More Help**: See README.md and ARCHITECTURE.md
