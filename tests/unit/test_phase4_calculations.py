import pytest
from datetime import datetime, timezone, timedelta
from src.ingestion.options_streamer import OptionsStreamer
from src.database.models import OptionsStatisticsLive, OptionsContextLive

def test_phase4_calculations():
    streamer = OptionsStreamer(client=None)
    test_time_1 = datetime(2026, 6, 16, 4, 35, tzinfo=timezone.utc)
    expiry_date = test_time_1 + timedelta(days=2)
    mock_payload = []
    for i in range(-15, 15):
        strike = 25000 + (i * 100)
        is_atm = (strike == 25000)
        oi1 = 100000 if is_atm else 5000
        vol1 = 10000 if is_atm else 1000
        mock_payload.append({"StrikeRate": strike, "CPType": "CE", "OpenInterest": oi1, "Volume": vol1, "LastRate": 150.0})
        mock_payload.append({"StrikeRate": strike, "CPType": "PE", "OpenInterest": oi1, "Volume": vol1, "LastRate": 150.0})

    streamer.process_snapshot("NIFTY", 25000, mock_payload, test_time_1, expiry_date)
    stats = streamer.db_session.query(OptionsStatisticsLive).filter_by(timestamp=test_time_1).first()
    assert stats is not None
