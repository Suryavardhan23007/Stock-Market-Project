import sys
from sqlalchemy import text
from src.database.connection import SessionLocal, init_db

def migrate_schemas():
    db = SessionLocal()
    print("[INFO] Starting database schema migrations...")
    
    # 1. Create any non-existent tables (like institutional_flows, amfi_flows, banking_relations, options_intelligence)
    try:
        init_db()
        print("[SUCCESS] Created any missing tables successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to run init_db: {e}")
        db.close()
        return

    # 2. Add columns to structured_events if not present
    structured_events_cols = [
        ("entities", "TEXT"),
        ("banknifty_return_1m", "DOUBLE PRECISION"),
        ("banknifty_return_5m", "DOUBLE PRECISION"),
        ("banknifty_return_15m", "DOUBLE PRECISION"),
        ("banknifty_return_30m", "DOUBLE PRECISION"),
        ("banknifty_return_1h", "DOUBLE PRECISION"),
        ("banknifty_return_1d", "DOUBLE PRECISION"),
        ("nifty_return_1m", "DOUBLE PRECISION"),
        ("nifty_return_5m", "DOUBLE PRECISION"),
        ("nifty_return_15m", "DOUBLE PRECISION"),
        ("nifty_return_30m", "DOUBLE PRECISION"),
        ("nifty_return_1h", "DOUBLE PRECISION"),
        ("nifty_return_1d", "DOUBLE PRECISION"),
        ("sensex_return_1m", "DOUBLE PRECISION"),
        ("sensex_return_5m", "DOUBLE PRECISION"),
        ("sensex_return_15m", "DOUBLE PRECISION"),
        ("sensex_return_30m", "DOUBLE PRECISION"),
        ("sensex_return_1h", "DOUBLE PRECISION"),
        ("sensex_return_1d", "DOUBLE PRECISION")
    ]

    print("[INFO] Migrating structured_events table columns...")
    for col_name, col_type in structured_events_cols:
        try:
            # PostgreSQL supports ALTER TABLE ... ADD COLUMN IF NOT EXISTS
            query = f"ALTER TABLE structured_events ADD COLUMN IF NOT EXISTS {col_name} {col_type}"
            db.execute(text(query))
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"[ERROR] Failed to add column {col_name} to structured_events: {e}")

    # 3. Add columns to economic_calendar if not present
    economic_calendar_cols = [
        ("event_type", "VARCHAR"),
        ("forecast", "VARCHAR"),
        ("actual", "VARCHAR"),
        ("previous", "VARCHAR"),
        ("importance", "VARCHAR"),
        ("source", "VARCHAR"),
        ("created_at", "TIMESTAMP WITH TIME ZONE")
    ]

    print("[INFO] Migrating economic_calendar table columns...")
    for col_name, col_type in economic_calendar_cols:
        try:
            query = f"ALTER TABLE economic_calendar ADD COLUMN IF NOT EXISTS {col_name} {col_type}"
            db.execute(text(query))
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"[ERROR] Failed to add column {col_name} to economic_calendar: {e}")

    print("[SUCCESS] Database schema migrations completed successfully.")
    db.close()

if __name__ == "__main__":
    migrate_schemas()
