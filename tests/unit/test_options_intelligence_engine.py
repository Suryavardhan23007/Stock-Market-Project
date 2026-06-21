import pytest
import pandas as pd
from src.analytics.options_intelligence_engine import OptionsIntelligenceEngine

def test_extract_top_concentration_walls():
    engine = OptionsIntelligenceEngine()
    
    # Valid
    df = pd.DataFrame([
        {'strike_price': 100, 'call_oi': 1000, 'put_oi': 100},
        {'strike_price': 110, 'call_oi': 500, 'put_oi': 500},
        {'strike_price': 120, 'call_oi': 100, 'put_oi': 1000}
    ])
    walls = engine.extract_top_concentration_walls(df)
    assert len(walls['top_5_calls']) == 3
    assert len(walls['top_5_puts']) == 3
    assert walls['top_5_calls'][0]['strike'] == 100
    assert walls['top_5_puts'][0]['strike'] == 120
    
    # Invalid / Zero OI
    df_zero = pd.DataFrame([
        {'strike_price': 100, 'call_oi': 0, 'put_oi': 0},
        {'strike_price': 110, 'call_oi': 0, 'put_oi': 0}
    ])
    walls_zero = engine.extract_top_concentration_walls(df_zero)
    assert walls_zero == "NO_VALID_CONCENTRATION"

def test_compute_convergence_confidence():
    engine = OptionsIntelligenceEngine()
    
    # Normal alignment
    score = engine.compute_convergence_confidence(pcr_zscore=1.5, regime="TRENDING_BULL", ml_prediction="UP")
    assert score > 60.0
    
    # Market Closed
    score_closed = engine.compute_convergence_confidence(pcr_zscore=1.5, regime="TRENDING_BULL", ml_prediction="UP", is_market_closed=True)
    assert score_closed == 0.0

def test_generate_execution_recommendation():
    engine = OptionsIntelligenceEngine()
    
    assert engine.generate_execution_recommendation(90, "TRENDING_BULL") == "APPROVE"
    assert engine.generate_execution_recommendation(60, "TRENDING_BULL") == "REDUCE_SIZE"
    assert engine.generate_execution_recommendation(40, "TRENDING_BULL") == "REJECT"
    assert engine.generate_execution_recommendation(90, "RANGE_BOUND") == "RANGE_BOUND"
    
    # Edge Cases
    assert engine.generate_execution_recommendation(90, "TRENDING_BULL", is_market_closed=True) == "MARKET_CLOSED"
    assert engine.generate_execution_recommendation(90, "TRENDING_BULL", is_insufficient_data=True) == "INSUFFICIENT_DATA"
    assert engine.generate_execution_recommendation(90, "NO_SIGNAL") == "NO_TRADE"
