import pandas as pd
import numpy as np

def calculate_pcr(calls_oi: int, puts_oi: int) -> float:
    """Calculates Put-Call Ratio (PCR)."""
    if calls_oi == 0:
        return 1.0
    return float(puts_oi) / float(calls_oi)

def calculate_max_pain(options_df: pd.DataFrame) -> float:
    """
    Calculates Max Pain strike price.
    options_df columns expected: ['strike_price', 'option_type', 'open_interest']
    """
    if options_df is None or options_df.empty:
        return 0.0

    strikes = options_df["strike_price"].unique()
    min_pain = float('inf')
    max_pain_strike = 0.0

    for strike in strikes:
        total_pain = 0.0
        for _, row in options_df.iterrows():
            strike_p = row["strike_price"]
            oi = row["open_interest"]
            op_type = row["option_type"].upper()
            
            if op_type == "CE" or op_type == "CALL":
                # Pain for call writers: if spot > strike, writers pay (spot - strike)
                if strike > strike_p:
                    total_pain += (strike - strike_p) * oi
            elif op_type == "PE" or op_type == "PUT":
                # Pain for put writers: if spot < strike, writers pay (strike - spot)
                if strike < strike_p:
                    total_pain += (strike_p - strike) * oi
                    
        if total_pain < min_pain:
            min_pain = total_pain
            max_pain_strike = strike

    return float(max_pain_strike)

def calculate_iv_rank(current_iv: float, historical_ivs: list[float]) -> float:
    """Calculates Implied Volatility (IV) Rank."""
    if not historical_ivs:
        return 50.0
    
    min_iv = min(historical_ivs)
    max_iv = max(historical_ivs)
    
    if max_iv == min_iv:
        return 50.0
        
    iv_rank = ((current_iv - min_iv) / (max_iv - min_iv)) * 100.0
    return iv_rank

def generate_mock_options_features(spot_price: float) -> dict:
    """
    Generates standard options features based on current spot price
    to serve as high-quality defaults when option chain feeds are offline.
    """
    # Simulate realistic ranges around spot
    pcr = 0.8 + 0.4 * np.random.rand()  # PCR between 0.8 and 1.2
    max_pain = round(spot_price / 100) * 100  # Closest round strike
    iv = 12.0 + 8.0 * np.random.rand()  # IV between 12% and 20%
    iv_rank = 30.0 + 40.0 * np.random.rand() # IV Rank between 30 and 70
    
    return {
        "pcr": pcr,
        "max_pain": max_pain,
        "implied_volatility": iv,
        "iv_rank": iv_rank
    }

if __name__ == "__main__":
    # Test calculations
    data = pd.DataFrame([
        {"strike_price": 50000, "option_type": "CE", "open_interest": 500},
        {"strike_price": 50100, "option_type": "CE", "open_interest": 1000},
        {"strike_price": 50200, "option_type": "CE", "open_interest": 1500},
        {"strike_price": 50000, "option_type": "PE", "open_interest": 1200},
        {"strike_price": 50100, "option_type": "PE", "open_interest": 800},
        {"strike_price": 50200, "option_type": "PE", "open_interest": 400},
    ])
    
    mp = calculate_max_pain(data)
    print("Calculated Max Pain strike:", mp)
    print("Mock Options Features for spot 55250:", generate_mock_options_features(55250))
