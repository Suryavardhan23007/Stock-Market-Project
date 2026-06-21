import os
import shutil
import pandas as pd
from sqlalchemy import inspect
from src.database.connection import engine

def export_data():
    print("Starting Phase 1 & 2: Full Data Export & Sampling...")
    
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    audit_records = []
    
    # 1. Export DB Tables
    for table in tables:
        print(f"Exporting table: {table}...")
        
        try:
            # We use an iterator for market_candles if it's too big, but pd.read_sql handles it if RAM permits.
            # 2M rows is ~150MB, fits easily in 8GB RAM.
            df = pd.read_sql_table(table, engine.connect())
            
            full_path = os.path.join(output_dir, f"{table}.csv")
            sample_path = os.path.join(output_dir, f"sample_{table}.csv")
            
            df.to_csv(full_path, index=False)
            df.head(100).to_csv(sample_path, index=False)
            
            # Audit calculations
            row_count = len(df)
            num_cols = len(df.columns)
            null_count = int(df.isna().sum().sum())
            
            # Duplicates without ID
            dupe_count = 0
            if "id" in df.columns:
                dupe_count = int(df.duplicated(subset=[c for c in df.columns if c != "id"]).sum())
            else:
                dupe_count = int(df.duplicated().sum())
                
            earliest = "N/A"
            latest = "N/A"
            for col in ['timestamp', 'date', 'time']:
                if col in df.columns and row_count > 0:
                    earliest = str(df[col].min())
                    latest = str(df[col].max())
                    break
                    
            audit_records.append({
                "Dataset Name": f"{table}.csv",
                "Row Count": row_count,
                "Earliest Timestamp": earliest,
                "Latest Timestamp": latest,
                "Number of Columns": num_cols,
                "Null Counts": null_count,
                "Duplicate Counts": dupe_count,
                "Storage Path": full_path
            })
            
        except Exception as e:
            print(f"Failed exporting {table}: {e}")
            
    # 2. Copy the existing 1m candles and create samples
    existing_1m_files = ["nifty_1m_candles.csv", "banknifty_1m_candles.csv", "sensex_1m_candles.csv"]
    for file in existing_1m_files:
        src_path = os.path.join(output_dir, "exports", file)
        if os.path.exists(src_path):
            print(f"Processing existing 1m file: {file}...")
            dest_path = os.path.join(output_dir, file)
            sample_path = os.path.join(output_dir, f"sample_{file}")
            
            shutil.copy2(src_path, dest_path)
            
            df = pd.read_csv(src_path, low_memory=False)
            df.head(100).to_csv(sample_path, index=False)
            
            time_col = 'datetime' if 'datetime' in df.columns else 'timestamp'
            if time_col not in df.columns: time_col = 'time'
            
            earliest = str(df[time_col].min()) if time_col in df.columns else "N/A"
            latest = str(df[time_col].max()) if time_col in df.columns else "N/A"
            
            audit_records.append({
                "Dataset Name": file,
                "Row Count": len(df),
                "Earliest Timestamp": earliest,
                "Latest Timestamp": latest,
                "Number of Columns": len(df.columns),
                "Null Counts": int(df.isna().sum().sum()),
                "Duplicate Counts": int(df.duplicated(subset=[time_col]).sum()) if time_col in df.columns else 0,
                "Storage Path": dest_path
            })
            
    # 3. Write data_audit_report.csv
    print("Writing data_audit_report.csv...")
    audit_df = pd.DataFrame(audit_records)
    audit_df.to_csv(os.path.join(output_dir, "data_audit_report.csv"), index=False)
    print("Export pipeline complete.")

if __name__ == "__main__":
    export_data()
