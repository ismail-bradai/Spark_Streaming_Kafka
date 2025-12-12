# 🏗️ Architecture & Design Document

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    LAKEHOUSE ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────────┘

INGESTION LAYER
═══════════════════════════════════════════════════════════════════
    ┌──────────────────┐
    │  Sales Producer  │  ◄── Generates ~30 sales/minute
    │  (Simulator)     │     Random clients, products, quantities
    └────────┬─────────┘
             │
             ▼ JSON messages
    ┌──────────────────┐
    │ Kafka Topic      │  ◄── Distributed, partitioned queue
    │ ventes_stream    │     Offset tracking, replay capability
    └────────┬─────────┘
             │

BRONZE LAYER (Raw Data)
═══════════════════════════════════════════════════════════════════
             ▼
    ┌──────────────────────────────┐
    │  Spark Streaming Consumer    │
    │  - Read from Kafka           │
    │  - Parse JSON schema         │
    │  - Watermark late data (10m) │
    │  - Add metadata              │
    │  - Partition by date         │
    └────────┬─────────────────────┘
             │
             ▼ Append mode
    ┌──────────────────────────────┐
    │  Delta Lake Bronze Table     │
    │  /tmp/delta/bronze/          │
    │                              │
    │  Partitions: jour (YYYY-MM-DD)
    │  Format: Parquet + Delta Log │
    │  Retention: 90 days (adjust) │
    └──────────────────────────────┘

SILVER LAYER (Aggregations)
═══════════════════════════════════════════════════════════════════
             ▼
    ┌──────────────────────────────┐
    │  Aggregation Jobs (Batch)    │
    │  - Read Bronze               │
    │  - Group & aggregate         │
    │  - Calculate metrics         │
    │  - Detect patterns           │
    └─────────┬──────────┬──────────┘
              │          │
         ┌────▼──┐  ┌────▼──┐     ┌──────────────┐
         │Client │  │Country│     │   Segment    │
         │Agg    │  │Agg    │     │   Agg        │
         └────┬──┘  └────┬──┘     └──────┬───────┘
              │          │                │
         ┌────▼──┐  ┌────▼──┐     ┌──────▼───────┐
         │ SLV1  │  │ SLV2  │     │    SLV3      │
         │/agg/  │  │/pays/ │     │  /segment/   │
         └───────┘  └───────┘     └──────────────┘

GOLD LAYER (Analytics & BI)
═══════════════════════════════════════════════════════════════════
         ┌─────────────────────────────────┐
         │  Dashboard & Analytics Query    │
         │  - Top customers               │
         │  - Revenue trends              │
         │  - Geographic analysis         │
         │  - Loyalty metrics             │
         │  - Segmentation results        │
         └─────────────────────────────────┘
```

## Data Flow Diagram

```
Time Dimension: Real-time ────► Near real-time ────► Batch Analytics

    Every 2 sec                Every micro-batch        Periodic (hourly/daily)
         │                           │                          │
         ▼                           ▼                          ▼
    Producer                    Streaming Job              Analytics Job
    (sends 1 sale)        (consumes 10-20 sales)      (aggregates 1000+ sales)
         │                           │                          │
         └──► Kafka ────► Bronze ────► Checkpoints             │
                 (queue)    (history)   (fault-tolerance)       │
                                                                 │
                                            ┌────────────────────┘
                                            │
                                            ▼
                                       Silver Tables
                                      (aggregations)
                                            │
                                            ▼
                                      SQL / Dashboard
```

## Component Details

### 1. Producer (producer_ventes.py)

**Purpose**: Simulate real-world sales events

**Key Features**:
- Generates random but realistic sales data
- 5 products × 5 clients × random quantities
- JSON serialization for Kafka
- Async callbacks for delivery confirmation
- Configurable batch interval

**Data Structure**:
```python
{
    "vente_id": 1,                              # Unique transaction ID
    "client_id": 1,                             # Customer reference
    "produit_id": 101,                          # Product reference
    "timestamp": "2024-12-12T10:15:23.123456",  # Event time (ISO-8601)
    "quantite": 2,                              # Number of units
    "montant": 1799.98,                         # Revenue (EUR)
    "client_nom": "Jean Dupont",                # Customer name
    "produit_nom": "Ordinateur portable",       # Product name
    "categorie": "Électronique",                # Product category
    "pays": "France",                           # Customer country
    "segment": "Particulier"                    # B2B or B2C
}
```

**Execution**: `python producer_ventes.py`

### 2. Streaming Consumer (spark_streaming_delta.py)

**Purpose**: Real-time ingestion and Bronze layer creation

**Architecture**:
```
Kafka Source
    ↓ readStream
JSON Parser (from_json)
    ↓
Data Enrichment (timestamp conversion, metadata)
    ↓ withWatermark (10 minutes)
Watermarked DataFrame
    ↓ writeStream
Delta Lake (Bronze)
```

**Key Transformations**:
1. **Schema Parsing**: Convert JSON string to structured data
2. **Timestamp Conversion**: Parse ISO-8601 to Spark timestamp
3. **Metadata Addition**:
   - `date_ingestion`: Current processing time
   - `jour`: Date partition key (YYYY-MM-DD)
4. **Watermarking**: Allows 10-minute late data
5. **Partitioning**: Organized by `jour` for query efficiency

**Checkpointing**:
- Location: `/tmp/delta/checkpoints/ventes_bronze`
- Tracks: Kafka offsets, source metadata
- Recovery: Resumes from last successful batch if interrupted

**Execution**:
```bash
spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,io.delta:delta-spark_2.12:3.2.0 \
  spark_streaming_delta.py
```

**Metrics Tracked**:
- Input Rows: Records read from Kafka
- Output Rows: Records written to Delta
- Batch Duration: Time to process batch
- Processing Latency: Total end-to-end delay

### 3. Analytics Pipeline (streaming_silver.py)

**Purpose**: Aggregate Bronze data and create analytical views

**Three Silver Tables**:

#### a) Client Aggregation (ventes_aggreges)
```sql
GROUP BY client_id, client_nom, pays, segment, jour
AGGREGATE:
  - sum(quantite)           → total_quantite
  - sum(montant)            → total_depense
  - count(*)                → nb_achats
  - avg(montant)            → panier_moyen
  - min(montant)            → achat_min
  - max(montant)            → achat_max
  - count(distinct produit) → nb_produits_distincts
CALCULATED:
  - est_client_fidele (nb_achats >= 2)
  - segment_depense (Premium/Standard/Economy)
```

#### b) Country Analysis (ventes_par_pays)
```sql
GROUP BY pays
AGGREGATE:
  - count(*)                    → total_transactions
  - sum(montant)                → revenue_total
  - avg(montant)                → transaction_moyenne
  - sum(quantite)               → items_sold
  - count(distinct client_id)   → unique_customers
```

#### c) Segment Analysis (ventes_par_segment)
```sql
GROUP BY segment
AGGREGATE:
  - count(*)                    → total_transactions
  - sum(montant)                → revenue_total
  - avg(montant)                → transaction_moyenne
  - count(distinct client_id)   → unique_customers
  - count(distinct pays)        → countries_count
```

**Execution**: Run periodically (hourly/daily)
```bash
spark-submit \
  --packages io.delta:delta-spark_2.12:3.2.0 \
  streaming_silver.py
```

## Watermarking Deep Dive

**Problem**: Late-arriving data in distributed systems
- Records delayed by network issues
- Duplicate handling needed
- Out-of-order processing

**Solution**: 10-minute watermark
```
Event Time: 10:00:00
Watermark: 10:10:00 (current_watermark + delay)

Events arriving:
- 10:08:00 ✅ Before watermark → Process
- 10:12:00 ❌ After watermark → Drop (late)
```

**Configuration**: Edit `WATERMARK_DELAY` in `spark_streaming_delta.py`

## Partitioning Strategy

**Bronze Layer**: Partitioned by `jour` (date)
```
/tmp/delta/bronze/ventes_stream/
├── jour=2024-12-10/
│   ├── part-00000.parquet
│   └── part-00001.parquet
├── jour=2024-12-11/
│   └── part-00000.parquet
├── jour=2024-12-12/
│   ├── part-00000.parquet
│   └── _delta_log/
│       ├── 00000000000000000000.json
│       └── 00000000000000000001.json
```

**Benefits**:
- Faster date-range queries
- Easier data retention policies
- Parallel partition pruning
- Simple archive/delete by date

## Checkpoint Mechanism

**Location**: `/tmp/delta/checkpoints/ventes_bronze/`

**Contents**:
- Kafka offset tracking
- Processing state
- UUID checkpoint files

**Recovery**:
1. Stream stops unexpectedly
2. Spark reads checkpoint metadata
3. Resumes from last committed offset
4. No duplicate data (exactly-once semantics)

## Performance Considerations

### 1. Throughput
- **Current**: ~30 sales/minute from producer
- **Spark Processing**: Sub-second latency per batch
- **Bottleneck**: Kafka broker (can handle 100K+ msgs/sec)

### 2. Scalability
- **Increase Partitions**: `--partitions 4` for Kafka topic
- **Parallel Consumers**: Run multiple Spark jobs
- **Cluster Mode**: Deploy on Spark cluster

### 3. Storage
- **Compression**: Delta automatically compresses
- **Retention**: Vacuum old versions after 24 hours
- **Estimate**: ~1KB per transaction, ~1GB per 1M sales

### 4. Query Performance
- **Partitioning**: Queries by `jour` are fast
- **Caching**: Silver tables cached after first read
- **Optimization**: Spark auto-optimizes via Catalyst

## Fault Tolerance

### Kafka Failures
- **Rebalancing**: Auto-detected, seamless recovery
- **Broker Restart**: Offset replay from checkpoint
- **Data Loss**: One partition replication factor (adjust for production)

### Spark Failures
- **Task Failures**: Automatic retry (max 3 attempts)
- **Driver Failure**: Checkpoint recovery
- **Network**: Timeout and reconnect logic

### Delta Lake
- **ACID Guarantees**: Automatic conflict resolution
- **Version History**: Always available for rollback
- **Concurrent Writes**: Handled with optimistic locking

## Security Considerations

### Current Setup (Local Development)
⚠️ Not production-ready:
- No Kafka authentication
- No SSL/TLS encryption
- No data encryption at rest
- All data in `/tmp` (no persistence)

### Production Hardening
1. **Kafka Security**:
   - Enable SASL/SCRAM authentication
   - Use SSL/TLS for transport encryption

2. **Data Security**:
   - Encrypt Delta Lake with KMS
   - Use network VPN for Spark cluster
   - Enable audit logging

3. **Access Control**:
   - Use Delta Lake table ACLs
   - Implement Spark authentication
   - Role-based data access

4. **Compliance**:
   - GDPR: Data retention policies
   - Audit: Track all data modifications
   - Backup: Regular snapshots

## Monitoring & Observability

### Metrics Available

**From `query.recentProgress`**:
```python
{
    "numInputRows": 15,              # Records from Kafka
    "numOutputRows": 15,             # Records to Delta
    "numUpdatedStateRows": 0,        # State updates
    "durationMs": {
        "addBatch": 245,             # Processing time
        "commitOffsets": 12,
        "getBatch": 5
    },
    "eventTime": {
        "avg": "2024-12-12T10:15:30Z",
        "max": "2024-12-12T10:15:32Z",
        "min": "2024-12-12T10:15:25Z"
    },
    "states": [{
        "numRowsTotal": 1000,
        "numRowsUpdated": 15
    }]
}
```

**Custom Dashboards**:
- Kafka lag monitoring
- Delta Lake write latency
- Query execution times
- System resource usage (CPU, memory, I/O)

## Disaster Recovery

### Backup Strategy
```bash
# Backup Bronze table (daily)
cp -r /tmp/delta/bronze /backups/delta_bronze_$(date +%Y%m%d)

# Backup checkpoints
cp -r /tmp/delta/checkpoints /backups/checkpoints_$(date +%Y%m%d)
```

### Recovery Procedures
1. **Table Corruption**: Restore from backup, restart pipeline
2. **Data Loss**: Use Delta Lake time travel
   ```python
   spark.read.format("delta") \
       .option("timestampAsOf", "2024-12-12") \
       .load("/tmp/delta/bronze/...")
   ```
3. **Complete Failure**: Replay from Kafka (offset tracking)

---

## Next Enhancements

- [ ] Schema evolution and management
- [ ] Advanced data quality validations
- [ ] Real-time anomaly detection
- [ ] Machine learning feature engineering
- [ ] Cloud deployment (AWS S3, Azure ADLS)
- [ ] Multi-cluster federation
- [ ] Advanced monitoring dashboard

---

**Architecture Version**: 1.0  
**Last Updated**: December 2024  
**Maintainer**: Data Engineering Team
