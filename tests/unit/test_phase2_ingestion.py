import pytest
from datetime import datetime, timezone, timedelta
from src.ingestion.options_streamer import OptionsStreamer
from src.database.models import SnapshotIntegrityLive

def test_missing_option_chain_behavior():
    streamer = OptionsStreamer(client=None)
    test_time = datetime(2026, 6, 16, 4, 30, tzinfo=timezone.utc)
    mock_payload = [{"StrikeRate": 25000, "CPType": "CE", "OpenInterest": 50000, "Volume": 10000, "LastRate": 150.0}]
    streamer.process_snapshot("NIFTY", 25000, mock_payload, test_time, test_time)
    record = streamer.db_session.query(SnapshotIntegrityLive).order_by(SnapshotIntegrityLive.id.desc()).first()
    assert record.data_health_status == "LOW_CHAIN_COVERAGE"
