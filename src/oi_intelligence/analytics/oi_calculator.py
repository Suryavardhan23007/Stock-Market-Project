import numpy as np
from scipy.stats import norm
import pandas as pd

class OICalculator:
    """
    Implements the real-time calculation of Options Intelligence metrics.
    """
    
    @staticmethod
    def classify_strike_buildup(premium_change: float, oi_change: float) -> str:
        """
        Strike-Level Build-Up Classification
        """
        if premium_change > 0 and oi_change > 0:
            return "LONG_BUILDUP"
        elif premium_change < 0 and oi_change > 0:
            return "SHORT_BUILDUP"
        elif premium_change > 0 and oi_change < 0:
            return "SHORT_COVERING"
        elif premium_change < 0 and oi_change < 0:
            return "LONG_UNWINDING"
        else:
            return "NEUTRAL"

    @staticmethod
    def classify_index_buildup(spot_change: float, total_call_oi_change: float, total_put_oi_change: float) -> str:
        """
        Index-Level Build-Up Classification
        """
        if spot_change > 0 and total_call_oi_change < 0 and total_put_oi_change > 0:
            return "SHORT_COVERING_RALLY"
        elif spot_change < 0 and total_call_oi_change > 0 and total_put_oi_change < 0:
            return "LONG_UNWINDING_SELLING"
        elif spot_change > 0 and total_call_oi_change > 0 and total_put_oi_change > 0:
            # New money entering upward
            return "BULLISH_BUILDUP"
        elif spot_change < 0 and total_call_oi_change > 0 and total_put_oi_change > 0:
            # New money entering downward
            return "BEARISH_BUILDUP"
        else:
            return "MIXED"

    @staticmethod
    def calculate_max_pain(options_chain_df, spot_price):
        """
        Calculates the Max Pain strike where option buyers lose the most money (intrinsic value is minimized).
        `options_chain_df` expects columns: 'strike_price', 'call_oi', 'put_oi'
        """
        total_call_oi = options_chain_df.get('call_oi', pd.Series()).sum()
        total_put_oi = options_chain_df.get('put_oi', pd.Series()).sum()
        
        if total_call_oi <= 0 and total_put_oi <= 0:
            return "MAX_PAIN_UNAVAILABLE", 0.0
            
        strikes = sorted(options_chain_df['strike_price'].unique())
        min_pain = float('inf')
        max_pain_strike = spot_price
        
        for potential_expiry_strike in strikes:
            total_pain = 0
            
            # For each strike, sum the intrinsic value of all open options if it expires here
            for _, row in options_chain_df.iterrows():
                strike = row['strike_price']
                call_oi = row.get('call_oi', 0)
                put_oi = row.get('put_oi', 0)
                
                # Call intrinsic value
                if potential_expiry_strike > strike:
                    total_pain += (potential_expiry_strike - strike) * call_oi
                
                # Put intrinsic value
                if potential_expiry_strike < strike:
                    total_pain += (strike - potential_expiry_strike) * put_oi
                    
            if total_pain < min_pain:
                min_pain = total_pain
                max_pain_strike = potential_expiry_strike
                
        distance_pct = ((max_pain_strike - spot_price) / spot_price) * 100 if spot_price > 0 else 0.0
        return max_pain_strike, distance_pct

    @staticmethod
    def calculate_black_scholes_iv(option_price, S, K, T, r=0.07, is_call=True):
        """
        Newton-Raphson method to calculate Implied Volatility.
        S: Spot Price
        K: Strike Price
        T: Time to Expiry (in years)
        r: Risk-free rate (default 7% for India)
        """
        if option_price <= 0 or S <= 0 or K <= 0:
            return None
            
        MAX_ITERATIONS = 100
        PRECISION = 1.0e-5
        
        # Initial guess
        sigma = 0.5
        
        # Prevent division by zero if expiry is today
        if T <= 0:
            T = 1.0 / 365.0
            
        for _ in range(MAX_ITERATIONS):
            d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
            d2 = d1 - sigma * np.sqrt(T)
            
            if is_call:
                price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
            else:
                price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
                
            vega = S * norm.pdf(d1) * np.sqrt(T)
            
            diff = option_price - price
            if abs(diff) < PRECISION:
                return sigma * 100 # Return as percentage
                
            if vega < 1e-6:
                # Flat vega, numerical instability
                break
                
            sigma = sigma + diff / vega
            
        return sigma * 100
