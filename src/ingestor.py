import pandas as pd
import psycopg2
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

def stream_factory_data():
    # Load NASA Data (Simulating the PLC Source)
    # The file path is relative to where the script is run or absolute
    data_path = os.path.join(os.path.dirname(__file__), '../data/train_FD001.txt')
    
    if not os.path.exists(data_path):
        print(f"❌ Error: Data file not found at {data_path}")
        return

    # NASA C-MAPSS data is space-separated without headers
    # We only need a few columns for the simulation
    try:
        df = pd.read_csv(data_path, sep="\s+", header=None)
    except Exception as e:
        print(f"❌ Error reading data file: {e}")
        return
    
    # Connect to Database
    conn = None
    cur = None
    dry_run = False
    
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        print("✅ Connected to Supabase Database")
    except Exception as e:
        print(f"⚠️  Database connection failed (Check .env). Switching to SIMULATION MODE (Console Only).")
        dry_run = True

    print("🚀 Factory Line Started: Streaming Telemetry...")
    
    try:
        for index, row in df.iterrows():
            # NASA formatted data mapping
            unit_id = int(row[0])
            cycle_time = int(row[1])
            sensor_11_temp = float(row[15])     # Column 15 is Sensor 11
            sensor_12_pressure = float(row[16]) # Column 16 is Sensor 12
            
            if not dry_run:
                try:
                    sql = """INSERT INTO optimus_test_telemetry (unit_id, cycle_time, sensor_11_temp, sensor_12_pressure) 
                             VALUES (%s, %s, %s, %s)"""
                    cur.execute(sql, (unit_id, cycle_time, sensor_11_temp, sensor_12_pressure))
                    conn.commit()
                except Exception as e:
                    print(f"❌ DB Write Error: {e}")
            
            # Print to console regardless of DB connection (The "Show")
            print(f"✅ Unit {unit_id} | Cycle {cycle_time} | Temp: {sensor_11_temp:.2f} | Pressure: {sensor_12_pressure:.2f} | Data Ingested")
            
            # Simulate Real-Time delay
            time.sleep(1) 
            
    except KeyboardInterrupt:
        print("\n🛑 Factory Line Stopped by User")
    except Exception as e:
        print(f"❌ Error during streaming: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()
            print("🔌 Database Connection Closed")

if __name__ == "__main__":
    stream_factory_data()
