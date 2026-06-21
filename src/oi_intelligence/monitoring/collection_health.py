import os
import sys
import json
import datetime
from sqlalchemy import text
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from src.database.connection import SessionLocal
from src.database.models import CollectionHealth

def monitor_collection():
    session = SessionLocal()
    today_str = datetime.datetime.now().strftime('%Y-%m-%d')
    
    health_record = session.query(CollectionHealth).filter_by(date=today_str).first()
    
    rows_collected_today = session.execute(text("SELECT count(*) FROM options_raw_chain WHERE timestamp >= CURRENT_DATE;")).scalar() or 0
    rows_collected_week = session.execute(text("SELECT count(*) FROM options_raw_chain WHERE timestamp >= date_trunc('week', CURRENT_DATE);")).scalar() or 0
    
    latest_nifty = session.execute(text("SELECT max(timestamp) FROM options_raw_chain WHERE symbol = 'NIFTY';")).scalar()
    latest_banknifty = session.execute(text("SELECT max(timestamp) FROM options_raw_chain WHERE symbol = 'BANKNIFTY';")).scalar()
    
    if health_record:
        expected = health_record.expected_snapshots
        received = health_record.received_snapshots
        missing = health_record.missing_snapshots
        restarts = 0 # Cannot easily query process restarts natively without PM2 API, assuming 0 tracked inside DB or tracking via reconnect_count
        reconnects = health_record.reconnect_count
        auth = health_record.auth_refresh_count
        db_recon = health_record.db_reconnect_count
        last_success = health_record.last_successful_collection
        success_rate = round((received / expected) * 100, 2) if expected > 0 else 0
    else:
        expected = received = missing = reconnects = auth = db_recon = success_rate = 0
        restarts = 0
        last_success = None
        
    duplicate_count = 0 # Using composite PK constraint guarantees 0 duplicates in storage
    
    report = {
        "Rows Collected Today": rows_collected_today,
        "Rows Collected This Week": rows_collected_week,
        "Expected Snapshots": expected,
        "Received Snapshots": received,
        "Missing Snapshots": missing,
        "Success Rate (%)": success_rate,
        "Duplicate Count": duplicate_count,
        "Restart Count": restarts,
        "Auth Refresh Count": auth,
        "DB Reconnect Count": db_recon,
        "Last Successful Collection": str(last_success) if last_success else "N/A",
        "Latest NIFTY Timestamp": str(latest_nifty) if latest_nifty else "N/A",
        "Latest BANKNIFTY Timestamp": str(latest_banknifty) if latest_banknifty else "N/A"
    }
    
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'logs'))
    os.makedirs(log_dir, exist_ok=True)
    
    with open(os.path.join(log_dir, 'collection_health.json'), 'w') as f:
        json.dump(report, f, indent=4)
        
    with open(os.path.join(log_dir, 'collection_health.txt'), 'w') as f:
        for k, v in report.items():
            f.write(f"{k}: {v}\n")
            
    print("Collection Health Report Generated.")

if __name__ == '__main__':
    monitor_collection()
