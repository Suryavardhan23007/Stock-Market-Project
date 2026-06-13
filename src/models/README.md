# Machine Learning Ensemble Forecasting Engine

This directory contains the time series and tabular modeling pipelines. It combines multiple model predictions to deliver probabilistic multi-horizon forecasting.

## Models

1. **XGBoost (`xgboost_model.py`)**:
   * Highly efficient on tabular features: technical indicators, macroeconomic indicators, and options metrics.
2. **Temporal Fusion Transformer (TFT) (`tft_model.py`)**:
   * Learns complex temporal interactions across multi-timeframe inputs.
3. **PatchTST (`patchtst_model.py`)**:
   * Learns deep representation from patches of time series candles, providing state-of-the-art multi-horizon forecasting.

## Combined Prediction

- `ensemble.py`: Merges outputs from the three models using historical error weights. Rather than predicting exact point values, it calculates directional probabilities (e.g., 74% Up) and price ranges.
