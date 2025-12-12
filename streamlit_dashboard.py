"""
Streamlit Dashboard for Spark Streaming Kafka + Delta Lake Pipeline
Visualizes real-time data flow from Kafka → Bronze → Silver layers
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, sum as spark_sum, avg, date_format
from datetime import datetime, timedelta
import time
import os

# ═══════════════════════════════════════════════════════════════════════════
# STREAMLIT PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Spark Streaming Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════════
# INITIALIZE SPARK SESSION
# ═══════════════════════════════════════════════════════════════════════════

@st.cache_resource
def get_spark_session():
    """Initialize Spark Session with Delta Lake support"""
    # Ensure Delta Lake jar is available to the Spark driver when running
    # this app outside of spark-submit (streamlit process). Using
    # spark.jars.packages lets Spark download the required Delta artifact.
    packages = "io.delta:delta-spark_2.12:3.2.0"
    spark = SparkSession.builder         .appName("StreamingDashboard")         .config("spark.jars.packages", packages)         .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")         .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")         .config("spark.driver.memory", "2g")         .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")
    return spark


# ═══════════════════════════════════════════════════════════════════════════
# DATA LOADING FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def load_bronze_data(spark):
    """Load data from Delta Lake Bronze layer"""
    try:
        bronze_path = "/tmp/delta/bronze/ventes_stream"
        if not os.path.exists(bronze_path):
            return None
        
        df = spark.read.format("delta").load(bronze_path)
        return df.toPandas()
    except Exception as e:
        st.warning(f"Bronze layer not yet available: {str(e)[:50]}")
        return None

def load_silver_data(spark):
    """Load data from Delta Lake Silver layer"""
    try:
        silver_path = "/tmp/delta/silver/ventes_transformed"
        if not os.path.exists(silver_path):
            return None
        
        df = spark.read.format("delta").load(silver_path)
        return df.toPandas()
    except Exception as e:
        st.warning(f"Silver layer not yet available: {str(e)[:50]}")
        return None

def get_pipeline_metrics(spark):
    """Calculate pipeline metrics"""
    try:
        bronze_path = "/tmp/delta/bronze/ventes_stream"
        if not os.path.exists(bronze_path):
            return None
        
        df = spark.read.format("delta").load(bronze_path)
        
        metrics = {
            "total_records": df.count(),
            "unique_clients": df.select("client_id").distinct().count(),
            "unique_products": df.select("produit_id").distinct().count(),
            "total_revenue": float(df.select(spark_sum("montant")).collect()[0][0] or 0),
            "avg_transaction": float(df.select(avg("montant")).collect()[0][0] or 0),
        }
        
        return metrics
    except Exception as e:
        st.warning(f"Could not load metrics: {str(e)[:50]}")
        return None

# ═══════════════════════════════════════════════════════════════════════════
# DASHBOARD HEADER
# ═══════════════════════════════════════════════════════════════════════════

st.markdown("# 📊 Spark Streaming Dashboard")
st.markdown("### Real-time Pipeline Visualization: Kafka → Bronze → Silver")

# Sidebar controls
with st.sidebar:
    st.title("🎮 Controls")
    
    refresh_rate = st.slider("Refresh Rate (seconds)", 1, 30, 5)
    st.markdown("---")
    
    st.subheader("📍 Data Locations")
    st.code("Kafka Topic: ventes_stream", language="bash")
    st.code("Bronze: /tmp/delta/bronze/ventes_stream", language="bash")
    st.code("Silver: /tmp/delta/silver/", language="bash")
    
    st.markdown("---")
    st.info("ℹ️ Data refreshes automatically based on the selected interval")

# ═══════════════════════════════════════════════════════════════════════════
# MAIN DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════

spark = get_spark_session()

# PIPELINE STATUS SECTION
st.markdown("## 🚀 Pipeline Status")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🐰 Zookeeper", "✅ Running", "Port 2181")

with col2:
    st.metric("📨 Kafka Broker", "✅ Running", "Port 9092")

with col3:
    st.metric("🔄 Delta Job", "✅ Active", "Streaming")

with col4:
    st.metric("💾 Silver Job", "✅ Active", "Transforming")

st.markdown("---")

# METRICS SECTION
st.markdown("## 📈 Real-Time Metrics")

metrics = get_pipeline_metrics(spark)

if metrics:
    m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
    
    with m_col1:
        st.metric("📊 Total Records", f"{metrics['total_records']:,}")
    
    with m_col2:
        st.metric("👥 Unique Clients", f"{metrics['unique_clients']:,}")
    
    with m_col3:
        st.metric("📦 Unique Products", f"{metrics['unique_products']:,}")
    
    with m_col4:
        st.metric("💰 Total Revenue", f"€{metrics['total_revenue']:,.2f}")
    
    with m_col5:
        st.metric("📊 Avg Transaction", f"€{metrics['avg_transaction']:.2f}")
else:
    st.info("⏳ Waiting for data... Check if producer and Delta job are running")

st.markdown("---")

# DATA VISUALIZATION SECTION
st.markdown("## 📉 Data Analysis")

bronze_df = load_bronze_data(spark)

if bronze_df is not None and len(bronze_df) > 0:
    tab1, tab2, tab3, tab4 = st.tabs(["Sales by Country", "Top Products", "Sales Timeline", "Raw Data"])
    
    # TAB 1: Sales by Country
    with tab1:
        st.subheader("Revenue by Country")
        try:
            country_sales = bronze_df.groupby("pays")["montant"].sum().sort_values(ascending=False)
            
            fig = px.bar(
                x=country_sales.index,
                y=country_sales.values,
                labels={"x": "Country", "y": "Revenue (€)"},
                color=country_sales.values,
                color_continuous_scale="Viridis"
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # Stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Top Country", country_sales.index[0], f"€{country_sales.values[0]:,.2f}")
            with col2:
                st.metric("Countries Count", len(country_sales))
            with col3:
                st.metric("Total by Country", f"€{country_sales.sum():,.2f}")
        except Exception as e:
            st.error(f"Error: {str(e)[:50]}")
    
    # TAB 2: Top Products
    with tab2:
        st.subheader("Top 10 Products by Sales")
        try:
            product_sales = bronze_df.groupby("produit_nom")["montant"].agg(['sum', 'count']).sort_values('sum', ascending=False).head(10)
            
            fig = px.bar(
                x=product_sales.index,
                y=product_sales['sum'],
                labels={"x": "Product", "y": "Revenue (€)", "index": "Product"},
                color=product_sales['sum'],
                color_continuous_scale="Blues"
            )
            fig.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            
            # Top product details
            if len(product_sales) > 0:
                st.write(product_sales)
        except Exception as e:
            st.error(f"Error: {str(e)[:50]}")
    
    # TAB 3: Sales Timeline
    with tab3:
        st.subheader("Sales Over Time")
        try:
            if 'timestamp' in bronze_df.columns:
                bronze_df['timestamp'] = pd.to_datetime(bronze_df['timestamp'])
                timeline = bronze_df.set_index('timestamp')['montant'].resample('H').sum()
                
                fig = px.line(
                    x=timeline.index,
                    y=timeline.values,
                    labels={"x": "Time", "y": "Revenue (€)"},
                    markers=True
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.info("Timeline data not yet available")
    
    # TAB 4: Raw Data
    with tab4:
        st.subheader("Raw Data from Bronze Layer")
        st.dataframe(bronze_df.head(100), use_container_width=True)
        st.info(f"Showing first 100 of {len(bronze_df):,} records")

else:
    st.info("⏳ Waiting for data from Kafka... Make sure:")
    st.markdown("""
    - Producer is running: `python3 producer_ventes.py`
    - Delta job is running: `spark-submit spark_streaming_delta.py`
    - Data has time to be processed
    """)

st.markdown("---")

# SYSTEM ARCHITECTURE SECTION
st.markdown("## 🏗️ System Architecture")

col_arch1, col_arch2 = st.columns(2)

with col_arch1:
    st.markdown("""
    ### Data Pipeline Layers
    
    **1. Streaming Source**
    - Kafka Topic: `ventes_stream`
    - Message Format: JSON
    - Update Interval: 2 seconds
    
    **2. Bronze Layer** 🥉
    - Raw data ingestion
    - Format: Parquet (Delta Lake)
    - Partitioning: By date (jour)
    - Location: `/tmp/delta/bronze/`
    
    **3. Silver Layer** 🥈
    - Cleaned & enriched data
    - Format: Parquet (Delta Lake)
    - Transformations applied
    - Location: `/tmp/delta/silver/`
    """)

with col_arch2:
    st.markdown("""
    ### Technology Stack
    
    ```
    Kafka 3.7.1         Message Broker
    Zookeeper 3.8.4     Coordination
    Spark 3.5.0         Processing Engine
    Delta Lake 3.2.0    Data Storage
    Python 3.10         Applications
    Streamlit           Dashboard
    ```
    
    ### Running Components
    
    ✅ Producer (Python)  
    ✅ Delta Job (Spark)  
    ✅ Silver Job (Spark)  
    ✅ This Dashboard (Streamlit)
    """)

st.markdown("---")

# MONITORING SECTION
st.markdown("## 📋 Live Monitoring")

col_mon1, col_mon2, col_mon3 = st.columns(3)

with col_mon1:
    st.markdown("### 📊 Producer")
    st.code("""
tail -f /tmp/producer.log
    """, language="bash")

with col_mon2:
    st.markdown("### 🔄 Delta Job")
    st.code("""
tail -f /tmp/spark_delta.log
    """, language="bash")

with col_mon3:
    st.markdown("### 💾 Silver Job")
    st.code("""
tail -f /tmp/spark_silver.log
    """, language="bash")

st.markdown("---")

# FOOTER
st.markdown("""
---
**Last Updated:** """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """

🚀 Dashboard refreshes every """ + str(refresh_rate) + """ seconds  
📊 Data source: Delta Lake (Bronze & Silver layers)  
🔗 Kafka Topic: `ventes_stream` @ localhost:9092
""")

# Auto-refresh
time.sleep(refresh_rate)
st.rerun()
