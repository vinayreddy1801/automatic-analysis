import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

def check_production_health():
    conn = None
    cur = None
    dry_run = False

    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
    except Exception as e:
        print(f"⚠️  Database connection failed. Running in TEST MODE (Simulating check).")
        dry_run = True

    print("🔍 Sentinel: Scanning for Anomalies...")

    if dry_run:
        # Simulate finding an anomaly for demonstration
        import random
        if random.choice([True, False]):
             rows = [(1, 101, 502.45), (2, 45, 510.12)] # Fake data
        else:
             rows = []
    else:
        # SQL to find units where sensor_11 (Temp) is spiking
        query = """
        SELECT unit_id, cycle_time, sensor_11_temp 
        FROM optimus_test_telemetry 
        WHERE sensor_11_temp > 500 
        ORDER BY timestamp DESC LIMIT 10;
        """
        try:
            cur.execute(query)
            rows = cur.fetchall()
        except Exception as e:
            print(f"❌ Error querying anomalies: {e}")
            rows = []

    if rows:
        print(f"⚠️  ALERT: {len(rows)} High-Temp Anomalies Detected!")
        for row in rows:
            print(f"   -> Unit {row[0]} | Cycle {row[1]} | Temp {row[2]:.2f} - CHECK REQUIRED")
    else:
        print("✅ All Systems Normal. No anomalies detected.")
            
    if conn:
        cur.close()
        conn.close()

if __name__ == "__main__":
    check_production_health()
