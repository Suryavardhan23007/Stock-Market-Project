import logging
from datetime import datetime
from sqlalchemy.orm import Session
from src.database.models import OptionsGammaLive
from src.oi_intelligence.analytics.oi_calculator import OICalculator
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class GammaEngine:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def process(self, df: pd.DataFrame, timestamp: datetime, symbol: str, spot_price: float, expiry_date) -> OptionsGammaLive:
        """
        Calculates Gamma Exposure (GEX) across the entire chain.
        """
        if not expiry_date:
            return None
            
        if expiry_date.tzinfo is None:
            from datetime import timezone
            expiry_date = expiry_date.replace(tzinfo=timezone.utc)
            
        days_to_expiry = max(0, (expiry_date - timestamp).days)
        dte_years = max(days_to_expiry, 0.01) / 365.0
        
        total_call_gex = 0.0
        total_put_gex = 0.0
        
        for _, row in df.iterrows():
            K = row['strike_price']
            
            # Rough local IV estimate using current strike premium
            # In a true system, we'd build a volatility surface. We'll use Black Scholes locally per strike.
            iv_ce = OICalculator.calculate_black_scholes_iv(row.get('ce_premium', 0), spot_price, K, dte_years, is_call=True)
            iv_pe = OICalculator.calculate_black_scholes_iv(row.get('pe_premium', 0), spot_price, K, dte_years, is_call=False)
            
            # Default to 20% if convergence fails
            sigma_ce = (iv_ce if iv_ce else 20.0) / 100.0
            sigma_pe = (iv_pe if iv_pe else 20.0) / 100.0
            
            # Calculate Gamma (Gamma is same for Call and Put in standard BS)
            from scipy.stats import norm
            r = 0.07 # Assume 7% risk free rate for India
            
            # CE Gamma
            d1_ce = (np.log(spot_price / K) + (r + 0.5 * sigma_ce ** 2) * dte_years) / (sigma_ce * np.sqrt(dte_years))
            gamma_ce = norm.pdf(d1_ce) / (spot_price * sigma_ce * np.sqrt(dte_years))
            
            # PE Gamma
            d1_pe = (np.log(spot_price / K) + (r + 0.5 * sigma_pe ** 2) * dte_years) / (sigma_pe * np.sqrt(dte_years))
            gamma_pe = norm.pdf(d1_pe) / (spot_price * sigma_pe * np.sqrt(dte_years))
            
            # GEX calculation: OI * 100 * Gamma * Spot Price * Spot Price * 0.01
            # Roughly approximating dealer exposure assuming market makers are short calls and short puts
            call_gex = row['call_oi'] * gamma_ce * spot_price * spot_price * 0.01
            put_gex = row['put_oi'] * gamma_pe * spot_price * spot_price * 0.01 * -1 # Puts have negative GEX for dealers
            
            total_call_gex += call_gex
            total_put_gex += put_gex
            
        net_gex = total_call_gex + total_put_gex
        gamma_regime = "POSITIVE_GAMMA" if net_gex > 0 else "NEGATIVE_GAMMA"
        
        record = OptionsGammaLive(
            timestamp=timestamp,
            symbol=symbol,
            total_call_gex=float(total_call_gex),
            total_put_gex=float(total_put_gex),
            net_gex=float(net_gex),
            gamma_regime=gamma_regime
        )
        
        self.db_session.add(record)
        self.db_session.commit()
        return record
