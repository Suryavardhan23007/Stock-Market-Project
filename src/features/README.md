# Feature Engineering & Indicator Generation

This module is responsible for calculating technical indicators, processing options market metrics, and compiling input vectors for the ensemble models.

## Components

- `indicators.py`: Implementation of standard technical indicators:
  * **Trend**: EMA (9, 20, 50, 200), SMA.
  * **Momentum**: RSI, MACD, Stochastic Oscillator.
  * **Volatility**: Bollinger Bands, Average True Range (ATR).
  * **Institutional**: Volume Weighted Average Price (VWAP).
- `options_chain.py`: Extracts PCR (Put-Call Ratio), Open Interest (OI) changes, Implied Volatility (IV) ranks, and Max Pain from option chain raw data.
- `aggregator.py`: Resamples 1-minute OHLCV candles into higher timeframes (5m, 15m, 30m, 1h) and aggregates indicators.
