#!/usr/bin/env python3
"""
Setup and Utility Script for Kafka + Spark Streaming + Delta Lake Project

Features:
- Verify environment and dependencies
- Create necessary directories
- Validate Kafka connectivity
- Display project structure
"""

import os
import sys
import subprocess
import json
from pathlib import Path

# Configuration
PROJECT_NAME = "Spark Streaming Lakehouse"
KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "ventes_stream"
DELTA_BASE = "/tmp/delta"

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

def check_python():
    """Check Python version"""
    print_header("Python Environment Check")
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 7:
        print_success("Python version is compatible")
        return True
    else:
        print_error("Python 3.7+ required")
        return False

def check_package(package_name):
    """Check if Python package is installed"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def check_dependencies():
    """Check required Python packages"""
    print_header("Dependencies Check")
    
    required_packages = {
        "pyspark": "PySpark",
        "kafka": "kafka-python",
        "delta": "delta-spark",
    }
    
    missing = []
    for package, name in required_packages.items():
        if check_package(package):
            print_success(f"{name} is installed")
        else:
            print_error(f"{name} is NOT installed")
            missing.append(name)
    
    if missing:
        print_warning(f"Install missing packages: pip install {' '.join([p.lower() for p in missing])}")
        return False
    return True

def check_kafka_connectivity():
    """Check Kafka broker connectivity"""
    print_header("Kafka Connectivity Check")
    
    try:
        from kafka import KafkaProducer
        from kafka.errors import KafkaError
        
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            request_timeout_ms=5000
        )
        producer.close()
        
        print_success(f"Connected to Kafka broker: {KAFKA_BROKER}")
        return True
    except Exception as e:
        print_error(f"Cannot connect to Kafka: {str(e)}")
        print_warning("Make sure ZooKeeper and Kafka broker are running:")
        print(f"  - ZooKeeper: zookeeper-server-start /usr/local/etc/kafka/zookeeper.properties")
        print(f"  - Kafka: kafka-server-start /usr/local/etc/kafka/server.properties")
        return False

def create_directories():
    """Create necessary Delta Lake directories"""
    print_header("Creating Delta Lake Directories")
    
    dirs = [
        f"{DELTA_BASE}/bronze/ventes_stream",
        f"{DELTA_BASE}/silver/ventes_aggreges",
        f"{DELTA_BASE}/silver/ventes_par_pays",
        f"{DELTA_BASE}/silver/ventes_par_segment",
        f"{DELTA_BASE}/checkpoints/ventes_bronze",
    ]
    
    for dir_path in dirs:
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            print_success(f"Directory created/verified: {dir_path}")
        except Exception as e:
            print_error(f"Failed to create directory {dir_path}: {e}")
            return False
    
    return True

def display_project_structure():
    """Display project directory structure"""
    print_header("Project Structure")
    
    structure = """
spark_streaming_kafka/
├── producer_ventes.py           (Kafka Producer - Sales Simulator)
├── spark_streaming_delta.py     (Spark Consumer - Bronze Layer)
├── streaming_silver.py          (Analytics Pipeline - Silver Layer)
├── README.md                    (Documentation)
├── setup_utils.py               (This script)
└── requirements.txt             (Python dependencies)

Data Storage:
/tmp/delta/
├── bronze/
│   ├── ventes_stream/          (Raw sales data)
│   └── checkpoints/            (Streaming checkpoints)
├── silver/
│   ├── ventes_aggreges/        (Client aggregation)
│   ├── ventes_par_pays/        (Country analysis)
│   └── ventes_par_segment/     (Segment analysis)
"""
    print(structure)

def generate_requirements_file():
    """Generate requirements.txt"""
    print_header("Generating Requirements File")
    
    requirements = """# Kafka + Spark Streaming + Delta Lake Project
pyspark==3.5.0
kafka-python==2.0.2
delta-spark==3.2.0
"""
    
    try:
        with open("requirements.txt", "w") as f:
            f.write(requirements)
        print_success("requirements.txt created")
        print_info("Install with: pip install -r requirements.txt")
        return True
    except Exception as e:
        print_error(f"Failed to create requirements.txt: {e}")
        return False

def display_execution_guide():
    """Display step-by-step execution guide"""
    print_header("Execution Guide - 6 Terminals")
    
    guide = """
Terminal 1: Start ZooKeeper
─────────────────────────────────────────────
$ zookeeper-server-start /usr/local/etc/kafka/zookeeper.properties

Terminal 2: Start Kafka Broker
─────────────────────────────────────────────
$ kafka-server-start /usr/local/etc/kafka/server.properties

Terminal 3: Create Kafka Topic
─────────────────────────────────────────────
$ kafka-topics --create --topic ventes_stream \\
  --bootstrap-server localhost:9092 \\
  --partitions 1 --replication-factor 1

Terminal 4: Run Sales Producer
─────────────────────────────────────────────
$ python producer_ventes.py

Terminal 5: Run Spark Streaming Consumer (Bronze)
─────────────────────────────────────────────
$ spark-submit \\
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,io.delta:delta-spark_2.12:3.2.0 \\
  spark_streaming_delta.py

Terminal 6: Run Silver Layer Analytics (Optional, run periodically)
─────────────────────────────────────────────
$ spark-submit \\
  --packages io.delta:delta-spark_2.12:3.2.0 \\
  streaming_silver.py

All running together:
├─ Producer sends sales → Kafka
├─ Streaming consumer reads Kafka → Bronze (Delta Lake)
└─ Analytics job reads Bronze → Silver (aggregations)
"""
    print(guide)

def display_commands():
    """Display useful Kafka and Spark commands"""
    print_header("Useful Commands")
    
    commands = """
📨 Kafka Commands
─────────────────────────────────────────────
# List topics
kafka-topics --list --bootstrap-server localhost:9092

# Describe topic
kafka-topics --describe --topic ventes_stream --bootstrap-server localhost:9092

# Monitor topic in real-time
kafka-console-consumer --bootstrap-server localhost:9092 \\
  --topic ventes_stream --from-beginning

# Check consumer group lag
kafka-consumer-groups --bootstrap-server localhost:9092 --list

# Delete topic (if needed)
kafka-topics --delete --topic ventes_stream --bootstrap-server localhost:9092


🔥 Spark Commands
─────────────────────────────────────────────
# Submit with memory allocation
spark-submit --driver-memory 4g --executor-memory 2g script.py

# Submit with verbose logging
spark-submit --verbose script.py

# Run in local mode with all cores
spark-submit --master local[*] script.py


📊 Delta Lake Commands (PySpark)
─────────────────────────────────────────────
# Read and display data
from delta import DeltaTable
dt = DeltaTable.forPath(spark, '/tmp/delta/bronze/ventes_stream')
dt.toDF().show()

# Show Delta table history
dt.history().show()

# Optimize table (compact files)
dt.optimize().executeCompaction()

# Vacuum old versions (cleanup)
dt.vacuum(24)  # Keep 24 hours of history
"""
    print(commands)

def validate_setup():
    """Run all validation checks"""
    print_header(f"🚀 {PROJECT_NAME} - Setup Validator")
    
    checks = [
        ("Python Environment", check_python),
        ("Python Dependencies", check_dependencies),
        ("Kafka Connectivity", check_kafka_connectivity),
        ("Directory Creation", create_directories),
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print_error(f"{check_name}: {str(e)}")
            all_passed = False
    
    return all_passed

def main():
    """Main setup routine"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print(r"""
    ╔═══════════════════════════════════════════════════════════╗
    ║   Kafka + Spark Streaming + Delta Lake Setup Utility     ║
    ║                                                           ║
    ║   Real-Time Sales Data Lakehouse Architecture            ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    print(f"{Colors.RESET}")
    
    # Run validation
    if validate_setup():
        print_success("All validation checks passed! ✨")
    else:
        print_error("Some checks failed. Please fix issues above.")
        sys.exit(1)
    
    # Generate requirements
    generate_requirements_file()
    
    # Display information
    display_project_structure()
    display_execution_guide()
    display_commands()
    
    print_header("✅ Setup Complete")
    print("""
You're ready to start the streaming pipeline!

Next Steps:
1. Open 6 terminal windows
2. Follow the Execution Guide above
3. Monitor data flowing through the pipeline
4. Check Silver analytics output

For detailed documentation, see: README.md
    """)

if __name__ == "__main__":
    main()
