# Database Infrastructure

This directory contains the Docker configuration for spinning up the persistent storage backends for the AI trading assistant.

## Services Included

1. **PostgreSQL (Port 5432)**:
   * Used for storing numeric structured data: historical OHLCV candles, real-time tick logs, paper-trading ledger, and metadata.
   * Persistence volume: `postgres_data`

2. **Qdrant (Port 6333 / 6334)**:
   * High-performance vector database used for storing financial news embeddings (generated via FinBERT) and retrieving similar historical events.
   * Persistence volume: `qdrant_data`

## Getting Started

### Start Databases
To start both database containers in detached mode:
```bash
docker compose up -d
```

### Stop Databases
To spin down containers without losing data:
```bash
docker compose down
```

### Reset Data
To wipe volumes and start from scratch:
```bash
docker compose down -v
```
