import pandas as pd
import numpy as np

class OptionsIntelligenceEngine:
    """
    Coordinates the multi-factor analysis of live options data to generate confidence scores and execution recommendations.
    """
    
    def __init__(self):
        # We need historical rolling arrays to calculate Z-scores and percentiles.
        # In production, these should be loaded from the database on startup.
        self.history_pcr = []
        self.history_iv = []
        self.history_vix = []
        self.history_breadth = []
        self.history_sector = []
        self.MAX_HISTORY = 30 * 375 # roughly 30 trading days of 1-minute ticks

    def update_history(self, pcr, iv, vix, breadth, sector):
        self.history_pcr.append(pcr)
        self.history_iv.append(iv)
        self.history_vix.append(vix)
        self.history_breadth.append(breadth)
        self.history_sector.append(sector)
        
        # Enforce history limit
        self.history_pcr = self.history_pcr[-self.MAX_HISTORY:]
        self.history_iv = self.history_iv[-self.MAX_HISTORY:]
        self.history_vix = self.history_vix[-self.MAX_HISTORY:]
        self.history_breadth = self.history_breadth[-self.MAX_HISTORY:]
        self.history_sector = self.history_sector[-self.MAX_HISTORY:]

    def _calculate_zscore(self, current_val, history_list):
        if len(history_list) < 100:  # Need minimum warmup
            return 0.0
        mean = np.mean(history_list)
        std = np.std(history_list)
        if std == 0:
            return 0.0
        return (current_val - mean) / std

    def _calculate_percentile(self, current_val, history_list):
        if len(history_list) < 100:
            return 50.0
        # How many historical values are less than the current value
        less_than = sum(1 for x in history_list if x < current_val)
        return (less_than / len(history_list)) * 100.0

    def generate_statistical_context(self, current_pcr, current_iv, current_vix):
        """
        Calculates percentiles and Z-scores using historical state.
        """
        return {
            "pcr_zscore": self._calculate_zscore(current_pcr, self.history_pcr),
            "pcr_percentile": self._calculate_percentile(current_pcr, self.history_pcr),
            "atm_iv_percentile": self._calculate_percentile(current_iv, self.history_iv),
            "vix_percentile": self._calculate_percentile(current_vix, self.history_vix)
        }

    def extract_top_concentration_walls(self, options_chain_df):
        """
        Extracts top 5 Call and Put walls, ignoring illiquid strikes.
        Expects df with: strike_price, call_oi, put_oi, liquidity_score
        """
        # Filter illiquid
        if 'liquidity_score' in options_chain_df.columns:
            # Drop bottom 10% of liquidity
            threshold = options_chain_df['liquidity_score'].quantile(0.1)
            df_liquid = options_chain_df[options_chain_df['liquidity_score'] >= threshold].copy()
        else:
            df_liquid = options_chain_df.copy()
            
        total_call_oi = df_liquid['call_oi'].sum()
        total_put_oi = df_liquid['put_oi'].sum()
        
        if total_call_oi <= 0 and total_put_oi <= 0:
            return "NO_VALID_CONCENTRATION"
            
        # Sort and get top 5
        top_calls = df_liquid.nlargest(5, 'call_oi')
        top_puts = df_liquid.nlargest(5, 'put_oi')
        
        call_walls = []
        put_walls = []
        
        for _, row in top_calls.iterrows():
            contribution = (row['call_oi'] / total_call_oi) * 100 if total_call_oi > 0 else 0
            call_walls.append({"strike": row['strike_price'], "oi": row['call_oi'], "pct": contribution})
            
        for _, row in top_puts.iterrows():
            contribution = (row['put_oi'] / total_put_oi) * 100 if total_put_oi > 0 else 0
            put_walls.append({"strike": row['strike_price'], "oi": row['put_oi'], "pct": contribution})
            
        return {"top_5_calls": call_walls, "top_5_puts": put_walls}

    def determine_regime(self, index_structure_15m, iv_percentile, vix_percentile, spot_price, top_call_wall, top_put_wall):
        """
        Simplified logic for regime classification.
        """
        if iv_percentile > 80 and vix_percentile > 80:
            return "VOLATILITY_EXPANSION"
        if iv_percentile < 20 and vix_percentile < 20:
            return "VOLATILITY_COMPRESSION"
            
        if index_structure_15m in ["BULLISH_BUILDUP", "SHORT_COVERING_RALLY"]:
            return "TRENDING_BULL"
        elif index_structure_15m in ["BEARISH_BUILDUP", "LONG_UNWINDING_SELLING"]:
            return "TRENDING_BEAR"
            
        # Check range-bound condition
        if top_call_wall and top_put_wall:
            if spot_price < top_call_wall[0]['strike'] and spot_price > top_put_wall[0]['strike']:
                return "RANGE_BOUND"
                
        return "NEUTRAL"

    def compute_convergence_confidence(self, pcr_zscore, regime, ml_prediction, is_market_closed=False, is_insufficient_data=False):
        """
        Calculates the logarithmic convergence confidence (0-100).
        """
        if is_market_closed or is_insufficient_data or regime == "NO_SIGNAL":
            return 0.0
            
        # Base penalties for divergence
        if ml_prediction == "UP" and regime == "TRENDING_BEAR":
            return 20.0
        if ml_prediction == "DOWN" and regime == "TRENDING_BULL":
            return 20.0
            
        # If aligned, scale based on Z-score
        base_score = 60.0
        
        # Logarithmic scaling of z-score magnitude (capped at 40 points)
        magnitude = abs(pcr_zscore)
        if magnitude > 0:
            bonus = min(40.0, np.log(1 + magnitude) * 15.0)
            base_score += bonus
            
        return min(100.0, base_score)

    def generate_execution_recommendation(self, final_confidence, regime, is_market_closed=False, is_insufficient_data=False):
        if is_market_closed:
            return "MARKET_CLOSED"
        if is_insufficient_data:
            return "INSUFFICIENT_DATA"
        if regime == "NO_SIGNAL":
            return "NO_TRADE"
            
        if regime == "RANGE_BOUND":
            return "RANGE_BOUND" # Signal for ML to adjust target
        if final_confidence >= 80:
            return "APPROVE"
        elif final_confidence >= 50:
            return "REDUCE_SIZE"
        else:
            return "REJECT"
