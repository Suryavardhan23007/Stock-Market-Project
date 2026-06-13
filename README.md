# Currently this project is in development stage and is continously being updated in GitHub after every progress
# Sensex & Bank Nifty AI-Powered Market Intelligence & Algorithmic Trading System

This is a production-grade, AI-powered real-time forecasting and algorithmic trading system designed for the Indian stock market (specifically Sensex & Bank Nifty). It operates as an intelligent trading assistant, supporting paper-trading and eventually automated live order execution via the **5paisa Xstream API**.

## System Architecture Overview

The platform uses a modular architecture:
1. **Infrastructure**: Orchestrated via Docker containing PostgreSQL (numerical and metadata storage) and Qdrant (vector storage for news/event embeddings).
2. **Data Processing**: Fetches 1-minute historical OHLCV candles, manages real-time tick streaming via WebSockets, and parses news/macroeconomic events.
3. **News Intelligence**: Aggregates news from authoritative RSS feeds (RBI, Economic Times, SEBI, LiveMint, etc.), processes them using **FinBERT** or Financial Sentence Transformers, and indexes them in **Qdrant** for similarity-based historical context retrieval.
4. **Feature Engineering**: Generates multi-timeframe features (1m, 5m, 15m, 30m, 1h) including key momentum, trend, volatility, and options indicators (IV, PCR, Max Pain).
5. **Ensemble Modeling**: Blends XGBoost (for structured tabular features), Temporal Fusion Transformers (TFT, for temporal relations), and PatchTST (for long sequence forecasting) into multi-horizon probabilistic predictions.
6. **LLM Explainer**: Leverages the Gemini API to analyze market conditions, retrieved historical matches, and explain why the forecasting ensemble is predicting a specific target direction.
7. **Paper-Trading Simulator**: Executes and tracks trades locally to validate models without exposing real funds.
8. **Dashboard UI**: A custom Streamlit-based web interface to monitor active models, forecasts, news events, and execution logs in real-time.

---

## Directory Structure

To keep the project modular, maintainable, and easy to debug, we use the following directory layout:

* **`infrastructure/`**: Docker configs and setups for PostgreSQL and Qdrant database servers.
* **`src/config/`**: Configuration parsing, `.env` file loader, and credentials manager.
* **`src/database/`**: Database connections, schemas, models, and migrations.
* **`src/data/`**: 5paisa historical data downloaders and WebSocket live streamers.
* **`src/intelligence/`**: News collectors (RSS), embedding extractors, vector retrieval, and LLM text generation.
* **`src/features/`**: Technical indicators (TA-Lib / pandas calculations), multi-timeframe candle aggregations, and options chain metrics.
* **`src/models/`**: Predictive pipelines for XGBoost, TFT, and PatchTST.
* **`src/trading/`**: Simulator and execution logic for live-broker order management.
* **`src/dashboard/`**: Streamlit visualization frontend dashboard.

Each folder contains its own self-documenting `README.md` outlining the local setup and execution details.

---

## Getting Started

### Prerequisites
* **macOS (M1/M2/M3)**: Ensure Docker Desktop is installed and running.
* **Python**: Python 3.10+ (recommend creating a virtual environment).

### 1. Database Setup
Spin up the PostgreSQL and Qdrant database servers:
```bash
docker-compose up -d
```

### 2. Python Virtual Environment & Dependencies
Create a virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Environment Variables Configuration
Copy the template configuration and supply your keys:
```bash
cp .env.example .env
```
Update `.env` with:
* **5paisa Credentials**: APP_NAME, USER_KEY, ENCRYPTION_KEY, etc.
* **TOTP Secret Key**: Enable TOTP in your 5paisa portal and paste the secret.
* **Gemini API Key**: For news intelligence summarization.

---

## Phased Development Path

The project is executed in modular milestones:
- **Phase 1**: Database and environment configuration.
- **Phase 2**: Historical data fetcher from 5paisa API.
- **Phase 3**: Live market feed WebSocket connector.
- **Phase 4**: RSS aggregator & news vector database (Qdrant).
- **Phase 5**: Feature generator.
- **Phase 6**: Predictive modeling ensemble.
- **Phase 7**: Streamlit UI and LLM explainer.
- **Phase 8**: Paper-trading engine.
