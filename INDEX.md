# 📑 Project Index & Navigation

Welcome to the **Real-Time Sales Streaming Lakehouse** project!

This is your complete guide to navigate all project components.

---

## 🗺️ Quick Navigation

### 🚀 I want to START NOW
1. **[QUICKSTART.md](QUICKSTART.md)** ← Read this first (5 minutes)
2. Run: `python setup_utils.py`
3. Open 6 terminals and follow the guide

### 📚 I want to UNDERSTAND the project
1. **[README.md](README.md)** - Complete overview (20 minutes)
2. **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design (30 minutes)
3. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Implementation details

### 🔧 I'm having ISSUES
1. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Problems & solutions
2. Search for your error message
3. Follow the diagnostic steps

### 💻 I want to EXPLORE the code
1. **[producer_ventes.py](producer_ventes.py)** - Kafka producer (120 lines)
2. **[spark_streaming_delta.py](spark_streaming_delta.py)** - Stream consumer (160 lines)
3. **[streaming_silver.py](streaming_silver.py)** - Analytics pipeline (200 lines)

### 📊 I want to ANALYZE data
1. **[query_utils.py](query_utils.py)** - Interactive analytics tool
2. Run: `python query_utils.py` or `python query_utils.py --batch`
3. Explore tables and metrics

### ⚙️ I want to CONFIGURE something
1. **[config.ini](config.ini)** - All configuration options
2. **[requirements.txt](requirements.txt)** - Python dependencies
3. Update settings and restart services

---

## 📂 Project Structure

```
spark_streaming_kafka/
│
├── 📄 APPLICATION FILES (Run these)
│   ├── producer_ventes.py              # Kafka producer - sales simulator
│   ├── spark_streaming_delta.py        # Spark consumer - Bronze layer
│   └── streaming_silver.py             # Analytics - Silver layer
│
├── 📖 DOCUMENTATION FILES (Read these)
│   ├── QUICKSTART.md                   # 5-minute setup ⭐ START HERE
│   ├── README.md                       # Complete documentation
│   ├── ARCHITECTURE.md                 # System design details
│   ├── PROJECT_SUMMARY.md              # Implementation guide
│   ├── TROUBLESHOOTING.md              # Problems & solutions
│   └── INDEX.md                        # This file
│
├── 🛠️ UTILITY FILES (Use these)
│   ├── setup_utils.py                  # Environment validation
│   ├── query_utils.py                  # Data exploration tool
│   └── check_setup.sh                  # Setup verification (bash)
│
├── ⚙️ CONFIGURATION FILES (Customize)
│   ├── config.ini                      # Application settings
│   └── requirements.txt                # Python dependencies
│
└── 💾 DATA DIRECTORIES (Created at runtime)
    └── /tmp/delta/                     # Delta Lake storage
        ├── bronze/                     # Raw data
        ├── silver/                     # Aggregations
        └── checkpoints/                # Stream recovery
```

---

## 📖 File Descriptions

### Core Application Files

#### [producer_ventes.py](producer_ventes.py) (120 lines)
**Purpose**: Simulate real-world sales events  
**Sends**: JSON messages to Kafka topic every 2 seconds  
**Generates**: 5 random clients × 6 products × random quantities  
**Output**: Sales records with client, product, timestamp, amount  
**Run**: `python producer_ventes.py`  
**Logs**: Each sale sent and delivery status

#### [spark_streaming_delta.py](spark_streaming_delta.py) (160 lines)
**Purpose**: Real-time data ingestion and Bronze layer storage  
**Reads**: Kafka topic `ventes_stream`  
**Transforms**: Parse JSON, add metadata, apply watermarking  
**Writes**: Delta Lake Bronze table  
**Features**: 
- Watermarking (10-minute late data tolerance)
- Checkpointing (fault recovery)
- Partitioning by date
- Metrics monitoring  
**Run**: `spark-submit --packages ... spark_streaming_delta.py`  
**Output**: Streaming metrics every 30 seconds

#### [streaming_silver.py](streaming_silver.py) (200 lines)
**Purpose**: Aggregate Bronze data and create analytical views  
**Reads**: Delta Lake Bronze table  
**Creates**: 3 Silver tables (client, country, segment aggregations)  
**Includes**: Dashboard, loyalty detection, spending segments  
**Run**: `spark-submit --packages ... streaming_silver.py`  
**Output**: Analytics dashboard with key metrics

### Documentation Files

#### [QUICKSTART.md](QUICKSTART.md) ⭐ START HERE
5-minute guide to get everything running:
- Installation
- 6 terminal setup
- Expected outputs
- Quick troubleshooting

#### [README.md](README.md)
Complete project documentation:
- Architecture overview
- Data schema
- Component details
- Configuration options
- Query examples
- Troubleshooting tips

#### [ARCHITECTURE.md](ARCHITECTURE.md)
Deep dive into system design:
- Data flow diagrams
- Component architecture
- Watermarking explained
- Checkpointing mechanism
- Performance characteristics
- Security considerations
- Disaster recovery

#### [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
Implementation guide and learning path:
- What's included
- Getting started (3 steps)
- Configuration reference
- Key concepts explained
- Next steps (beginner → advanced)
- Success criteria

#### [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
Common issues and solutions:
- Kafka connection errors
- Spark out-of-memory issues
- Delta Lake problems
- Data quality issues
- Performance problems
- Permission issues
- Recovery procedures
- Diagnostic commands

### Utility Files

#### [setup_utils.py](setup_utils.py)
Environment validation and setup:
- Checks Python version
- Verifies dependencies
- Tests Kafka connectivity
- Creates directories
- Generates requirements.txt
- Displays project structure
- Shows execution guide
- Lists useful commands

**Run**: `python setup_utils.py`

#### [query_utils.py](query_utils.py)
Interactive analytics tool:
- View Bronze table
- View Silver tables (3 types)
- Count records
- Top clients by revenue
- Revenue by country
- Customer loyalty report
- Latest transactions
- Overall statistics

**Run**: `python query_utils.py` (interactive)  
**Or**: `python query_utils.py --batch` (all reports)

#### [check_setup.sh](check_setup.sh)
Bash script for setup verification:
- Checks system commands
- Verifies Kafka/Spark installed
- Checks if services running
- Validates project files
- Confirms data directories

**Run**: `bash check_setup.sh`

### Configuration Files

#### [config.ini](config.ini)
Application configuration with 30+ options:
- Kafka settings (bootstrap servers, topic)
- Spark settings (memory, partitions)
- Delta Lake paths
- Streaming settings (watermark)
- Producer settings (batch interval)
- Analytics thresholds
- Performance tuning options

Edit these to customize behavior.

#### [requirements.txt](requirements.txt)
Python package dependencies:
- pyspark==3.5.0
- kafka-python==2.0.2
- delta-spark==3.2.0
- numpy, pandas (optional)

Install with: `pip install -r requirements.txt`

---

## 🎯 Common Tasks

### I want to...

#### Start the streaming pipeline
1. Read: [QUICKSTART.md](QUICKSTART.md)
2. Open 6 terminals
3. Run commands in order
4. Watch data flow in Terminal 5

#### Understand the system design
1. Read: [ARCHITECTURE.md](ARCHITECTURE.md)
2. Review diagrams and flow charts
3. Check [spark_streaming_delta.py](spark_streaming_delta.py) code

#### Query and analyze data
1. Run: `python query_utils.py`
2. Select option from interactive menu
3. Or run: `python query_utils.py --batch`

#### Debug a problem
1. Search: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Find your error
3. Follow solution steps
4. Check diagnostic commands

#### Change how it works
1. Edit: [config.ini](config.ini)
2. Or edit: source Python files
3. Restart the affected component
4. Monitor output in terminal

#### Add new functionality
1. Study: [ARCHITECTURE.md](ARCHITECTURE.md)
2. Review: relevant Python file
3. Make changes (comments explain code)
4. Restart component
5. Validate output

#### Deploy to cloud
1. Read: Deployment section in [README.md](README.md)
2. Modify paths: `/tmp/delta` → cloud storage
3. Update Kafka: local → cloud broker
4. Adjust resources: memory, cores, workers

---

## 🚀 Quick Commands Reference

### Setup & Validation
```bash
python setup_utils.py           # Validate environment
bash check_setup.sh             # Check system (bash)
pip install -r requirements.txt # Install packages
```

### Start Pipeline (6 Terminals)
```bash
# Terminal 1: ZooKeeper
zookeeper-server-start /usr/local/etc/kafka/zookeeper.properties

# Terminal 2: Kafka
kafka-server-start /usr/local/etc/kafka/server.properties

# Terminal 3: Create Topic
kafka-topics --create --topic ventes_stream \
  --bootstrap-server localhost:9092 --partitions 1

# Terminal 4: Producer
python producer_ventes.py

# Terminal 5: Spark Consumer (with packages)
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,io.delta:delta-spark_2.12:3.2.0 spark_streaming_delta.py

# Terminal 6: Analytics (periodic)
spark-submit --packages io.delta:delta-spark_2.12:3.2.0 streaming_silver.py
```

### Query Data
```bash
python query_utils.py           # Interactive menu
python query_utils.py --batch   # All reports at once
```

### Monitor Services
```bash
jps | grep -E "Kafka|Zookeeper|Spark"  # Running services
lsof -i :9092                          # Kafka port
lsof -i :2181                          # ZooKeeper port
df -h /tmp/delta                       # Storage usage
```

---

## 📚 Learning Path

### Beginner (Day 1)
- [ ] Read [QUICKSTART.md](QUICKSTART.md) (5 min)
- [ ] Run `python setup_utils.py` (2 min)
- [ ] Start 6 terminals and observe (10 min)
- [ ] Run `python query_utils.py` and explore (10 min)
- [ ] **Total: 27 minutes** ✅

### Intermediate (Week 1)
- [ ] Read [README.md](README.md) (30 min)
- [ ] Study [ARCHITECTURE.md](ARCHITECTURE.md) (45 min)
- [ ] Review Python code comments (30 min)
- [ ] Modify producer_ventes.py (customization)
- [ ] Create new Silver aggregations
- [ ] **Total: 2-3 hours**

### Advanced (Ongoing)
- [ ] Deep-dive into specific components
- [ ] Add ML features or data quality
- [ ] Deploy to cloud
- [ ] Optimize performance
- [ ] Implement monitoring dashboard

---

## 🎓 Key Concepts Covered

| Concept | Files | Explanation |
|---------|-------|-------------|
| **Kafka Streaming** | producer_ventes.py, spark_streaming_delta.py | Real-time event streaming |
| **Spark Structured Streaming** | spark_streaming_delta.py | Processing streaming data |
| **Watermarking** | spark_streaming_delta.py, ARCHITECTURE.md | Handling late data |
| **Checkpointing** | spark_streaming_delta.py, ARCHITECTURE.md | Fault tolerance |
| **Delta Lake** | streaming_silver.py, README.md | ACID data lake |
| **Partitioning** | spark_streaming_delta.py, ARCHITECTURE.md | Performance optimization |
| **Aggregation** | streaming_silver.py | Data transformation |
| **Monitoring** | spark_streaming_delta.py, ARCHITECTURE.md | Observability |

---

## 🔗 Cross-References

### If you're reading...

**QUICKSTART.md** → Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if you hit issues

**README.md** → See [ARCHITECTURE.md](ARCHITECTURE.md) for deeper explanations

**ARCHITECTURE.md** → Reference [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for recovery

**PROJECT_SUMMARY.md** → Start with [QUICKSTART.md](QUICKSTART.md)

**spark_streaming_delta.py** → See [ARCHITECTURE.md](ARCHITECTURE.md) section on Watermarking

**streaming_silver.py** → Check [README.md](README.md) for schema details

---

## ✅ Getting Help

### Step-by-Step

1. **Does it show an error?**
   → Search [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

2. **Don't understand a concept?**
   → Read [ARCHITECTURE.md](ARCHITECTURE.md)

3. **How do I configure something?**
   → See [config.ini](config.ini) or [README.md](README.md)

4. **How do I run something?**
   → Check [QUICKSTART.md](QUICKSTART.md) or command header in files

5. **Want detailed documentation?**
   → Read [README.md](README.md) or [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

---

## 🎉 You're Ready!

Start here: **[QUICKSTART.md](QUICKSTART.md)**

Then explore: **[README.md](README.md)**

Dive deep: **[ARCHITECTURE.md](ARCHITECTURE.md)**

Happy Streaming! 🚀

---

**Last Updated**: December 12, 2024  
**Project Status**: ✅ Complete & Ready  
**Documentation Level**: Comprehensive  
**Difficulty**: Beginner → Advanced
