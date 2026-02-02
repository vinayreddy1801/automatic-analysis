import streamlit as st
import pandas as pd
import os
import time
from dotenv import load_dotenv

# Robust Import for Cloud
try:
    import psycopg2
except ImportError:
    psycopg2 = None

# Load env vars
load_dotenv()

# Page Config
st.set_page_config(
    page_title="Industrial Manufacturing Intelligence",
    page_icon="🏭",
    layout="wide",
)

st.title("🏭 Manufacturing Intelligence: Command Center")

# Database Connection
@st.cache_resource
def get_database_connection():
    if psycopg2 is None:
        return None
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        return None
    try:
        # TIMEOUT: Fail fast (3s) if DB is unreachable (e.g. firewall issues)
        return psycopg2.connect(db_url, connect_timeout=3)
    except Exception as e:
        return None

conn = get_database_connection()

# Sidebar
st.sidebar.header("⚙️ Pipeline Configuration")
refresh_rate = st.sidebar.slider("Telemetry Refresh Rate (s)", 1, 60, 5)
st.sidebar.markdown("---")
st.sidebar.markdown("**Status:** " + ("🟢 Connected to Production DB" if conn else "🟡 MOCK MODE (Simulation)"))

# Data Fetching
def fetch_data():
    if conn:
        try:
            curr = conn.cursor()
            # Get latest 100 records
            query = """
            SELECT unit_id, cycle_time, sensor_11_temp, sensor_12_pressure, timestamp 
            FROM optimus_test_telemetry 
            ORDER BY timestamp DESC LIMIT 100
            """
            curr.execute(query)
            cols = ["Unit ID", "Cycle Time", "Motor Temp (C)", "Hydraulic Pressure", "Timestamp"]
            df = pd.DataFrame(curr.fetchall(), columns=cols)
            return df
        except Exception as e:
            st.error(f"Database Error: {e}")
            return pd.DataFrame()
    else:
        # Mock Data Generation
        import numpy as np
        data = {
            "Unit ID": np.random.randint(1, 20, 100),
            "Cycle Time": np.random.randint(100, 500, 100),
            "Motor Temp (C)": np.random.normal(480, 15, 100),
            "Hydraulic Pressure": np.random.normal(520, 10, 100),
            "Timestamp": pd.date_range(end=pd.Timestamp.now(), periods=100, freq='1s')
        }
        return pd.DataFrame(data)

# Main Dashboard
placeholder = st.empty()

while True:
    df = fetch_data()
    
    with placeholder.container():
        # Top Metrics
        kpi1, kpi2, kpi3 = st.columns(3)
        
        avg_temp = df["Motor Temp (C)"].mean()
        high_temp_count = df[df["Motor Temp (C)"] > 500].shape[0]
        active_units = df["Unit ID"].nunique()
        
        kpi1.metric(label="Active Dyno Units", value=active_units)
        kpi2.metric(label="Avg Motor Temp", value=f"{avg_temp:.2f} °C", delta=f"{500-avg_temp:.1f} Margin")
        kpi3.metric(label="Critical Anomalies", value=high_temp_count, delta_color="inverse")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔥 Motor Temperature Live Feed")
            st.line_chart(df.set_index("Timestamp")["Motor Temp (C)"])
            
        with col2:
            st.subheader("⚠️ Anomaly Scatter Plot")
            try:
                # Convert Unit ID to string for discrete color mapping
                df["Unit ID"] = df["Unit ID"].astype(str)
                st.scatter_chart(df, x="Cycle Time", y="Motor Temp (C)", color="Unit ID")
            except Exception as e:
                st.warning(f"Chart unavailable: {e}")
            
        # Raw Data
        st.subheader("📋 Raw Telemetry Stream")
        st.dataframe(df, use_container_width=True)

        st.markdown("---")
        
        # System Health Section (The "Pulse")
        st.subheader("🏥 Infrastructure Health (Sentinel)")
        health_col1, health_col2 = st.columns([1, 2])
        
        with health_col1:
            st.success("✅ **Pipeline Status: ACTIVE** (Latency: Low)")
            st.info(f"📡 Ingestion Rate: ~1.0 Hz | 🛡️ Sentinel: MONITORING")
        
        with health_col2:
            st.caption("Recent Critical Alerts (Last 1hr)")
            # Simulate an alerts table for the dashboard view
            alert_data = {
                "Timestamp": [pd.Timestamp.now().strftime("%H:%M:%S")],
                "Event Type": ["Thermal Check"],
                "Status": ["Pass" if high_temp_count < 5 else "CRITICAL FAIL"],
                "Action": ["None" if high_temp_count < 5 else "STOP LINE"]
            }
            st.dataframe(pd.DataFrame(alert_data), use_container_width=True, hide_index=True)
        
    time.sleep(refresh_rate)
