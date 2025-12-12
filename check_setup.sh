#!/usr/bin/env bash

# Real-Time Sales Streaming Lakehouse - Setup Checklist
# This script verifies all prerequisites before starting

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   Kafka + Spark Streaming + Delta Lake - Setup Checker    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

PASSED=0
FAILED=0

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✅${NC} $2"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌${NC} $2"
        ((FAILED++))
        return 1
    fi
}

check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo -e "${GREEN}✅${NC} Port $1 is open ($2)"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌${NC} Port $1 is not open ($2)"
        ((FAILED++))
        return 1
    fi
}

check_directory() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✅${NC} Directory exists: $1"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌${NC} Directory missing: $1"
        ((FAILED++))
        return 1
    fi
}

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} File exists: $1"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌${NC} File missing: $1"
        ((FAILED++))
        return 1
    fi
}

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 SYSTEM REQUIREMENTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_command "java" "Java installed"
check_command "python3" "Python 3 installed"
check_command "kafka-topics" "Kafka CLI tools installed"
check_command "spark-submit" "Apache Spark installed"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 PROJECT FILES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_file "producer_ventes.py" "Producer script"
check_file "spark_streaming_delta.py" "Spark streaming consumer"
check_file "streaming_silver.py" "Analytics pipeline"
check_file "requirements.txt" "Python dependencies"
check_file "README.md" "Documentation"
check_file "QUICKSTART.md" "Quick start guide"
check_file "ARCHITECTURE.md" "Architecture documentation"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 RUNNING SERVICES (Optional)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_port "2181" "ZooKeeper"
check_port "9092" "Kafka Broker"
check_port "4040" "Spark UI"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💾 DATA DIRECTORIES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_directory "/tmp/delta/bronze" "Bronze layer directory"
check_directory "/tmp/delta/silver" "Silver layer directory"
check_directory "/tmp/delta/checkpoints" "Checkpoint directory"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📈 SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo ""
echo "Checks passed: ${GREEN}$PASSED${NC}"
echo "Checks failed: ${RED}$FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ All checks passed! Ready to start.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Read: QUICKSTART.md"
    echo "2. Run: python setup_utils.py"
    echo "3. Open 6 terminals and follow the guide"
    exit 0
else
    echo ""
    echo -e "${YELLOW}⚠️  Some checks failed. Please fix issues above.${NC}"
    echo ""
    echo "Common fixes:"
    echo "• Install missing tools: brew install kafka spark"
    echo "• Create directories: mkdir -p /tmp/delta/{bronze,silver,checkpoints}"
    echo "• Start Kafka: kafka-server-start server.properties"
    echo "• Check documentation: see README.md"
    exit 1
fi
