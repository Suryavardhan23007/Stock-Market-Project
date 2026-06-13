import pandas as pd
import numpy as np

def calculate_sma(df: pd.DataFrame, period: int, column: str = "close") -> pd.Series:
    """Calculates Simple Moving Average (SMA)."""
    return df[column].rolling(window=period).mean()

def calculate_ema(df: pd.DataFrame, period: int, column: str = "close") -> pd.Series:
    """Calculates Exponential Moving Average (EMA)."""
    return df[column].ewm(span=period, adjust=False).mean()

def calculate_rsi(df: pd.DataFrame, period: int = 14, column: str = "close") -> pd.Series:
    """Calculates Relative Strength Index (RSI)."""
    delta = df[column].diff()
    gain = delta.copy()
    loss = delta.copy()
    gain[gain < 0] = 0
    loss[loss > 0] = 0
    
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.abs().rolling(window=period).mean()
    
    # Wilders smoothing fallback/simplification
    for i in range(period, len(df)):
        if i == period:
            continue
        avg_gain.iloc[i] = (avg_gain.iloc[i-1] * (period - 1) + gain.iloc[i]) / period
        avg_loss.iloc[i] = (avg_loss.iloc[i-1] * (period - 1) + abs(loss.iloc[i])) / period
        
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50.0)

def calculate_macd(df: pd.DataFrame, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9, column: str = "close") -> tuple[pd.Series, pd.Series, pd.Series]:
    """Calculates Moving Average Convergence Divergence (MACD)."""
    fast_ema = calculate_ema(df, fast_period, column)
    slow_ema = calculate_ema(df, slow_period, column)
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def calculate_stochastic(df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> tuple[pd.Series, pd.Series]:
    """Calculates Stochastic Oscillator (%K and %D)."""
    low_min = df["low"].rolling(window=k_period).min()
    high_max = df["high"].rolling(window=k_period).max()
    
    k_line = 100 * ((df["close"] - low_min) / (high_max - low_min))
    d_line = k_line.rolling(window=d_period).mean()
    return k_line.fillna(50.0), d_line.fillna(50.0)

def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, num_std: float = 2.0, column: str = "close") -> tuple[pd.Series, pd.Series, pd.Series]:
    """Calculates Bollinger Bands (Middle, Upper, Lower)."""
    middle_band = calculate_sma(df, period, column)
    std_dev = df[column].rolling(window=period).std()
    upper_band = middle_band + (num_std * std_dev)
    lower_band = middle_band - (num_std * std_dev)
    return middle_band, upper_band, lower_band

def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculates Average True Range (ATR)."""
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    atr = true_range.rolling(window=period).mean()
    return atr.fillna(0.0)

def calculate_vwap(df: pd.DataFrame) -> pd.Series:
    """Calculates Volume Weighted Average Price (VWAP)."""
    typical_price = (df["high"] + df["low"] + df["close"]) / 3.0
    price_volume = typical_price * df["volume"]
    
    # Cumulative sums
    cum_pv = price_volume.cumsum()
    cum_volume = df["volume"].cumsum()
    
    vwap = cum_pv / cum_volume
    return vwap.fillna(df["close"])

def generate_all_features(df: pd.DataFrame) -> pd.DataFrame:
    """Computes all technical indicator features on a candle DataFrame."""
    out = df.copy()
    
    # Sort by datetime to ensure calculations run in sequence
    if "timestamp" in out.columns:
        out = out.sort_values("timestamp").reset_index(drop=True)
    elif "Datetime" in out.columns:
        out = out.sort_values("Datetime").reset_index(drop=True)
        
    # SMAs and EMAs
    out["sma_20"] = calculate_sma(out, 20)
    out["ema_9"] = calculate_ema(out, 9)
    out["ema_20"] = calculate_ema(out, 20)
    out["ema_50"] = calculate_ema(out, 50)
    out["ema_200"] = calculate_ema(out, 200)
    
    # Momentum
    out["rsi_14"] = calculate_rsi(out, 14)
    macd, signal, hist = calculate_macd(out)
    out["macd_line"] = macd
    out["macd_signal"] = signal
    out["macd_hist"] = hist
    
    k_stoch, d_stoch = calculate_stochastic(out)
    out["stoch_k"] = k_stoch
    out["stoch_d"] = d_stoch
    
    # Volatility
    mid_bb, upper_bb, lower_bb = calculate_bollinger_bands(out)
    out["bb_mid"] = mid_bb
    out["bb_upper"] = upper_bb
    out["bb_lower"] = lower_bb
    out["atr_14"] = calculate_atr(out, 14)
    
    # Institutional
    out["vwap"] = calculate_vwap(out)
    
    return out

if __name__ == "__main__":
    # Test indicators calculation
    np.random.seed(42)
    dates = pd.date_range("2026-06-01", periods=100, freq="min")
    close = 50000 + np.random.randn(100).cumsum() * 50
    high = close + np.random.rand(100) * 10
    low = close - np.random.rand(100) * 10
    open_p = close + np.random.randn(100) * 5
    volume = np.random.randint(100, 1000, size=100)
    
    test_df = pd.DataFrame({
        "timestamp": dates,
        "open": open_p,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume
    })
    
    features_df = generate_all_features(test_df)
    print("Columns in computed features DataFrame:")
    print(list(features_df.columns))
    print("\nFirst row of computed features:")
    print(features_df.iloc[50])
