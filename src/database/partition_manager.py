import logging
from sqlalchemy import text
from src.database.connection import engine, Base
# Import all models to ensure metadata knows about them
from src.database.models import *
from datetime import datetime
from dateutil.relativedelta import relativedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PARTITIONED_TABLES = [
    "options_raw_chain",
    "options_velocity_live",
    "options_statistics_live",
    "options_context_live"
]

def drop_old_options_tables():
    """Drops the old Options Intelligence Layer V0 tables before migration."""
    old_tables = [
        "options_raw_chain", "oi_structure_live", "index_oi_structure_live", 
        "options_concentration_live", "max_pain_live", "options_statistics_live", 
        "market_regime_live", "confidence_components_live", "system_warmup_status", 
        "execution_recommendation_live", "data_quality_log",
        "symbol_config", "system_health_live", "snapshot_integrity_live",
        "options_velocity_live", "market_breadth_live", "options_context_live"
    ]
    with engine.begin() as conn:
        for table in old_tables:
            conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))
            logger.info(f"Dropped table {table} (if it existed).")

def create_schema():
    """Creates all tables using SQLAlchemy's metadata."""
    logger.info("Creating schema from SQLAlchemy models...")
    Base.metadata.create_all(bind=engine)
    logger.info("Schema creation completed.")

def create_monthly_partition(table_name: str, target_date: datetime):
    """
    Creates a partition for the specified table and month.
    PostgreSQL syntax: CREATE TABLE table_YYYY_MM PARTITION OF table FOR VALUES FROM ('YYYY-MM-01') TO ('YYYY-MM+1-01');
    """
    year = target_date.year
    month = target_date.month
    
    # Calculate start and end dates for the partition
    start_date = datetime(year, month, 1)
    end_date = start_date + relativedelta(months=1)
    
    partition_name = f"{table_name}_{year}_{month:02d}"
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    ddl = f"""
    CREATE TABLE IF NOT EXISTS {partition_name} 
    PARTITION OF {table_name} 
    FOR VALUES FROM ('{start_str}') TO ('{end_str}');
    """
    
    with engine.begin() as conn:
        conn.execute(text(ddl))
        logger.info(f"Ensured partition {partition_name} exists for range {start_str} to {end_str}.")

def manage_partitions(months_ahead=1):
    """
    Creates partitions for the current month and up to `months_ahead` months in the future.
    """
    now = datetime.now()
    
    for i in range(months_ahead + 1):
        target_date = now + relativedelta(months=i)
        for table in PARTITIONED_TABLES:
            create_monthly_partition(table, target_date)

if __name__ == "__main__":
    logger.info("=== Starting Partition Manager & DB Migration ===")
    drop_old_options_tables()
    create_schema()
    manage_partitions(months_ahead=1)
    
    # Pre-seed symbol config
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO symbol_config (symbol, atm_zone_width, liquidity_threshold, wall_significance_threshold, coverage_threshold)
            VALUES 
            ('NIFTY', 100, 1000, 15.0, 80.0),
            ('BANKNIFTY', 200, 1000, 15.0, 80.0)
            ON CONFLICT DO NOTHING;
        """))
    logger.info("=== Migration and Partition setup complete ===")
