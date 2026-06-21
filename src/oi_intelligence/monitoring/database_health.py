import os
import sys
import json
from sqlalchemy import text
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from src.database.connection import SessionLocal

def monitor_database():
    session = SessionLocal()
    
    db_size = session.execute(text("SELECT pg_database_size(current_database());")).scalar() or 0
    db_size_mb = db_size / (1024 * 1024)
    
    raw_chain_size = session.execute(text("""
        SELECT sum(pg_total_relation_size(inhrelid))
        FROM pg_inherits
        WHERE inhparent = 'options_raw_chain'::regclass;
    """)).scalar()
    if not raw_chain_size:
        raw_chain_size = session.execute(text("SELECT pg_total_relation_size('options_raw_chain');")).scalar() or 0
    raw_chain_size_mb = raw_chain_size / (1024 * 1024)
    
    partition_count = session.execute(text("""
        SELECT count(*) FROM pg_inherits WHERE inhparent = 'options_raw_chain'::regclass;
    """)).scalar() or 0
    
    total_rows = session.execute(text("SELECT count(*) FROM options_raw_chain;")).scalar() or 0
    
    rows_today = session.execute(text("SELECT count(*) FROM options_raw_chain WHERE timestamp >= CURRENT_DATE;")).scalar() or 0
    rows_week = session.execute(text("SELECT count(*) FROM options_raw_chain WHERE timestamp >= date_trunc('week', CURRENT_DATE);")).scalar() or 0
    rows_month = session.execute(text("SELECT count(*) FROM options_raw_chain WHERE timestamp >= date_trunc('month', CURRENT_DATE);")).scalar() or 0
    
    # Growth rate per day (average over last 7 days)
    last_7_days_rows = session.execute(text("SELECT count(*) FROM options_raw_chain WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days';")).scalar() or 0
    growth_rate_per_day = last_7_days_rows / 7.0
    
    # Largest table
    largest_table = session.execute(text("""
        SELECT relname FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public' AND relkind = 'r'
        ORDER BY pg_total_relation_size(c.oid) DESC LIMIT 1;
    """)).scalar() or "Unknown"
    
    # Total Index size
    index_size = session.execute(text("""
        SELECT sum(pg_relation_size(indexrelid)) FROM pg_index;
    """)).scalar() or 0
    index_size_mb = index_size / (1024 * 1024)
    
    report = {
        "Total Database Size (MB)": float(round(db_size_mb, 2)),
        "options_raw_chain Size (MB)": float(round(raw_chain_size_mb, 2)),
        "Partition Count": int(partition_count),
        "Total Row Count": int(total_rows),
        "Rows Inserted Today": int(rows_today),
        "Rows Inserted This Week": int(rows_week),
        "Rows Inserted This Month": int(rows_month),
        "Growth Rate (Rows/Day)": float(round(growth_rate_per_day, 2)),
        "Largest Table": str(largest_table),
        "Total Index Size (MB)": float(round(index_size_mb, 2))
    }
    
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'logs'))
    os.makedirs(log_dir, exist_ok=True)
    
    with open(os.path.join(log_dir, 'database_health.json'), 'w') as f:
        json.dump(report, f, indent=4)
        
    with open(os.path.join(log_dir, 'database_health.txt'), 'w') as f:
        for k, v in report.items():
            f.write(f"{k}: {v}\n")
            
    print("Database Health Report Generated.")

if __name__ == '__main__':
    monitor_database()
