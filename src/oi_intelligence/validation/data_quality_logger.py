from datetime import datetime, timezone

class DataQualityLogger:
    """
    Logs data quality events such as missing snapshots, disconnects, and stale data.
    These events should be flushed to the database table `data_quality_log`.
    """
    
    def __init__(self, db_session=None):
        self.db_session = db_session
        
    def log_event(self, event_type: str, description: str, severity: str = "INFO"):
        """
        event_type options: MISSING_SNAPSHOT, DISCONNECT, API_FAILURE, DUPLICATE_RECORD, STALE_DATA, RECONNECT
        """
        timestamp = datetime.now(timezone.utc)
        
        # In production, insert into `data_quality_log` using self.db_session
        # For now, just print to console/logger
        print(f"[{timestamp}] [DATA QUALITY] {severity} - {event_type}: {description}")
        
    def check_stale_data(self, fetch_timestamp: datetime, threshold_seconds=120):
        """
        Validates if the fetched snapshot is older than the threshold.
        Returns True if stale.
        """
        now = datetime.now(timezone.utc)
        if (now - fetch_timestamp).total_seconds() > threshold_seconds:
            self.log_event("STALE_DATA", f"Snapshot is {(now - fetch_timestamp).total_seconds()}s old", "WARNING")
            return True
        return False
