import pytest
from datetime import datetime, timezone
from src.database.connection import SessionLocal, Base, engine
from src.database.models import (
    SymbolConfig, OptionsRawChain, SystemHealthLive, SnapshotIntegrityLive,
    OptionsVelocityLive, MarketBreadthLive, OptionsConcentrationLive,
    MarketRegimeLive, OptionsStatisticsLive, OptionsContextLive, DataQualityLog
)

@pytest.fixture(scope="module")
def db_session():
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()

def test_database_insert_update_query(db_session):
    # Test DataQualityLog insertion
    test_time = datetime.now(timezone.utc)
    log = DataQualityLog(
        timestamp=test_time,
        event_type="TEST_EVENT",
        description="Dry-run audit test",
        severity="INFO"
    )
    db_session.add(log)
    db_session.commit()
    
    # Query
    fetched = db_session.query(DataQualityLog).filter_by(event_type="TEST_EVENT").first()
    assert fetched is not None
    assert fetched.description == "Dry-run audit test"
    
    # Clean up
    db_session.delete(fetched)
    db_session.commit()

def test_sqlalchemy_schemas_match(db_session):
    tables = [
        SymbolConfig, OptionsRawChain, SystemHealthLive, SnapshotIntegrityLive,
        OptionsVelocityLive, MarketBreadthLive, OptionsConcentrationLive,
        MarketRegimeLive, OptionsStatisticsLive, OptionsContextLive, DataQualityLog
    ]
    for table in tables:
        # Just selecting the first row to ensure the schema bindings match PostgreSQL
        try:
            res = db_session.query(table).first()
        except Exception as e:
            pytest.fail(f"Failed querying {table.__tablename__}: {e}")
