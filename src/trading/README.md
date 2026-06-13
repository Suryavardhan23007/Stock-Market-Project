# Paper Trading & Broker Execution Module

This module simulates real execution and forwards real orders to 5paisa Xstream.

## Components

- `execution_engine.py`: Base class coordinating entry and exit logic, order validation, and trade accounting.
- `paper_simulator.py`: Manages mock portfolios, logs executions to PostgreSQL `paper_trades`, and computes cumulative metrics (win rate, Sharpe ratio, drawdown).
- `broker_client.py`: Translates simulated trades into live orders via 5paisa REST endpoints when live execution is enabled.

## Strategy Logic

The signals derived from the forecasting ensemble (XGBoost, TFT, PatchTST) trigger actions:
- **Direction = UP** & high confidence: Execute BUY on simulated long options/futures.
- **Direction = DOWN** & high confidence: Execute SELL / buy puts.
- **Risk management**: Automatic stop-loss and trailing take-profit are checked every minute.
