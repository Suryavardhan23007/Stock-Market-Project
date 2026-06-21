import logging
from datetime import datetime, timezone
import pandas as pd
from sqlalchemy.orm import Session
from src.database.models import SnapshotIntegrityLive, SystemHealthLive

logger = logging.getLogger(__name__)

class SnapshotIntegrityEngine:
    def __init__(self, db_session: Session, symbol_config: dict):
        self.db_session = db_session
        self.config = symbol_config
        
    def determine_session_state(self, timestamp: datetime) -> str:
        """
        Determines the Indian market session state.
        09:00 - 09:15 = PRE_MARKET
        09:15 - 15:30 = MARKET_OPEN
        15:30 - 09:00 = MARKET_CLOSED
        Weekend = MARKET_CLOSED (or HOLIDAY)
        """
        # Convert UTC to IST
        ist_tz = timezone(pd.Timedelta(hours=5, minutes=30))
        ist_time = timestamp.astimezone(ist_tz)
        
        if ist_time.weekday() >= 5:
            return "MARKET_CLOSED"
            
        time_str = ist_time.strftime("%H:%M:%S")
        if "09:00:00" <= time_str < "09:15:00":
            return "PRE_MARKET"
        elif "09:15:00" <= time_str <= "15:30:00":
            return "MARKET_OPEN"
        else:
            return "MARKET_CLOSED"
            
    def validate_snapshot(self, 
                          df: pd.DataFrame, 
                          timestamp: datetime, 
                          symbol: str, 
                          underlying_spot_price: float,
                          last_snapshot_time: datetime = None) -> SnapshotIntegrityLive:
        """
        Validates the raw options chain dataframe.
        """
        ingestion_timestamp = datetime.now(timezone.utc)
        
        session_state = self.determine_session_state(timestamp)
        
        # Freshness Check
        data_age_seconds = None
        if last_snapshot_time:
            data_age_seconds = int((timestamp - last_snapshot_time).total_seconds())
        
        # Aggregate logic
        total_call_oi = int(df['call_oi'].sum()) if not df.empty else 0
        total_put_oi = int(df['put_oi'].sum()) if not df.empty else 0
        total_call_volume = int(df['call_vol'].sum()) if not df.empty else 0
        total_put_volume = int(df['put_vol'].sum()) if not df.empty else 0
        
        strikes_received = len(df)
        atm_width = self.config.get('atm_zone_width', 100)
        atm_zone_low = underlying_spot_price - atm_width
        atm_zone_high = underlying_spot_price + atm_width
        
        # Approximating expected strikes (based on roughly ±15 steps of step size)
        step_size = 50 if symbol == 'NIFTY' else 100
        strikes_expected = 30 # standard +/- 15 strikes
        chain_coverage_pct = (strikes_received / strikes_expected) * 100 if strikes_expected > 0 else 0.0
        
        # Health classification
        data_health_status = "HEALTHY"
        if session_state != "MARKET_OPEN":
            data_health_status = "INSUFFICIENT_DATA"
        elif df.empty or (total_call_oi == 0 and total_put_oi == 0):
            data_health_status = "INSUFFICIENT_DATA"
        elif data_age_seconds is not None and data_age_seconds > 120:
            data_health_status = "STALE_FEED"
        elif chain_coverage_pct < 50.0:
            data_health_status = "LOW_CHAIN_COVERAGE"
            
        record = SnapshotIntegrityLive(
            timestamp=timestamp,
            symbol=symbol,
            collection_version="v1.0",
            calculation_version="v1.0",
            ingestion_timestamp=ingestion_timestamp,
            source_name="5paisa_xstream",
            strikes_expected=strikes_expected,
            strikes_received=strikes_received,
            chain_coverage_pct=chain_coverage_pct,
            total_call_oi=total_call_oi,
            total_put_oi=total_put_oi,
            total_call_volume=total_call_volume,
            total_put_volume=total_put_volume,
            session_state=session_state,
            data_health_status=data_health_status,
            data_age_seconds=data_age_seconds,
            underlying_spot_price=underlying_spot_price,
            atm_zone_low=atm_zone_low,
            atm_zone_high=atm_zone_high
        )
        
        self.db_session.add(record)
        self.db_session.commit()
        return record

    def update_system_health(self, api_status: str, websocket_status: str, last_snapshot_time: datetime):
        """Records system health independently of market data."""
        record = SystemHealthLive(
            timestamp=datetime.now(timezone.utc),
            api_status=api_status,
            db_status="HEALTHY", # if we can write this, DB is healthy
            partition_status="HEALTHY",
            websocket_status=websocket_status,
            last_snapshot_time=last_snapshot_time
        )
        self.db_session.add(record)
        self.db_session.commit()
