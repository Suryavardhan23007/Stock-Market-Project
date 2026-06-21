import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from src.database.models import OptionsContextLive
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

class ContextEngine:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.MAX_HISTORY = 30 * 375 # roughly 30 days
        
        self.history = {
            "NIFTY": {"pcr": [], "iv": [], "vix": [], "velocity": []},
            "BANKNIFTY": {"pcr": [], "iv": [], "vix": [], "velocity": []}
        }
        
    def _calculate_percentile(self, current_val, history_list):
        if len(history_list) < 100:
            return None
        less_than = sum(1 for x in history_list if x < current_val)
        return float((less_than / len(history_list)) * 100.0)

    def process(self, timestamp: datetime, symbol: str, pcr: float, iv: float, vix: float, velocity: float) -> OptionsContextLive:
        state = self.history.setdefault(symbol, {"pcr": [], "iv": [], "vix": [], "velocity": []})
        
        pcr_pct = None
        iv_pct = None
        vix_pct = None
        vel_pct = None
        
        if pcr is not None:
            state["pcr"].append(pcr)
            if len(state["pcr"]) > self.MAX_HISTORY: state["pcr"].pop(0)
            pcr_pct = self._calculate_percentile(pcr, state["pcr"])
            
        if iv is not None:
            state["iv"].append(iv)
            if len(state["iv"]) > self.MAX_HISTORY: state["iv"].pop(0)
            iv_pct = self._calculate_percentile(iv, state["iv"])
            
        if vix is not None:
            state["vix"].append(vix)
            if len(state["vix"]) > self.MAX_HISTORY: state["vix"].pop(0)
            vix_pct = self._calculate_percentile(vix, state["vix"])
            
        if velocity is not None:
            state["velocity"].append(velocity)
            if len(state["velocity"]) > self.MAX_HISTORY: state["velocity"].pop(0)
            vel_pct = self._calculate_percentile(velocity, state["velocity"])
            
        # Calculate session time contexts
        ist_time = timestamp.astimezone(timezone(pd.Timedelta(hours=5, minutes=30))) if hasattr(timestamp, "astimezone") else timestamp
        market_open = ist_time.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = ist_time.replace(hour=15, minute=30, second=0, microsecond=0)
        
        minutes_since_open = max(0, int((ist_time - market_open).total_seconds() / 60))
        minutes_until_close = max(0, int((market_close - ist_time).total_seconds() / 60))
        
        record = OptionsContextLive(
            timestamp=timestamp,
            symbol=symbol,
            collection_version="v1.0",
            calculation_version="v1.0",
            ingestion_timestamp=datetime.now(timezone.utc),
            source_name="5paisa_xstream",
            minutes_since_open=minutes_since_open,
            minutes_until_close=minutes_until_close,
            underlying_spot_price=None, # Filled by other processes if needed, but Context focuses on %
            pcr_percentile=pcr_pct,
            oi_velocity_percentile=vel_pct,
            iv_percentile=iv_pct,
            vix_percentile=vix_pct,
            breadth_percentile=None, # Sourced externally
            regime_stability_percentile=None # Calculated in Phase 5
        )
        
        self.db_session.add(record)
        self.db_session.commit()
        return record
