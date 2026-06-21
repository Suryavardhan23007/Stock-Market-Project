import logging
from datetime import datetime
from sqlalchemy.orm import Session
from src.database.models import OptionsWritingLive
import pandas as pd

logger = logging.getLogger(__name__)

class WritingEngine:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.history = {}

    def process(self, df_merged: pd.DataFrame, timestamp: datetime, symbol: str) -> OptionsWritingLive:
        """
        Calculates writing detection by tracking OI and Premium changes between current and previous snapshots.
        """
        # Ensure we sort by strike
        df = df_merged.sort_values("strike_price").copy()
        
        # We need historical comparison, so get previous state
        state = self.history.get(symbol)
        
        long_buildup = 0.0
        short_buildup = 0.0
        short_covering = 0.0
        long_unwinding = 0.0
        
        if state is not None:
            # Merge current and prev to calculate deltas
            merged = pd.merge(df, state, on="strike_price", suffixes=("", "_prev"))
            
            # CE calculations
            ce_oi_change = merged["call_oi"] - merged["call_oi_prev"]
            ce_price_change = merged["ce_premium"] - merged["ce_premium_prev"]
            
            # PE calculations
            pe_oi_change = merged["put_oi"] - merged["put_oi_prev"]
            pe_price_change = merged["pe_premium"] - merged["pe_premium_prev"]
            
            for _, row in merged.iterrows():
                # Call rules
                dOI_c = row["call_oi"] - row["call_oi_prev"]
                dP_c = row["ce_premium"] - row["ce_premium_prev"]
                
                # Assign to categories
                if dP_c > 0 and dOI_c > 0: long_buildup += abs(dOI_c)
                elif dP_c < 0 and dOI_c > 0: short_buildup += abs(dOI_c)
                elif dP_c > 0 and dOI_c < 0: short_covering += abs(dOI_c)
                elif dP_c < 0 and dOI_c < 0: long_unwinding += abs(dOI_c)
                
                # Put rules
                dOI_p = row["put_oi"] - row["put_oi_prev"]
                dP_p = row["pe_premium"] - row["pe_premium_prev"]
                
                if dP_p > 0 and dOI_p > 0: long_buildup += abs(dOI_p)
                elif dP_p < 0 and dOI_p > 0: short_buildup += abs(dOI_p)
                elif dP_p > 0 and dOI_p < 0: short_covering += abs(dOI_p)
                elif dP_p < 0 and dOI_p < 0: long_unwinding += abs(dOI_p)
        
        # Save current state for next iteration
        self.history[symbol] = df[["strike_price", "call_oi", "put_oi", "ce_premium", "pe_premium"]]
        
        # We can normalize the scores as a percentage of total OI change
        total_change = long_buildup + short_buildup + short_covering + long_unwinding
        if total_change == 0: total_change = 1 # Avoid div/0
        
        record = OptionsWritingLive(
            timestamp=timestamp,
            symbol=symbol,
            long_buildup_score=float(long_buildup / total_change * 100),
            short_buildup_score=float(short_buildup / total_change * 100),
            short_covering_score=float(short_covering / total_change * 100),
            long_unwinding_score=float(long_unwinding / total_change * 100)
        )
        
        self.db_session.add(record)
        self.db_session.commit()
        return record
