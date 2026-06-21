import logging
from datetime import datetime, timezone
import pandas as pd
from sqlalchemy.orm import Session
from src.database.models import OptionsStatisticsLive
from src.oi_intelligence.analytics.oi_calculator import OICalculator

logger = logging.getLogger(__name__)

class StatisticsEngine:
    def __init__(self, db_session: Session, symbol_config: dict):
        self.db_session = db_session
        self.config = symbol_config
        self.history_count = 0
        
    def _determine_expiry_type(self, expiry_date: datetime, timestamp: datetime) -> str:
        if not expiry_date:
            return "UNKNOWN"
        # Rough heuristic: if expiry is on last thursday of the month, it's monthly
        # For simplicity in V1, return WEEKLY unless days_to_expiry > 7 and it's near month end
        return "WEEKLY"
        
    def process(self, df: pd.DataFrame, timestamp: datetime, symbol: str, spot_price: float, expiry_date: datetime) -> OptionsStatisticsLive:
        if df.empty:
            return None
            
        atm_width = self.config.get('atm_zone_width', 100)
        atm_zone_low = spot_price - atm_width
        atm_zone_high = spot_price + atm_width
        
        days_to_expiry = None
        expiry_type = "UNKNOWN"
        if expiry_date:
            # Ensure expiry_date is timezone-aware
            if expiry_date.tzinfo is None:
                expiry_date = expiry_date.replace(tzinfo=timezone.utc)
            days_to_expiry = max(0, (expiry_date - timestamp).days)
            expiry_type = self._determine_expiry_type(expiry_date, timestamp)
            
        total_call_oi = df['call_oi'].sum()
        total_put_oi = df['put_oi'].sum()
        
        pcr = None
        if total_call_oi > 0:
            pcr = float(total_put_oi / total_call_oi)
            
        iv = None
        atm_strike = round(spot_price / (50 if symbol == 'NIFTY' else 100)) * (50 if symbol == 'NIFTY' else 100)
        atm_row = df[df['strike_price'] == atm_strike]
        if not atm_row.empty:
            premium = atm_row.iloc[0].get('ce_premium', atm_row.iloc[0].get('premium', 0))
            dte_years = max(days_to_expiry if days_to_expiry else 0, 0.01) / 365.0
            # Calculate Call IV
            iv = OICalculator.calculate_black_scholes_iv(premium, spot_price, atm_strike, dte_years, is_call=True)
            if iv is not None:
                iv = float(iv)
                
        self.history_count += 1
        warmup_status = "COLD_START"
        if self.history_count > 100:
            warmup_status = "READY"
        elif self.history_count > 10:
            warmup_status = "PARTIAL_HISTORY"
            
        record = OptionsStatisticsLive(
            timestamp=timestamp,
            symbol=symbol,
            collection_version="v1.0",
            calculation_version="v1.0",
            ingestion_timestamp=datetime.now(timezone.utc),
            source_name="5paisa_xstream",
            underlying_spot_price=spot_price,
            atm_zone_low=atm_zone_low,
            atm_zone_high=atm_zone_high,
            days_to_expiry=days_to_expiry,
            expiry_type=expiry_type,
            total_call_oi=int(total_call_oi),
            total_put_oi=int(total_put_oi),
            pcr=pcr,
            iv=iv,
            vix=None, # VIX is sourced externally in V1
            warmup_status=warmup_status
        )
        
        self.db_session.add(record)
        self.db_session.commit()
        return record
