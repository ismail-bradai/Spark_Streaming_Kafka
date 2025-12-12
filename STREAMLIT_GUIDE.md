# 📊 Streamlit Dashboard Guide

## Overview

The Streamlit dashboard provides **real-time visualization** of your Spark Streaming Kafka pipeline. It connects directly to Delta Lake (Bronze and Silver layers) to display live metrics, charts, and data insights.

## 🚀 Quick Start

### 1. Access the Dashboard
Once the dashboard is running, open your browser:
```
http://localhost:8501
```

### 2. Dashboard Components

#### 🔴 Real-time Metrics (Top of Page)
Shows 5 key performance indicators updated every 5 seconds:
- **Total Records**: Cumulative messages processed
- **Unique Clients**: Count of distinct client IDs
- **Unique Products**: Count of distinct product IDs  
- **Total Revenue**: Sum of all transaction amounts
- **Avg Transaction**: Average sale amount

#### 📈 Visualizations (4 Tabs)

**Tab 1: Sales by Country**
- Bar chart showing total revenue per country
- Interactive Plotly chart (hover for details)
- Updates every 5 seconds

**Tab 2: Top 10 Products**
- Bar chart of best-selling products by volume
- Product names and quantities
- Real-time ranking updates

**Tab 3: Sales Timeline**
- Line chart showing sales volume over time
- X-axis: Timestamp
- Y-axis: Cumulative sales count
- Shows trends in message flow

**Tab 4: Raw Data**
- Displays Bronze layer data as pandas DataFrame
- Shows last 100 records
- Columns: vente_id, client_id, produit_id, montant, timestamp, etc.
- Searchable and sortable

#### ⚙️ Configuration Sidebar
- **Refresh Rate**: Adjust auto-refresh interval (5-30 seconds)
- **System Architecture**: View diagram of pipeline
- **Monitoring Commands**: Copy-paste terminal commands
- **Help & Troubleshooting**: Common issues

## 📁 Data Sources

### Bronze Layer
- **Location**: `/tmp/delta/bronze/ventes_stream/`
- **Format**: Delta Lake (Parquet files)
- **Content**: Raw messages from Kafka (1:1 mapping)
- **Partitioning**: By date (jour column)

### Silver Layer
- **Location**: `/tmp/delta/silver/`
- **Format**: Delta Lake (Parquet files)
- **Content**: Transformed and cleaned data
- **Current Status**: Reading from Bronze, transformations ongoing

## 🔄 How It Works

```
Kafka Producer
      ↓
  Kafka Topic: ventes_stream
      ↓
spark_streaming_delta.py (consumes Kafka)
      ↓
Delta Lake Bronze (/tmp/delta/bronze/)
      ↓
streaming_silver.py (Bronze → Silver transformations)
      ↓
Delta Lake Silver (/tmp/delta/silver/)
      ↓
streamlit_dashboard.py (reads both layers for visualization)
      ↓
http://localhost:8501 (web browser)
```

## 📊 Metrics Explanation

### Total Records
- Counts all rows in Bronze Delta table
- Increases as producer sends messages and Delta job ingests them
- Real indicator of data flow velocity

### Unique Clients
- `SELECT DISTINCT(client_id) FROM bronze`
- Shows customer base diversity
- Should grow as new clients are added

### Unique Products
- `SELECT DISTINCT(produit_id) FROM bronze`
- Shows product catalog utilization
- Indicates product variety in sales

### Total Revenue
- Sum of `montant` column across all records
- Increases as more sales flow through
- Business KPI metric

### Avg Transaction
- Mean of `montant` across all records
- Indicates average transaction size
- Business profitability indicator

## 🔍 Monitoring

### View Dashboard Logs
```bash
tail -f /tmp/streamlit.log
```

### View Kafka Producer Activity
```bash
tail -f /tmp/producer.log
```

### View Delta Job (Kafka ingestion)
```bash
tail -f /tmp/spark_delta.log
```

### View Silver Job (Transformations)
```bash
tail -f /tmp/spark_silver.log
```

## 🐛 Troubleshooting

### Dashboard Not Loading
**Problem**: Browser shows "Connection refused" or "Cannot reach localhost:8501"

**Solution**:
```bash
# Check if Streamlit is running
ps aux | grep streamlit

# Check logs
cat /tmp/streamlit.log

# Restart dashboard
pkill -f streamlit
cd /home/ismail/projects/spark_streaming_kafka
streamlit run streamlit_dashboard.py
```

### No Data Showing
**Problem**: Dashboard loads but all metrics show 0

**Solution**:
1. Check if producer is running: `tail -f /tmp/producer.log`
2. Check if Delta job is running: `tail -f /tmp/spark_delta.log`
3. Check if Bronze data exists: `ls -la /tmp/delta/bronze/ventes_stream/`

```bash
# If nothing exists, restart entire pipeline
pkill -f 'producer|spark_streaming|streamlit'
sleep 2
bash start_pipeline.sh
```

### Charts Not Updating
**Problem**: Metrics show data but charts are empty

**Solution**:
1. Streamlit may need more data to accumulate
2. Wait 1-2 minutes for data to flow through
3. Manually refresh browser (F5)
4. Check refresh rate setting (sidebar)

### Performance Issues
**Problem**: Dashboard is slow or unresponsive

**Solution**:
1. Reduce refresh rate to 15-30 seconds (sidebar)
2. Limit data loaded: edit `streamlit_dashboard.py`
3. Monitor system resources: `top` or `htop`
4. Restart Streamlit: `pkill -f streamlit && streamlit run streamlit_dashboard.py`

## 💡 Advanced Usage

### Custom Queries
Edit `streamlit_dashboard.py` to add custom Spark SQL queries:

```python
def get_custom_metrics(spark):
    df = spark.sql("""
        SELECT 
            categorie,
            COUNT(*) as count,
            SUM(montant) as revenue
        FROM bronze_data
        GROUP BY categorie
    """)
    return df

# In main Streamlit app:
custom_df = get_custom_metrics(spark)
st.bar_chart(custom_df)
```

### Add New Visualizations
```python
# In streamlit_dashboard.py, add to tabs:
with tab5:
    st.subheader("Custom Chart")
    custom_data = load_custom_data(spark)
    st.line_chart(custom_data)
```

### Export Data
```bash
# Export Bronze data to CSV
spark-sql --master local[2] \
  --packages io.delta:delta-spark_2.12:3.2.0 \
  -e "SELECT * FROM delta.\`/tmp/delta/bronze/ventes_stream\` LIMIT 10000" \
  | head -100
```

## 🔧 Configuration

### Adjust Refresh Rate
In Streamlit sidebar, change "Refresh Rate (seconds)" to your preferred interval.

### Change Dashboard Port
```bash
streamlit run streamlit_dashboard.py --server.port 8502
```

### Run in Production Mode
```bash
streamlit run streamlit_dashboard.py \
  --logger.level=error \
  --client.showErrorDetails=false \
  --client.toolbar.mode=minimal
```

## 📈 Expected Data Growth

| Time | Records | Unique Clients | Revenue |
|------|---------|-----------------|---------|
| 1 min | ~30 | 5-8 | $1,000-2,000 |
| 5 min | ~150 | 15-20 | $5,000-10,000 |
| 10 min | ~300 | 25-30 | $10,000-20,000 |
| 1 hour | ~1,800 | 50-75 | $50,000-100,000 |

(Values depend on producer configuration and message generation rate)

## ✅ Success Indicators

- ✅ Dashboard loads on `http://localhost:8501`
- ✅ Metrics show non-zero values
- ✅ Charts display data and update smoothly
- ✅ Refresh rate is configurable
- ✅ Raw data tab shows recent transactions
- ✅ Logs show successful Spark queries

## 📝 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Producer (Python)                     │
│         Generates sales transactions every 2s           │
└────────────────────────┬────────────────────────────────┘
                         │ JSON messages
                         ↓
┌─────────────────────────────────────────────────────────┐
│              Kafka Broker (Port 9092)                   │
│           Topic: ventes_stream (1 partition)            │
└────────────────────────┬────────────────────────────────┘
                         │ Kafka Consumer
                         ↓
┌─────────────────────────────────────────────────────────┐
│        Delta Streaming Job (Spark SQL)                  │
│  Watermark: 10 minutes, Partition by: jour (date)      │
└────────────────────────┬────────────────────────────────┘
                         │ writeStream()
                         ↓
┌─────────────────────────────────────────────────────────┐
│   Delta Lake Bronze Layer (/tmp/delta/bronze/)         │
│        Format: Parquet + Delta Transactions            │
│        Checkpoint: /tmp/delta/checkpoints/             │
└────────────────────────┬────────────────────────────────┘
                         │ readStream()
                         ↓
┌─────────────────────────────────────────────────────────┐
│        Silver Streaming Job (Transformations)          │
│     Cleaning, enrichment, aggregations applied         │
└────────────────────────┬────────────────────────────────┘
                         │ Silver transformations
                         ↓
┌─────────────────────────────────────────────────────────┐
│   Delta Lake Silver Layer (/tmp/delta/silver/)         │
│        Curated, clean data ready for analytics         │
└────────────────────────┬────────────────────────────────┘
                         │ Spark SQL Queries
                         ↓
┌─────────────────────────────────────────────────────────┐
│        Streamlit Dashboard (Python)                    │
│     Real-time metrics and visualization charts        │
└────────────────────────┬────────────────────────────────┘
                         │ Web Server
                         ↓
┌─────────────────────────────────────────────────────────┐
│    Web Browser http://localhost:8501                   │
│           Live Dashboard Visualization                 │
└─────────────────────────────────────────────────────────┘
```

## 🎯 Next Steps

1. **Access Dashboard**: Open http://localhost:8501 in your browser
2. **Monitor Metrics**: Watch real-time KPIs update
3. **Explore Data**: View raw data in the Raw Data tab
4. **Adjust Refresh**: Set optimal refresh rate for your use case
5. **Check Logs**: Monitor job logs for any issues
6. **Scale Up**: When satisfied, scale to larger data volumes

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review logs in `/tmp/*.log`
3. Verify all processes are running: `ps aux | grep -E 'producer|spark_streaming|streamlit'`
4. Restart pipeline: `bash start_pipeline.sh`

---

**Status**: ✅ Dashboard fully operational and ready for use
**Last Updated**: Auto-refresh enabled (configurable in sidebar)
**Data Source**: Live Delta Lake Bronze layer
