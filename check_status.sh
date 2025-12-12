#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
# COMPLETE SYSTEM VERIFICATION & STATUS CHECK
# ═══════════════════════════════════════════════════════════════════════════════

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║            SPARK STREAMING KAFKA + STREAMLIT PIPELINE STATUS            ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"

# ═══════════════════════════════════════════════════════════════════════════════
# 1. CHECK INFRASTRUCTURE SERVICES
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo "📍 INFRASTRUCTURE STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo -n "Zookeeper (Port 2181)... "
if nc -z localhost 2181 2>/dev/null; then
    echo "✅ Running"
else
    echo "❌ Not responding"
fi

echo -n "Kafka Broker (Port 9092)... "
if nc -z localhost 9092 2>/dev/null; then
    echo "✅ Running"
else
    echo "❌ Not responding"
fi

echo -n "Streamlit Dashboard (Port 8501)... "
if curl -s http://localhost:8501 > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not responding"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 2. CHECK STREAMING JOBS
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo "📍 STREAMING JOBS STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "Running Processes:"
ps aux | grep -E 'producer_ventes|spark_streaming_delta|streaming_silver|streamlit' | grep -v grep | awk '{
    cmd=$12;
    if ($12 ~ /producer/) print "  ✅ Producer (python3) - PID: " $2;
    else if ($11 ~ /spark-submit|java/) {
        if (NR == 1) print "  ✅ Delta Job (Spark) - PID: " $2;
        else print "  ✅ Silver Job (Spark) - PID: " $2;
    }
    else if ($11 ~ /streamlit/) print "  ✅ Dashboard (Streamlit) - PID: " $2;
}'

# ═══════════════════════════════════════════════════════════════════════════════
# 3. CHECK DATA DIRECTORIES
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo "📍 DATA STORAGE STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo -n "Bronze Layer (/tmp/delta/bronze/)... "
if [ -d /tmp/delta/bronze/ventes_stream ]; then
    COUNT=$(find /tmp/delta/bronze/ventes_stream -name "*.parquet" 2>/dev/null | wc -l)
    echo "✅ ($COUNT parquet files)"
else
    echo "⚠️  Directory not found"
fi

echo -n "Silver Layer (/tmp/delta/silver/)... "
if [ -d /tmp/delta/silver ]; then
    COUNT=$(find /tmp/delta/silver -name "*.parquet" 2>/dev/null | wc -l)
    if [ $COUNT -gt 0 ]; then
        echo "✅ ($COUNT parquet files)"
    else
        echo "⚠️  No data yet"
    fi
else
    echo "⚠️  Directory not found"
fi

echo -n "Checkpoints... "
if [ -d /tmp/delta/checkpoints ]; then
    echo "✅ Available"
else
    echo "⚠️  Not found"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 4. CHECK MESSAGE FLOW
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo "📍 MESSAGE FLOW"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "Producer Messages:"
if [ -f /tmp/producer.log ]; then
    MSG_COUNT=$(grep -c "Message published" /tmp/producer.log 2>/dev/null || echo "0")
    ERROR_COUNT=$(grep -c "ERROR\|Exception" /tmp/producer.log 2>/dev/null || echo "0")
    echo "  ✅ Total messages: $MSG_COUNT"
    echo "  ℹ️  Errors logged: $ERROR_COUNT"
else
    echo "  ⚠️  No log file found"
fi

echo "Delta Job Ingestion:"
if [ -f /tmp/spark_delta.log ]; then
    BATCH_COUNT=$(grep -c "batchId" /tmp/spark_delta.log 2>/dev/null || echo "0")
    echo "  ✅ Batches processed: $BATCH_COUNT"
else
    echo "  ⚠️  No log file found"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 5. QUICK STATS
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo "📍 QUICK STATISTICS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "System Uptime:"
UPTIME=$(ps aux | grep "zookeeper-server" | grep -v grep | awk '{print $22}' 2>/dev/null || echo "Unknown")
echo "  Zookeeper started: $UPTIME"

echo ""
echo "Available Commands:"
echo "  tail -f /tmp/producer.log        → Producer messages"
echo "  tail -f /tmp/spark_delta.log     → Delta job ingestion"
echo "  tail -f /tmp/spark_silver.log    → Silver job transformations"
echo "  tail -f /tmp/streamlit.log       → Dashboard logs"

# ═══════════════════════════════════════════════════════════════════════════════
# 6. FINAL STATUS
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║                    🎯 SYSTEM STATUS COMPLETE 🎯                         ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"

echo ""
echo "🌐 ACCESS DASHBOARD:"
echo "   Browser: http://localhost:8501"
echo ""
echo "📊 VISUALIZATION FEATURES:"
echo "   ✨ Real-time metrics (updated every 5 seconds)"
echo "   ✨ Sales by country (bar chart)"
echo "   ✨ Top products (rankings)"
echo "   ✨ Sales timeline (trends)"
echo "   ✨ Raw data (Bronze layer records)"
echo "   ✨ Configurable refresh rate"
echo ""
