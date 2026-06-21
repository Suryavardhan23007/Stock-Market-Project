import pytest
import pandas as pd
from src.analytics.oi_calculator import OICalculator

def test_classify_strike_buildup():
    assert OICalculator.classify_strike_buildup(1.5, 500) == "LONG_BUILDUP"
    assert OICalculator.classify_strike_buildup(-1.5, 500) == "SHORT_BUILDUP"
    assert OICalculator.classify_strike_buildup(1.5, -500) == "SHORT_COVERING"
    assert OICalculator.classify_strike_buildup(-1.5, -500) == "LONG_UNWINDING"
    assert OICalculator.classify_strike_buildup(0, 0) == "NEUTRAL"

def test_classify_index_buildup():
    assert OICalculator.classify_index_buildup(100, -1000, 2000) == "SHORT_COVERING_RALLY"
    assert OICalculator.classify_index_buildup(-100, 2000, -1000) == "LONG_UNWINDING_SELLING"
    assert OICalculator.classify_index_buildup(100, 1000, 2000) == "BULLISH_BUILDUP"
    assert OICalculator.classify_index_buildup(-100, 1000, 2000) == "BEARISH_BUILDUP"
    assert OICalculator.classify_index_buildup(0, 0, 0) == "MIXED"

def test_calculate_max_pain():
    # Test valid data
    df = pd.DataFrame([
        {'strike_price': 100, 'call_oi': 1000, 'put_oi': 100},
        {'strike_price': 110, 'call_oi': 500, 'put_oi': 500},
        {'strike_price': 120, 'call_oi': 100, 'put_oi': 1000}
    ])
    spot = 110
    max_pain, dist_pct = OICalculator.calculate_max_pain(df, spot)
    assert max_pain == 110
    assert dist_pct == 0.0
    
    # Test zero OI (Market Closed or Invalid Chain)
    df_zero = pd.DataFrame([
        {'strike_price': 100, 'call_oi': 0, 'put_oi': 0},
        {'strike_price': 110, 'call_oi': 0, 'put_oi': 0}
    ])
    max_pain_z, dist_pct_z = OICalculator.calculate_max_pain(df_zero, spot)
    assert max_pain_z == "MAX_PAIN_UNAVAILABLE"
    assert dist_pct_z == 0.0

def test_calculate_black_scholes_iv():
    # Valid
    iv = OICalculator.calculate_black_scholes_iv(option_price=5.0, S=100.0, K=100.0, T=30/365.0, r=0.07, is_call=True)
    assert iv is not None
    assert iv > 0
    
    # Invalid (Premium 0)
    iv_zero_prem = OICalculator.calculate_black_scholes_iv(option_price=0.0, S=100.0, K=100.0, T=30/365.0)
    assert iv_zero_prem is None
    
    # Invalid (Spot 0) - Divide by zero check
    iv_zero_spot = OICalculator.calculate_black_scholes_iv(option_price=5.0, S=0.0, K=100.0, T=30/365.0)
    assert iv_zero_spot is None
