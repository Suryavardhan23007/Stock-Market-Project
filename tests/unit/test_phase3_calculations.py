import pytest
from datetime import datetime, timezone, timedelta
from src.ingestion.options_streamer import OptionsStreamer
from src.database.models import OptionsConcentrationLive, OptionsVelocityLive

def test_phase3_calculations():
    streamer = OptionsStreamer(client=None)
    test_time_1 = datetime(2026, 6, 16, 4, 35, tzinfo=timezone.utc)
    test_time_2 = test_time_1 + timedelta(minutes=1)

    mock_payload_1 = []
    mock_payload_2 = []
    for i in range(-15, 15):
        strike = 25000 + (i * 100)
        is_atm = (strike == 25000)
        oi1 = 100000 if is_atm else 5000
        vol1 = 10000 if is_atm else 1000
        mock_payload_1.append({"StrikeRate": strike, "CPType": "CE", "OpenInterest": oi1, "Volume": vol1, "LastRate": 150.0})
        mock_payload_1.append({"StrikeRate": strike, "CPType": "PE", "OpenInterest": oi1, "Volume": vol1, "LastRate": 150.0})
        oi2 = 120000 if is_atm else 5000
        mock_payload_2.append({"StrikeRate": strike, "CPType": "CE", "OpenInterest": oi2, "Volume": vol1, "LastRate": 150.0})
        mock_payload_2.append({"StrikeRate": strike, "CPType": "PE", "OpenInterest": oi2, "Volume": vol1, "LastRate": 150.0})

    streamer.process_snapshot("NIFTY", 25000, mock_payload_1, test_time_1, test_time_1)
    concentration = streamer.db_session.query(OptionsConcentrationLive).filter_by(timestamp=test_time_1).first()
    assert concentration is not None
