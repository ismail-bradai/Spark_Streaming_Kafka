#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
# STREAMLIT DASHBOARD - QUICK START GUIDE
# ═══════════════════════════════════════════════════════════════════════════════

# This script shows how to start the complete streaming pipeline with visualization

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║          SPARK STREAMING KAFKA + STREAMLIT DASHBOARD                     ║"
echo "║                        QUICK START GUIDE                                 ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"

PROJECT_DIR="/home/ismail/projects/spark_streaming_kafka"
KAFKA_DIR="/home/ismail/apps/kafka_2.13-3.7.1"
SPARK_DIR="/home/ismail/apps/spark-3.5.0-bin-hadoop3"

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1: START KAFKA INFRASTRUCTURE
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo "📍 STEP 1: Starting Kafka Infrastructure..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Start Zookeeper
echo "Starting Zookeeper..."
cd $KAFKA_DIR
nohup bin/zookeeper-server-start.sh config/zookeeper.properties > logs/zookeeper.log 2>&1 &
sleep 3

# Start Kafka Broker
echo "Starting Kafka Broker..."
nohup bin/kafka-server-start.sh config/server.properties > logs/kafka.log 2>&1 &
sleep 3

# Create/Recreate topic
echo "Creating Kafka topic 'ventes_stream'..."
bin/kafka-topics.sh --delete --topic ventes_stream --bootstrap-server localhost:9092 2>/dev/null
sleep 1
bin/kafka-topics.sh --create --topic ventes_stream --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1

echo "✅ Kafka infrastructure ready"

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2: START STREAMING JOBS
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo "📍 STEP 2: Starting Streaming Jobs..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd $PROJECT_DIR

# Start Producer
echo "Starting Producer (python3 producer_ventes.py)..."
nohup python3 producer_ventes.py > /tmp/producer.log 2>&1 &
PRODUCER_PID=$!
echo "  Producer PID: $PRODUCER_PID"

# Start Delta Job
echo "Starting Delta Job (spark_streaming_delta.py)..."
nohup $SPARK_DIR/bin/spark-submit --master local[2] \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,io.delta:delta-spark_2.12:3.2.0 \
  spark_streaming_delta.py > /tmp/spark_delta.log 2>&1 &
DELTA_PID=$!
echo "  Delta Job PID: $DELTA_PID"

# Start Silver Job
echo "Starting Silver Job (streaming_silver.py)..."
nohup $SPARK_DIR/bin/spark-submit --master local[2] \
  --packages io.delta:delta-spark_2.12:3.2.0 \
  streaming_silver.py > /tmp/spark_silver.log 2>&1 &
SILVER_PID=$!
echo "  Silver Job PID: $SILVER_PID"

sleep 5
echo "✅ Streaming jobs started"

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3: START STREAMLIT DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo "📍 STEP 3: Starting Streamlit Dashboard..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "Starting Streamlit (streamlit_dashboard.py)..."
nohup streamlit run streamlit_dashboard.py --logger.level=error > /tmp/streamlit.log 2>&1 &
STREAMLIT_PID=$!
echo "  Streamlit PID: $STREAMLIT_PID"

sleep 3
echo "✅ Streamlit dashboard started"

# ═══════════════════════════════════════════════════════════════════════════════
# FINAL STATUS
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                    🎉 SYSTEM FULLY DEPLOYED 🎉                          ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"

echo ""
echo "📊 DASHBOARD ACCESS:"
echo "   🌐 Open your browser and go to: http://localhost:8501"
echo "   📈 View real-time metrics and visualizations"

echo ""
echo "📋 MONITORING COMMANDS:"
echo "   Producer:    tail -f /tmp/producer.log"
echo "   Delta Job:   tail -f /tmp/spark_delta.log"
echo "   Silver Job:  tail -f /tmp/spark_silver.log"
echo "   Dashboard:   tail -f /tmp/streamlit.log"

echo ""
echo "🛑 STOP ALL JOBS:"
echo "   pkill -f 'producer_ventes|spark_streaming|streamlit'"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ System is ready! Messages are flowing and dashboard is live ✨"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
