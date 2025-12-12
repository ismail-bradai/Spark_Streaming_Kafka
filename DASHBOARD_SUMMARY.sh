#!/bin/bash
# 📊 STREAMLIT DASHBOARD - FINAL SUMMARY & QUICK REFERENCE

cat << 'EOF'

╔═════════════════════════════════════════════════════════════════════════════╗
║                                                                             ║
║         🚀 SPARK STREAMING KAFKA + STREAMLIT DASHBOARD 🚀                  ║
║                      Complete Real-Time Visualization                       ║
║                                                                             ║
╚═════════════════════════════════════════════════════════════════════════════╝


✨ QUICK START (One Command!)
═════════════════════════════════════════════════════════════════════════════

  1️⃣  Start Everything:
      cd /home/ismail/projects/spark_streaming_kafka
      bash start_pipeline.sh

  2️⃣  Open Dashboard:
      http://localhost:8501

  3️⃣  Monitor Progress:
      bash check_status.sh


🌐 LIVE DASHBOARD
═════════════════════════════════════════════════════════════════════════════

   ✨ URL: http://localhost:8501
   
   📈 Real-Time Metrics
      • Total Records (cumulative)
      • Unique Clients (distinct count)
      • Unique Products (SKU count)
      • Total Revenue (sum)
      • Avg Transaction (mean)
   
   📊 Interactive Charts
      • Sales by Country (bar)
      • Top 10 Products (ranking)
      • Sales Timeline (line)
      • Raw Data Browser (table)
   
   ⚙️  Configuration
      • Auto-refresh rate (5-30 seconds)
      • System architecture
      • Monitoring commands
      • Help & troubleshooting


📡 SYSTEM COMPONENTS
═════════════════════════════════════════════════════════════════════════════

   Zookeeper ........... Port 2181 (Kafka coordinator)
   Kafka Broker ........ Port 9092 (Message broker)
   Spark Jobs .......... Local[2] (2 workers)
   Delta Lake .......... /tmp/delta/ (ACID storage)
   Streamlit ........... Port 8501 (Web dashboard)
   
   Producer ............ python3 producer_ventes.py
   Delta Job ........... spark_streaming_delta.py
   Silver Job .......... streaming_silver.py


🔍 MONITORING
═════════════════════════════════════════════════════════════════════════════

   View All Logs:
      tail -f /tmp/producer.log        # Messages generated
      tail -f /tmp/spark_delta.log     # Kafka ingestion
      tail -f /tmp/spark_silver.log    # Transformations
      tail -f /tmp/streamlit.log       # Dashboard

   Check Status:
      bash check_status.sh             # Full system health

   Query Data:
      spark-sql --master local[2] \\
        --packages io.delta:delta-spark_2.12:3.2.0 \\
        -e "SELECT COUNT(*) FROM delta.\`/tmp/delta/bronze/ventes_stream\`"


🛑 STOP ALL JOBS
═════════════════════════════════════════════════════════════════════════════

   pkill -f 'producer_ventes|spark_streaming|streamlit'


📁 PROJECT FILES
═════════════════════════════════════════════════════════════════════════════

   Core Streaming Jobs:
      📜 producer_ventes.py       - Generates sales messages
      📜 spark_streaming_delta.py - Kafka → Delta Bronze
      📜 streaming_silver.py      - Bronze → Silver (transformations)

   Visualization:
      📜 streamlit_dashboard.py   - Interactive web dashboard
      📜 STREAMLIT_GUIDE.md       - Dashboard documentation
      📜 DASHBOARD_README.md      - Complete guide

   Utilities:
      📜 query_utils.py           - Query helpers
      📜 setup_utils.py           - Setup functions
      📜 requirements.txt         - Python dependencies
      📜 config.ini               - Configuration

   Scripts:
      🔧 start_pipeline.sh        - Start entire system
      🔧 check_status.sh          - Verify system status
      🔧 check_setup.sh           - Verify setup


📊 DATA FLOW DIAGRAM
═════════════════════════════════════════════════════════════════════════════

   Producer (python3)
        ↓ 1 message every 2 seconds
   Kafka Topic: ventes_stream
        ↓ Kafka Consumer
   Spark Delta Job (reads Kafka)
        ↓ writeStream()
   Delta Lake Bronze (/tmp/delta/bronze/)
        ↓ readStream()
   Spark Silver Job (transformations)
        ↓ writeStream()
   Delta Lake Silver (/tmp/delta/silver/)
        ↓ Spark SQL Queries
   Streamlit Dashboard (http://localhost:8501)
        ↓ Auto-refresh every 5-30 seconds
   Web Browser Visualization


⚡ PERFORMANCE STATS
═════════════════════════════════════════════════════════════════════════════

   Message Rate:        ~30/minute (1 every 2 seconds)
   Kafka Partitions:    1
   Spark Workers:       2 (local[2])
   Memory (Kafka):      1 GB
   Memory (Spark):      2 GB
   Refresh Rate:        5-30 seconds (configurable)
   
   Expected Growth:
      1 minute:   ~30 records
      5 minutes:  ~150 records
      1 hour:     ~1,800 records
      1 day:      ~43,200 records


✅ SUCCESS CHECKLIST
═════════════════════════════════════════════════════════════════════════════

   [ ] Dashboard loads on http://localhost:8501
   [ ] Metrics update in real-time
   [ ] Charts display data correctly
   [ ] Raw data tab shows transactions
   [ ] Refresh rate is adjustable
   [ ] All logs are accessible
   [ ] Producer messages flowing
   [ ] Delta job ingesting data
   [ ] Silver job processing data


🎯 NEXT STEPS
═════════════════════════════════════════════════════════════════════════════

   1. Access Dashboard
      ➜ Open http://localhost:8501 in your browser

   2. Monitor System
      ➜ Run: bash check_status.sh
      ➜ Watch logs: tail -f /tmp/producer.log

   3. Explore Data
      ➜ Click on "Raw Data" tab to see transactions
      ➜ Scroll through sales records
      ➜ View data structure

   4. Observe Metrics
      ➜ Watch KPIs update every 5 seconds
      ➜ Notice records accumulating
      ➜ Track revenue growth

   5. Experiment
      ➜ Adjust refresh rate (sidebar)
      ➜ Increase producer rate (edit producer_ventes.py)
      ➜ Scale Spark workers


📚 DOCUMENTATION
═════════════════════════════════════════════════════════════════════════════

   START_HERE.txt      - First steps
   QUICKSTART.md       - Quick setup guide
   README.md           - Project overview
   ARCHITECTURE.md     - System design
   DASHBOARD_README.md - Dashboard documentation
   STREAMLIT_GUIDE.md  - Dashboard features & troubleshooting
   TROUBLESHOOTING.md  - Common issues & solutions


🐛 TROUBLESHOOTING
═════════════════════════════════════════════════════════════════════════════

   Dashboard not loading?
      pkill -f streamlit
      cd /home/ismail/projects/spark_streaming_kafka
      python3 -m streamlit run streamlit_dashboard.py --server.headless=true < /dev/null &

   No data showing?
      • Check producer: tail -f /tmp/producer.log
      • Check Delta job: tail -f /tmp/spark_delta.log
      • Check Bronze data: ls -la /tmp/delta/bronze/ventes_stream/

   Need fresh start?
      pkill -f 'producer|spark_streaming|streamlit'
      rm -rf /tmp/delta/
      bash start_pipeline.sh


🎓 LEARNING
═════════════════════════════════════════════════════════════════════════════

   Understand the Pipeline:
      1. Producer creates messages (JSON format)
      2. Kafka receives and stores messages
      3. Spark reads from Kafka (streaming)
      4. Delta Lake ACID writes to Bronze
      5. Silver job transforms Bronze data
      6. Streamlit queries Delta for visualization

   Key Concepts:
      • Kafka Topic: Named stream (like a table)
      • Partition: Parallel processing unit
      • Batch: Micro-batch of messages
      • Watermark: Late data cutoff
      • Delta Lake: Data lake with ACID
      • Bronze/Silver: Data quality layers


🚀 PRODUCTION DEPLOYMENT
═════════════════════════════════════════════════════════════════════════════

   Current Setup:
      ✅ Development environment (local machine)
      ✅ Single Kafka broker (1 partition)
      ✅ Local Spark (2 workers)
      ✅ Streamlit dashboard (web UI)

   To Scale:
      • Increase Kafka partitions (parallel ingestion)
      • Add Spark workers (distributed processing)
      • Increase producer rate (higher throughput)
      • Use cloud Kafka (AWS MSK, Confluent Cloud)
      • Deploy to Kubernetes (containerized)


═════════════════════════════════════════════════════════════════════════════

                    🎉 YOU'RE ALL SET! 🎉
                    
         Your real-time streaming analytics pipeline is ready!
         
         Open http://localhost:8501 in your browser now!

═════════════════════════════════════════════════════════════════════════════

EOF
