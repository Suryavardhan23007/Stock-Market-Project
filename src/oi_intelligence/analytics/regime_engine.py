import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from src.database.models import MarketRegimeLive

logger = logging.getLogger(__name__)

class RegimeEngine:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.state = {
            "NIFTY": {"current_regime": "UNKNOWN", "transition_timestamp": None, "duration": 0},
            "BANKNIFTY": {"current_regime": "UNKNOWN", "transition_timestamp": None, "duration": 0}
        }
        
    def _determine_raw_regime(self, pcr_pct, iv_pct, vel_pct, breadth_pct, call_wall_pct, put_wall_pct):
        if pcr_pct is None or vel_pct is None:
            return "UNKNOWN"
            
        # Volatility Dominance (Optional Enhancement)
        if iv_pct is not None:
            if iv_pct > 80:
                return "VOLATILITY_EXPANSION"
            if iv_pct < 20:
                return "VOLATILITY_COMPRESSION"
                
        # Trend Dominance (Velocity + PCR + Breadth if available)
        bullish_score = 0
        bearish_score = 0
        
        if vel_pct > 70: bullish_score += 1
        if vel_pct < 30: bearish_score += 1
        if pcr_pct > 70: bullish_score += 1
        if pcr_pct < 30: bearish_score += 1
        if breadth_pct is not None:
            if breadth_pct > 60: bullish_score += 1
            if breadth_pct < 40: bearish_score += 1
            
        if bullish_score >= 2:
            return "TRENDING_BULL"
        if bearish_score >= 2:
            return "TRENDING_BEAR"
            
        # Structure Dominance
        if call_wall_pct is not None and put_wall_pct is not None:
            if call_wall_pct > 20 and put_wall_pct > 20:
                return "RANGE_BOUND"
                
        return "NEUTRAL"

    def process(self, timestamp: datetime, symbol: str, context_record, concentration_record, breadth_record=None) -> MarketRegimeLive:
        pcr_pct = context_record.pcr_percentile if context_record else None
        iv_pct = context_record.iv_percentile if context_record else None
        vel_pct = context_record.oi_velocity_percentile if context_record else None
        breadth_pct = breadth_record.weighted_breadth if breadth_record else None # For simplicity we'll just map weighted breadth roughly
        
        # Scale weighted_breadth (-1 to 1) into a 0-100 percentile equivalent for scoring
        breadth_scaled = None
        if breadth_pct is not None:
            breadth_scaled = ((breadth_pct + 1.0) / 2.0) * 100.0
        
        call_wall_pct = concentration_record.call_wall_pct if concentration_record else None
        put_wall_pct = concentration_record.put_wall_pct if concentration_record else None
        
        raw_regime = self._determine_raw_regime(pcr_pct, iv_pct, vel_pct, breadth_scaled, call_wall_pct, put_wall_pct)
        
        state = self.state.setdefault(symbol, {"current_regime": "UNKNOWN", "transition_timestamp": None, "duration": 0})
        
        previous_regime = state["current_regime"]
        
        if raw_regime == state["current_regime"]:
            state["duration"] += 1
        else:
            state["transition_timestamp"] = timestamp
            state["current_regime"] = raw_regime
            state["duration"] = 1
            
        # Stability score calculation (0 to 100) based on duration (peaks at 120 minutes)
        stability_score = min(100.0, (state["duration"] / 120.0) * 100.0)
        
        # Update context record with stability score directly
        if context_record:
            context_record.regime_stability_percentile = stability_score
            
        record = MarketRegimeLive(
            timestamp=timestamp,
            symbol=symbol,
            collection_version="v1.0",
            calculation_version="v1.0",
            ingestion_timestamp=datetime.now(timezone.utc),
            source_name="5paisa_xstream",
            previous_regime=previous_regime,
            current_regime=state["current_regime"],
            transition_timestamp=state["transition_timestamp"],
            duration_minutes=state["duration"],
            stability_score=stability_score
        )
        
        self.db_session.add(record)
        self.db_session.commit()
        return record
