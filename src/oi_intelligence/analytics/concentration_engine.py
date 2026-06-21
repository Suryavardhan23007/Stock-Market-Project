import logging
from datetime import datetime, timezone
import pandas as pd
from sqlalchemy.orm import Session
from src.database.models import OptionsConcentrationLive

logger = logging.getLogger(__name__)

class ConcentrationEngine:
    def __init__(self, db_session: Session, symbol_config: dict):
        self.db_session = db_session
        self.config = symbol_config
        
        # State tracking for duration and shifts
        self.state = {
            "NIFTY": {"call_wall": None, "put_wall": None, "call_duration": 0, "put_duration": 0},
            "BANKNIFTY": {"call_wall": None, "put_wall": None, "call_duration": 0, "put_duration": 0}
        }
        
    def process(self, df: pd.DataFrame, timestamp: datetime, symbol: str, underlying_spot_price: float) -> OptionsConcentrationLive:
        """
        Calculates Wall positions, drift, and persistence.
        """
        if df.empty:
            return None
            
        # 1. Liquidity Filtering
        liquidity_thresh = self.config.get('liquidity_threshold', 1000)
        df['liquidity_score'] = df['call_vol'] + df['put_vol']
        df_liquid = df[df['liquidity_score'] >= liquidity_thresh].copy()
        
        if df_liquid.empty:
            return None
            
        total_call_oi = df_liquid['call_oi'].sum()
        total_put_oi = df_liquid['put_oi'].sum()
        
        call_wall_strike = None
        put_wall_strike = None
        call_wall_pct = 0.0
        put_wall_pct = 0.0
        
        # 2. Extract Top Concentration Walls
        if total_call_oi > 0:
            top_call = df_liquid.nlargest(1, 'call_oi').iloc[0]
            call_wall_strike = float(top_call['strike_price'])
            call_wall_pct = float((top_call['call_oi'] / total_call_oi) * 100.0)
            
        if total_put_oi > 0:
            top_put = df_liquid.nlargest(1, 'put_oi').iloc[0]
            put_wall_strike = float(top_put['strike_price'])
            put_wall_pct = float((top_put['put_oi'] / total_put_oi) * 100.0)
            
        # Wall Significance Gate
        sig_thresh = self.config.get('wall_significance_threshold', 10.0)
        if call_wall_pct < sig_thresh:
            call_wall_strike = None
            call_wall_pct = 0.0
        if put_wall_pct < sig_thresh:
            put_wall_strike = None
            put_wall_pct = 0.0
            
        # 3. Calculate Distance and Shifts
        distance_call = ((call_wall_strike - underlying_spot_price) / underlying_spot_price) * 100 if call_wall_strike and underlying_spot_price else None
        distance_put = ((underlying_spot_price - put_wall_strike) / underlying_spot_price) * 100 if put_wall_strike and underlying_spot_price else None
        
        state = self.state.setdefault(symbol, {"call_wall": None, "put_wall": None, "call_duration": 0, "put_duration": 0})
        
        call_shift = 0.0
        put_shift = 0.0
        
        # Call state logic
        if call_wall_strike:
            if state["call_wall"] == call_wall_strike:
                state["call_duration"] += 1
            else:
                if state["call_wall"]:
                    call_shift = call_wall_strike - state["call_wall"]
                state["call_wall"] = call_wall_strike
                state["call_duration"] = 1
        else:
            state["call_wall"] = None
            state["call_duration"] = 0
            
        # Put state logic
        if put_wall_strike:
            if state["put_wall"] == put_wall_strike:
                state["put_duration"] += 1
            else:
                if state["put_wall"]:
                    put_shift = put_wall_strike - state["put_wall"]
                state["put_wall"] = put_wall_strike
                state["put_duration"] = 1
        else:
            state["put_wall"] = None
            state["put_duration"] = 0
            
        record = OptionsConcentrationLive(
            timestamp=timestamp,
            symbol=symbol,
            collection_version="v1.0",
            calculation_version="v1.0",
            ingestion_timestamp=datetime.now(timezone.utc),
            source_name="5paisa_xstream",
            call_wall_strike=call_wall_strike,
            put_wall_strike=put_wall_strike,
            call_wall_pct=call_wall_pct,
            put_wall_pct=put_wall_pct,
            previous_call_wall=state["call_wall"] - call_shift if call_shift else None,
            previous_put_wall=state["put_wall"] - put_shift if put_shift else None,
            call_wall_shift=call_shift,
            put_wall_shift=put_shift,
            distance_to_call_wall=distance_call,
            distance_to_put_wall=distance_put,
            call_wall_duration_minutes=state["call_duration"],
            put_wall_duration_minutes=state["put_duration"]
        )
        
        self.db_session.add(record)
        self.db_session.commit()
        return record
