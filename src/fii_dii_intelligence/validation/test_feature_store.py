import pytest
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base, InstitutionalFlowIntelligence
from src.fii_dii_intelligence.feature_store import InstitutionalFeatureStore

# Setup In-Memory SQLite for isolated testing
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
InstitutionalFlowIntelligence.__table__.create(bind=engine)

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_mathematical_lookahead_prevention(db_session):
    """
    PROVES:
    1. Monday prediction receives Friday data.
    2. Tuesday prediction receives Monday data.
    3. Same-day leakage is impossible.
    """
    
    # 1. Inject Fake Historical Flow Data (Friday, Monday, Tuesday)
    friday_date = datetime(2026, 6, 12)
    monday_date = datetime(2026, 6, 15)
    tuesday_date = datetime(2026, 6, 16)
    
    friday_flow = InstitutionalFlowIntelligence(
        trade_date=friday_date, fii_net=1000, dii_net=-500, source="MOCK"
    )
    monday_flow = InstitutionalFlowIntelligence(
        trade_date=monday_date, fii_net=-2000, dii_net=1000, source="MOCK"
    )
    tuesday_flow = InstitutionalFlowIntelligence(
        trade_date=tuesday_date, fii_net=5000, dii_net=-2000, source="MOCK"
    )
    
    db_session.add_all([friday_flow, monday_flow, tuesday_flow])
    db_session.commit()

    # 2. Extract Shifted Features via Feature Store
    store = InstitutionalFeatureStore(db_session)
    df_shifted = store.get_shifted_features_for_inference()

    # 3. VERIFICATION: Monday Prediction receives Friday Data
    # Index is Monday (2026-06-15). The values should belong to Friday (1000 / -500).
    monday_prediction_row = df_shifted.loc[monday_date]
    assert monday_prediction_row['fii_net'] == 1000, "Look-ahead Bias! Monday sees Monday's data instead of Friday's."
    
    # 4. VERIFICATION: Tuesday Prediction receives Monday Data
    # Index is Tuesday (2026-06-16). The values should belong to Monday (-2000 / 1000).
    tuesday_prediction_row = df_shifted.loc[tuesday_date]
    assert tuesday_prediction_row['fii_net'] == -2000, "Look-ahead Bias! Tuesday sees Tuesday's data instead of Monday's."
    
    # 5. VERIFICATION: Same-Day Leakage is Impossible
    # If same-day leakage occurred, tuesday's row would have fii_net = 5000. We assert it is mathematically impossible.
    assert tuesday_prediction_row['fii_net'] != 5000, "Same-day leakage detected!"
    
    print("\n[SUCCESS] Look-Ahead Bias Mathematically Prevented.")
    print(f"Prediction for {tuesday_date.strftime('%A')} uses FII Net Flow: {tuesday_prediction_row['fii_net']}")
